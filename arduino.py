import serial
import sys
from log import log
from log import err
import time

class Arduino:
    def __init__(self, adr, onFound = None, onLost = None, baudrate = 9600):
        self.adr = adr
        self.baudrate =  baudrate
        self.onFound = onFound
        self.onLost  = onLost
        self._connected = None
        self.connect()

    def connect(self):
        while True:
            try:
                self.s = serial.Serial(self.adr, self.baudrate)
            except:
                if self._connected == True:
                    err("Loose connection with Serail %s:%s %s" % (self.adr, self.baudrate, sys.exc_info()[0]))
                    if self.onLost != None:
                        self.onLost()
                elif self._connected == None:
                    err("Can't open seril port %s:%s %s" % (self.adr, self.baudrate, sys.exc_info()[0]))
                self._connected = False
                time.sleep(5)
                continue

            # Success conntect to serial
            log('Recconnectred to Serail %s:%s' % (self.adr, self.baudrate))
            if self._connected == False:
                if self.onFound != None:
                    self.onFound()
            self._connected = True
            break

    def read(self):
        """ Read line from Serial with out \r\n """
        while True:
            line = ''
            try:
                line = self.s.readline()
            except KeyboardInterrupt:
                raise
            except:
                err("Can't read from serial: %s" % sys.exc_info()[0])
                self.connect()
                continue
            break
        return line[:-2]
