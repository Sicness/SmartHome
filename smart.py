# -*- coding: UTF-8 -*-

import objects
import serial, os
import subprocess
import config
import eeml					# for cosm.com
from log import log
from log import err

s = serial.Serial('/dev/ttyUSB0',9600)			# Arduino serial 
cosm = eeml.Cosm(config.API_URL, config.API_KEY)
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
	cosm.update([eeml.Data(id, value)])
	try:
		cosm.put()
	except:
		err("Can't send to cosm")

def read():
	""" Read line from Serial with out \r\n """
	return s.readline()[:-2]

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

####################################################
#####        Objects configuration            ######
####################################################

hole_motion.onOn = onHoleMotion

####################################################
#####            main dispatch                ######
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

if __name__ == '__main__':
	log('Smart home started')
	init_IR_codes()				# init dict: { IR_CODE : function }
	while True:
		line = read()
		print(line)
		dispatch(line)
