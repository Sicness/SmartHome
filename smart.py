#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import sys
import subprocess
import socket
from threading import Thread
import threading
from time import sleep
import datetime
from datetime import datetime, timedelta
from select import select
import signal
import urllib2

import mplayer
from sound import *
import feedparser   # for weather parser

from cosm import Cosm
import cosm_config
from log import log
from log import err
import arduino
import objects
import ds18s20


glob = objects.Vars()
glob.set('terminate', False)
glob.set('threads', list())
hole_motion = objects.MotionSensor()
room_motion = objects.MotionSensor()
IR_codes = dict()                   # Binded funcitions on IR codes
repeatable_IR = {b'FFE01F', b'FFA857'}          # This IR codes can be repeated
last_IR = ''                        # Last IR received code
ultra = Ultra()
cron = objects.Crontab(glob = glob)
cosm = Cosm(cosm_config.FEED_ID, cosm_config.API_KEY)
alice = Alice(glob = glob)
hole_night_light = objects.gpioLight(11, mode = objects.LIGHT_MODE_AUTO)
hole_light = objects.nooLite(0)     # USB NooLite on channale 0


def signal_handler(signal, frame):
    log('Time to terminate. Exit')
    print('Time to terminate. Setting the terminate flag\n')
    print("Active threads: ",threading.active_count())
    glob.set('terminate', True)
    for i in xrange(10):
        print("Active threads: ",threading.active_count(),
              ". Wait more %d seconds" % (10 - i))
        if threading.active_count() == 1:
            break
        sleep(1)
    print "Bye!"
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def init_IR_codes():
    """ Bind functions on IR codes """
    IR_codes.update( {b'FF629D' : say_temp} )     # Say temperature status
    IR_codes.update( {b'FFA857' : volume_inc} )   # increase volume
    IR_codes.update( {b'FFE01F' : volume_dec} )   # reduce volume
    IR_codes.update( {b'FF906F' : toSecureMode} )       # Will be noBodyHome
    IR_codes.update( {b'FFC23D' : ultra.switch} )       # On/off radio
    IR_codes.update( {b'BF09C35C' : ultra.switch} )     # On/off radio (big)
    IR_codes.update( {b'8BE68656' : holeNightLightAuto} )
    IR_codes.update( {b'B21F28AE' : hole_night_light.setManualStateOff} )
    IR_codes.update( {b'A6B1096A' : hole_night_light.setManualStateOn} )
    IR_codes.update( {b'24014B0' : holeLightAuto} )
    IR_codes.update( {b'8FC212DB' : hole_light.setManualStateOff} )
    IR_codes.update( {b'7960556F' : hole_light.setManualStateOn} )
    IR_codes.update( {b'FF10EF' : holeNightLightAuto} )
    IR_codes.update( {b'FF38C7' : hole_night_light.setManualStateOff} )
    IR_codes.update( {b'FF5AA5' : hole_night_light.setManualStateOn} )
    IR_codes.update( {b'FF30CF' : holeLightAuto} )
    IR_codes.update( {b'FF18E7' : hole_light.setManualStateOff} )
    IR_codes.update( {b'FF7A85' : hole_light.setManualStateOn} )

def cosm_send(id, value):
    '''Send data to Cosm.com'''
    try:
        cosm.put_data_point(id, value)
    except urllib2.HTTPError as e:
        err("Cosm: " + str(e))
    except urllib2.URLError as e:
        err("Cosm: " + str(e))
def volume_dec(value = 200):
    """ Reduce system volume """
    subprocess.Popen("amixer set PCM %d-" % (value), shell = True)

def volume_inc(value = 200):
    """ Increase system volume """
    subprocess.Popen("amixer set PCM %d+" % (value), shell = True)

def getWeather():
    cron.replace('getWeather', datetime.now() + timedelta(minutes=30), getWeather)
    try:
        d=feedparser.parse('http://weather.yahooapis.com/forecastrss?w=2123272&u=c')
    except:
        raise
    res = dict()
    res.update({'t' : int(d['items'][0]['yweather_condition']['temp'])})
    res.update({'chill' : int(d['feed']['yweather_wind']['chill'])})
    res.update({'wind_speed' : round(float(d['feed']['yweather_wind']['speed']) / 3.6, 1)})
    res.update({'sunset' : d['feed']['yweather_astronomy']['sunset']})
    res.update({'sunrise' : d['feed']['yweather_astronomy']['sunrise']})
    glob.set('weather', res)

def say_temp():
    """ Report temperatures state """
    print glob.get('weather')
    alice.say('Температура на улице ' + str(glob.get('weather')['t']))
    if glob.get('weather')['t'] != glob.get('weather')['chill']:
        alice.say('Температура комфорта' + str(glob.get('weather')['chill']))
    alice.say('Скорость ветра' + str(glob.get('weather')['wind_speed']))
    alice.say("Температура дома " + str(glob.get('T')).replace('.',','))

def get_T():
    """ loop for geting temperature form ds18s20 """
    ds = ds18s20.ds18b20('/sys/bus/w1/devices/10-0008025b6d03/w1_slave')
    while True:
        try:
            T=ds.read_c()
        except:
            print("ERROR: can't read from ds18s20")
            sleep(10)
            continue
        print('T='+str(T))
        if T != glob.get('T'):
            glob.set( 'T', T)
            cosm_send('Hole_temp_DC', T)
        sleep(5)
        if glob.get('terminate'):
            print("ds18s20: flound terminate flag. Exit.")
            return

