# -*- coding: UTF-8 -*-

import objects
import serial, os
import subprocess

s = serial.Serial('/dev/ttyUSB0',9600)			# Arduino serial 
glob = objects.Vars()
IR_codes = dict()					# Binded funcitions on IR codes
repeatable_IR = {b'FFE01F', b'FFA857'}			# This IR codes can be repeated
last_IR = ''						# Last IR received code
T = 0							# Temperature at home :)
ultra = None						# subprocess object for radio player

def init_IR_codes():
	""" Bind functions on IR codes """
	IR_codes.update({b'FF629D' : say_temp})		# Say temperature status
	IR_codes.update({b'FFA857' : volume_inc})	# increase volume
	IR_codes.update({b'FFE01F' : volume_dec})	# reduce volume
	IR_codes.update({b'FF906F' : radio})		# On/off radio

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
	print(glob.get('T'))
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

def dispatch(line):
	""" Parse serial from Arduino """
	global T, last_IR
	if line[:2] == b'T=':
		glob.set( 'T', float(line.split(b'=')[1]))
		print(glob.exist('T'))

	# cheack if it's 'repeat' IR code and this code repeatable
	elif (line == b'FFFFFFFF') and ( last_IR in repeatable_IR):
		line = last_IR		# restore repeated code
	
	# Check if line in IR code
	elif line in IR_codes:
		IR_codes[line]()	# run fuction, binded on this IR code
		last_IR = line		# remember code for 'repeat' case

if __name__ == '__main__':
	init_IR_codes()				# init dict: { IR_CODE : function }
	while True:
		line = read()
		print(line)
		dispatch(line)
