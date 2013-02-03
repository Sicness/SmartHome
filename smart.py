# -*- coding: UTF-8 -*-

import objects
import arduino, os, sys
import subprocess
import socket
from threading import Thread
import config
import eeml					# for cosm.com
from log import log
from log import err
import time

glob = objects.Vars()
hole_motion = objects.MotionSensor()
IR_codes = dict()					# Binded funcitions on IR codes
repeatable_IR = {b'FFE01F', b'FFA857'}			# This IR codes can be repeated
last_IR = ''						# Last IR received code
ultra = None						# subprocess object for radio player


def init_IR_codes():
	""" Bind functions on IR codes """
	IR_codes.update({b'FF629D' : say_temp})		# Say temperature status
	IR_codes.update({b'FFA857' : volume_inc})	# increase volume
	IR_codes.update({b'FFE01F' : volume_dec})	# reduce volume
	IR_codes.update({b'FF906F' : radio})		# On/off radio

def cosm_send(id, value):
	'''Send data to Cosm.com
	Can't update data yet, so, used recreate class :( '''
	cosm = eeml.Cosm(config.API_URL, config.API_KEY)
	cosm.update([eeml.Data(id, value)])
	try:
		cosm.put()
	except eeml.CosmError as e:
		err('cosm.put(): {}'.format(e))
	except:
		err('Unexpected error at cosm.put(): %s' % sys.exc_info()[0])

def volume_dec(value = 200):
	""" Reduce system volume """
	subprocess.Popen("amixer set PCM %d-" % (value), shell = True)	

def volume_inc(value = 200):
	""" Increase system volume """
	subprocess.Popen("amixer set PCM %d+" % (value), shell = True)	

def say(text):
	""" Text to speech with Google translate """
	cmd = "wget -q -U Mozilla -O /tmp/say.mp3 \"http://translate.google.com/translate_tts?ie=UTF-8&tl=ru&q=%s\" && mpg123 /tmp/say.mp3" % (text)
	subprocess.Popen(cmd, shell = True)	

def say_temp():
	""" Report temperatures state """
	say("Тепература дома %f" % glob.get('T'))

def radio():
	""" On/Off radio """
	global ultra
	if ultra  == None:
		ultra = subprocess.Popen("mpg123 http://94.25.53.132:80/ultra-128.mp3", shell = True)	
		return
	else:
		ultra.kill()
		ultra = None

def onHoleMotion():
	log('Motion in hole')

def onArduinoFound():
	say("Связь с Ардуино установлена!")

def onArduinoLost():
	say("Утеряна связь с Ардуино! Пытаюсь восстановить связь...")


####################################################
#####            main dispatchs               ######
####################################################

def dispatch(line):
	""" Parse serial from Arduino """
	global last_IR
	if line[:2] == b'T=':
		T = float(line.split(b'=')[1])
		if T != glob.get('T'):
			glob.set( 'T', T)
			cosm_send('temp_hole', T)

	elif line == b'hole ON':
		hole_motion.update(1)
	elif line == b'hole YES':
		hole_motion.update(0)


	# cheack if it's 'repeat' IR code and this code repeatable
	elif (line == b'FFFFFFFF') and ( last_IR in repeatable_IR):
		line = last_IR		# restore repeated code

	# Check if line in IR code
	elif line in IR_codes:
		IR_codes[line]()	# run fuction, binded on this IR code
		last_IR = line		# remember code for 'repeat' case

def sock_dispatch(s):
	data = s.recv(1024)
	print('sock| ', data)

	if data == b'radio':
		radio()
	s.sendall(b'OK')
	s.close()

def sock_listen():
	srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	srv.bind(("0.0.0.0", 10000))
	srv.listen(1)
	while True:
					s, addr = srv.accept()
					print('Connection from', addr)
					sock_disp_thr = Thread(target = sock_dispatch, args = (s,))
					sock_disp_thr.start()

if __name__ == '__main__':
	log('Smart home started')

	#####     Objects configuration      ######
	ard = arduino.Arduino('/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A80090sP-if00-port0', onFound = onArduinoFound, onLost = onArduinoLost)
	hole_motion.onOn = onHoleMotion
	init_IR_codes()				# init dict: { IR_CODE : function }
	sock_thr = Thread(target = sock_listen, args = ())
	sock_thr.start()

	#####     main loop     #####
	while True:
		try:
			line = ard.read()			# read line from arduino
		except KeyboardInterrupt:
			log('KeyboardInterrupt received. Exit')
			print('KeyboardInterrupt received. Bye!\n')
			sys.exit(0)
		print(line)
		dispatch(line)