def onHoleMotion():
    log('Motion in hole')
    hole_light.setAutoState(1)
    if alice.isNight():
        # turn on night light
        hole_night_light.setAutoState(1)
    if glob.get('noBodyHome') == 1:
        glob.set('noBodyHome', 0)
        alice.say('Добро пожаловать домой')
        alice.say('Текущее время ' + alice.now())
        say_temp()
        alice.say("Последний раз дома кто-то был " + alice.now(glob.get('lastMotion')))

def onHoleMotionOff():
    hole_light.setAutoState(0)
    hole_night_light.setAutoState(0)
    glob.set('lastMotion',datetime.now())
    cron.replace('noBodyHome', datetime.now() + timedelta(hours=3), noBodyHome)

def noBodyHome():
    """ Called by cron when no motion 3 hours"""
    alice.say('Кажется ниКого нет дома')
    glob.set('noBodyHome',1)

def toSecureMode():
    """ User function. Called when all gonna leave home """
    alice.say('Сторожевой режим будет включен через одну минуту. Приятного время препровождения!')
    cron.add('toSecureMode', datetime.now() + timedelta(minutes = 1), noBodyHome)

def holeNightLightAuto():
    alice.say("Ночное освещение в холе переведен автоматический режим")
    hole_night_light.setMode(objects.LIGHT_MODE_AUTO)

def holeLightAuto():
    alice.say("Свет в холе переведен автоматический режим")
    hole_light.setMode(objects.LIGHT_MODE_AUTO)

def onArduinoFound():
    alice.say("Связь с Ардуино установлена!")

def onArduinoLost():
    alice.say("Утеряна связь с Ардуино! Пытаюсь восстановить связь...")


####################################################
#####            main dispatchs               ######
####################################################

def dispatch(line):
    """ Parse serial from Arduino """
    global last_IR
    if line[:5] == b'Temp=':
        T = float(line.split(b'=')[1])
        if T != glob.get('Hole_temp'):
            glob.set( 'hole_temp', T)
            cosm_send('Hole_temp', T)

    elif line[:9] == b'Pressure=':
        pressure = float(line.split(b'=')[1])
        if pressure != glob.get('hole_pressure'):
            glob.set( 'hole_pressure', pressure)
            cosm_send('Hole_pressure', pressure)
    #Motion in room YES
    elif line[:10] == b'Motion in ':
        t = line.split(' ')
        if t[2] == b'hole':
            if t[3] == b'YES':
                hole_motion.update(1)
            else:
                hole_motion.update(0)
        if t[2] == b'room':
            if t[3] == b'YES':
                room_motion.update(1)
            else:
                room_motion.update(0)
        if t[3] == b'NO':
            glob.set('lastMotion',datetime.now())


    # cheack if it's 'repeat' IR code and this code repeatable
    elif (line == b'FFFFFFFF') and ( last_IR in repeatable_IR):
        line = last_IR      # restore repeated code

    # Check if line in IR code
    elif line in IR_codes:
        IR_codes[line]()    # run fuction, binded on this IR code
        last_IR = line      # remember code for 'repeat' case

def sock_dispatch(s):
    data = s.recv(1024)
    print('sock| ', data)

    if data == b'radio':
        ultra.switch()
    s.sendall(b'OK')
    s.close()

def sock_listen():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind(("0.0.0.0", 10000))
    srv.listen(1)
    input = [srv]
    while True:
        inputready,outputready,exceptready = select(input,[],[],2)

        # timeout on select
        if not inputready:
            if glob.get('terminate'):
                print 'sock_listen: flag terminate found. Exit'
                return

        for s in inputready:
            if s == srv:
                s, addr = srv.accept()
                print('Connection from', addr)
                sock_disp_thr = Thread(target = sock_dispatch, args = (s,))
                sock_disp_thr.start()

def arduino_listen():
    while True:
        if glob.get('terminate'):
            print 'arduino_listen: found terminate flag. Exit'
            return

        line = ard.read()       # read line from arduino
        if line == '':          # if serial timeout is reached
            continue
        print(line)
        dispatch(line)

if __name__ == '__main__':
    #log('Smart home started')
    getWeather()
#####     Objects configuration      ######
    ard = arduino.Arduino('/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A80090sP-if00-port0',
                          onFound = onArduinoFound, onLost = onArduinoLost)
    hole_motion.onOn = onHoleMotion
    hole_motion.onOff = onHoleMotionOff
    init_IR_codes()             # init dict: { IR_CODE : function }
    ### Threads creating ###
    sock_thr = Thread(target = sock_listen, args = (), name = "sock_thr")
    sock_thr.start()
    glob.get('threads').append(sock_thr)
    ard_thr = Thread(target = arduino_listen, args = (), name = "ard_thr")
    ard_thr.start()
    glob.get('threads').append(ard_thr)
    ds = Thread(target = get_T, args = (), name = "ds")
    ds.start()                  # ds18s20 temerature sensor
    glob.get('threads').append(ds)

    #####     main loop     #####
    while True:
        for th in glob.get('threads'):
            if th.isAlive() == False:
                print "WARNING: Thread with name %s is DEAD!" % (th.getName())
                print "  Resurrecting..."
                th.start()
        sleep(3)
        # Here should be check of threads
