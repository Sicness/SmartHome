import mplayer

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

