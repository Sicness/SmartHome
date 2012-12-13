# -*- coding: utf-8 -*-

import serial
from httplib2 import Http
import datetime

urlSmart = "http://smart/"
web = Http()

try:
	s = serial.Serial('/dev/ttyUSB0', 9600)
except:
	s = serial.Serial('/dev/ttyUSB1', 9600)
	
while 1:
	buf = s.readline()
	print datetime.datetime.now(), buf,
	if buf[:6] == "HMSoff" > 0 :
		web.request(urlSmart + "objects/?script=SayHoleLightOff") 
	if buf[:5] == "HMSon" > 0 :
		web.request(urlSmart + "objects/?script=SayHoleLightOn") 
	if buf[:9] == "HMSdetect" > 0 :
		web.request(urlSmart + "objects/?script=SayHoleLightDetect") 
	if buf[:8] == "VoiceOff" > 0 :
		web.request(urlSmart + "objects/?script=SetNoVoice") 
	if buf[:7] == "hole ON" > 0 :
		web.request(urlSmart + "objects/?object=holeMotion&op=m&m=statusChanged&status=1") 
	if buf[:8] == "hole OFF" > 0 :
		web.request(urlSmart + "objects/?object=holeMotion&op=m&m=statusChanged&status=0") 
	if "T=" in buf:
                t = buf[2:].split('.')
		web.request(urlSmart + "objects/?object=holeTemp&op=m&m=update&temp="+t[0]+"&tempDec="+t[1][0]) 

	if "FF629D" in buf[:6]:
		web.request(urlSmart + "objects/?script=sayTemp") 
	if "FF52AD" in buf[:6]:
		web.request(urlSmart + "/objects/?script=toSecurityMode") 
