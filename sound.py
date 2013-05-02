# -*- coding: utf-8 -*-

from threading import Thread
from time import sleep
from datetime import datetime, time
import urllib
import Queue

import mplayer

night_min = time(hour = 23)
night_max = time(hour = 8)

user_agent = ("Mozilla/5.0 (Windows NT 6.1; WOW64) "
              "AppleWebKit/537.17 "
              "(KHTML, like Gecko) Chrome/24.0.1312.60 Safari/537.17")

class Alice:
    def __init__(self, glob = None):
        self.player = mplayer.Player(args=('-user-agent', user_agent))  #, '-ao', 'pulse'))
        self.player.cmd_predix = ''
        self.queue = Queue.Queue()
        self.glob = glob
        self.thrd = Thread(target = self._loop, args = (), name = "alice")
        self.thrd.start()
        self.glob.get('threads').append(self.thrd)

    def _say(self, text, lang = "ru"):
        if self.isNight():
            return
        url = url = (u"http://translate.google.com/"
                    u"translate_tts?tl={0}&q={1}".format(
                    lang, urllib.quote(text)))
        self.player.loadfile(url, 1)

    def say(self, text, lang = "ru"):
        self.queue.put((text, lang))

    def _loop(self):
        """ Runed in dedicated thread
        " Takes from queue querty for speech
        " and sends it to TTS (self._say) """
        while True:
            if self.glob is not None:
                if self.glob.get('terminate'):
                    print "Alice: flag terminate found. Exit."
                    return
            try:
                item = self.queue.get_nowait()
                # >>>  item = (text, lang)
            except:
                sleep(0.5)
                continue
            self._say(item[0],item[1])
            sleep(0.6)

    def isNight(self):
        """ Returns True if night right now """
        now = datetime.now().time()
        return (now > night_min) or ( now <  night_max)

    def now(self, time = None):
        """ now -> str
        time is datedate.datetime.now.time() """
        if time is None:
            time = datetime.now().time()
        if time.minute < 10:
            return time.strftime("%H ноль %m")
        else:
            return time.strftime("%H %M")

class Ultra:
    def __init__(self):
        self.player = mplayer.Player()
        self._inPlay = False
    def play(self):
        self.player.loadfile('http://94.25.53.133:80/ultra-56.aac')
        self._inPlay = True
    def stop(self):
        self.player.stop()
        self._inPlay = False
    def switch(self):
        """ Switch between on/off """
        if self._inPlay:
            self.stop()
        else:
            self.play()

