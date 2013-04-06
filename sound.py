from threading import Thread
from time import sleep
import urllib
import Queue

import mplayer


user_agent = ("Mozilla/5.0 (Windows NT 6.1; WOW64) "
              "AppleWebKit/537.17 "
              "(KHTML, like Gecko) Chrome/24.0.1312.60 Safari/537.17")

class Alice:
    def __init__(self):
        self.player = mplayer.Player(args=('-user-agent', user_agent))  #, '-ao', 'pulse'))
        self.player.cmd_predix = ''
        self.queue = Queue.Queue()
        self.thrd = Thread(target = self._loop, args = ())
        self.thrd.start()

    def _say(self, text, lang = "ru"):
        url = url = (u"http://translate.google.com/"
                    u"translate_tts?tl={0}&q={1}".format(
                    lang,
                    urllib.quote(text)))
        self.player.loadfile(url, 1)

    def say(self, text, lang = "ru"):
        self.queue.put((text, lang))

    def _loop(self):
        while True:
            try:
                item = self.queue.get_nowait()
                # >>>  item = (text, lang)
            except:
                sleep(0.5)
                continue
            self._say(item[0],item[1])
            sleep(0.5)


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

