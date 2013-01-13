# -*- coding: UTF-8 -*-

import serial, os
import subprocess

s = serial.Serial('/dev/ttyUSB0',9600)
repeatable_IR = {b'FFE01F', b'FFA857'}
last_IR = ''
T = 0
ultra = None

def read():
	return s.readline()[:-2]

def volume_dec(value = 200):
	subprocess.Popen("amixer set PCM %d-" % (value), shell = True)	
def volume_inc(value = 200):
	subprocess.Popen("amixer set PCM %d+" % (value), shell = True)	

def say(text):
	cmd = "wget -q -U Mozilla -O /tmp/say.mp3 \"http://translate.google.com/translate_tts?ie=UTF-8&tl=ru&q=%s\" && mpg123 /tmp/say.mp3" % (text)
	subprocess.Popen(cmd, shell = True)	

def radio():
	global ultra
	if ultra  == None:
		ultra = subprocess.Popen("mpg123 http://94.25.53.132:80/ultra-128.mp3", shell = True)	
		return
	else:
		ultra.kill()
		ultra = None

def dispatch(line):
	global T, last_IR
	if (line == b'FFFFFFFF') and ( last_IR in repeatable_IR):
		print('OK')
		line = last_IR
	if line[:2] == b'T=':
		T=float(line.split(b'=')[1])
	elif line[:6] == b'FF629D':
		say("Тепература дома %f" % (T))
	elif line[:6] == b'FFE01F':
		volume_dec()
	elif line[:6] == b'FFA857':
		volume_inc()
	elif line[:6] == b'FF906F':
		radio()

	last_IR = line

while True:
	line = read()
	print(line)
	dispatch(line)
