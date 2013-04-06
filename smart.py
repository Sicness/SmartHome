# -*- coding: UTF-8 -*-

import os
import sys
import subprocess
import socket
from threading import Thread
from time import sleep
import datetime
import urllib
import Queue

import mplayer
from ultra import Ultra

from cosm import Cosm
import cosm_config
from log import log
from log import err
import arduino
import objects
import config
import ds18s20


glob = objects.Vars()
hole_motion = objects.MotionSensor()
IR_codes = dict()                   # Binded funcitions on IR codes
repeatable_IR = {b'FFE01F', b'FFA857'}          # This IR codes can be repeated
last_IR = ''                        # Last IR received code
ultra = Ultra()
cron = objects.Crontab()
cosm = Cosm(cosm_config.FEED_ID, cosm_config.API_KEY)
user_agent = ("Mozilla/5.0 (Windows NT 6.1; WOW64) "
                      "AppleWebKit/537.17 "
                      "(KHTML, like Gecko) Chrome/24.0.1312.60 Safari/537.17")
player = mplayer.Player(args=('-user-agent', user_agent))  #, '-ao', 'pulse'))
player.cmd_predix = ''
say_queue = Queue.Queue()


def init_IR_codes():
    """ Bind functions on IR codes """
    IR_codes.update({b'FF629D' : say_temp})     # Say temperature status
    IR_codes.update({b'FFA857' : volume_inc})   # increase volume
    IR_codes.update({b'FFE01F' : volume_dec})   # reduce volume
    IR_codes.update({b'FF906F' : ultra.switch})        # On/off radio

def cosm_send(id, value):
    '''Send data to Cosm.com'''
    try:
        cosm.put_data_point(id, value)
    except:
        print("ERROR: Can't send to cosm.com")

def volume_dec(value = 200):
    """ Reduce system volume """
    subprocess.Popen("amixer set PCM %d-" % (value), shell = True)

def volume_inc(value = 200):
    """ Increase system volume """
    subprocess.Popen("amixer set PCM %d+" % (value), shell = True)

def _say_queue():
    while True:
        try:
            item = say_queue.get_nowait()
            # item = (text, lang)
        except:
            sleep(0.5)
            continue
        _say(item[0],item[1])
        sleep(0.5)

def say(text, language = "ru"):
    say_queue.put((text, language))
    print "\""+text+"\" puted"

def _say(text, language = "ru"):
    """ Text to speech with Google translate """
    """
    time = datetime.datetime.now().time()
    if time < datetime.time(hour = 8) and time > datetime.time(hour=23, munute=30):
        return
    cmd = "wget -q -U Mozilla -O /tmp/say.mp3 \"http://translate.google.com/translate_tts?ie=UTF-8&tl=ru&q=%s\" && mpg123 /tmp/say.mp3" % (text)
    subprocess.Popen(cmd, shell = True)
    """
    url = url = (u"http://translate.google.com/"
                 u"translate_tts?tl={0}&q={1}".format(
                 language,
                 urllib.quote(text)))
    player.loadfile(url, 1)

def say_temp():
    """ Report temperatures state """
    say("Температура дома " + str(glob.get('T')).replace('.',','))
    say("Атмосферное давление " +
        str(glob.get('hole_pressure')).replace('.',',') +
        " Килопаскаль")

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
        sleep(10)

def onHoleMotion():
    log('Motion in hole')
    return
    if glob.get('noBodyHome') == 1:
        glob.set('noBodyHome', 0)
        say('Добро пожаловать домой')
        say('Текущее время '+datetime.datetime.now().strftime("%H %M"))
        say_temp()
        say("Последний раз дома кто-то был " + glob.get('lastMotion').strftime("%H %M"))


def onHoleMotionOff():
    glob.set('lastMotion',datetime.datetime.now())
    if cron.isExist('noBodyHome'):
        cron.remove('noBodyHome')
    cron.add(objects.Task('noBodyHome', \
                          datetime.datetime.now() + datetime.timedelta(hours=3), noBodyHome))

def noBodyHome():
    """ Called by cron when no motion 3 hours"""
    say('Кажется никого нет дома')
    glob.set('noBodyHome',1)

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

    elif line == b'hole ON':
        hole_motion.update(1)
    elif line == b'hole OFF':
        hole_motion.update(0)


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
    hole_motion.onOff = onHoleMotionOff
    init_IR_codes()             # init dict: { IR_CODE : function }
    sock_thr = Thread(target = sock_listen, args = ())
    sock_thr.start()
    ds = Thread(target = get_T, args = ())
    ds.start()                  # ds18s20 temerature sensor
    say_thrd = Thread(target = _say_queue, args = ())
    say_thrd.start()

    #####     main loop     #####
    while True:
        try:
            line = ard.read()      # read line from arduino
        except KeyboardInterrupt:
            log('KeyboardInterrupt received. Exit')
            print('KeyboardInterrupt received. \n')
            sys.exit(0)
        print(line)
        dispatch(line)
