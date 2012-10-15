# -*- coding: utf-8 -*-

import serial
from httplib2 import Http

urlSmart = "http://smart/"
web = Http()

try:
	s = serial.Serial('/dev/ttyUSB0', 9600)
except:
	s = serial.Serial('/dev/ttyUSB1', 9600)
	
while 1:
	buf = s.readline()
	print buf,
	if buf[:6] == "HMSoff" > 0 :
		web.request(urlSmart + "objects/?script=SayHoleLightOff") 
	if buf[:5] == "HMSon" > 0 :
		web.request(urlSmart + "objects/?script=SayHoleLightOn") 
	if buf[:9] == "HMSdetect" > 0 :
		web.request(urlSmart + "objects/?script=SayHoleLightDetect") 
	if buf[:8] == "VoiceOff" > 0 :
		web.request(urlSmart + "objects/?script=SetNoVoice") 
	if buf[:7] == "VoiceOn" > 0 :
		web.request(urlSmart + "objects/?script=SetVoice") 
