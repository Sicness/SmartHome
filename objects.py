# -*- coding: utf-8 -*-

import datetime
from threading import Thread
from time import sleep
import subprocess


LIGHT_MODE_AUTO = 1
LIGHT_MOTE_MANUAL = 0

class Vars:
    def __init__(self):
        """ Class for global vars """
        self.vars = dict()

    def get(self, var):
        """ Get value of global var """
        if var in self.vars:
            return self.vars[var]
        else:
            return ''

    def set(self, name, value):
        """ Set value of global var """
        self.vars[name] = value

    def exist(self, var):
        """ return True if global var exist """
        return var in self.vars


class MotionSensor:
    def __init__(self, state = 0):
        self.state = state
        self.onOn = None
        self.onOff = None
        self.onChange = None

    def update(self, state):
            self.state = state
            if self.onChange != None:
                self.onChange()
            if state:
                if self.onOn != None:
                    self.onOn()
            else:
                if self.onOff != None:
                    self.onOff()

class Task:
    def __init__(self, name, when, foo):
        self.name = name
        self.when = when
        self.do = foo

    def show(self):
        print "Name: ", self.name,
        print "\tWhen: ", self.when,
        print "\tDo: ", self.do

class Crontab:
    def __init__(self, glob = None):
        self.tasks = list()
        self._thread = Thread(target = self.__check, args = ())
        self._thread.start()
        self.glob = glob

    def add(self, name, time, foo):
        """ Add new task to cron.
        Name - str
        time - datetime
        foo - pointer to function"""
        task = Task(name, time, foo)
        for t in self.tasks:
            if t.name == task.name:         # If we alredy have task with this name
                return -1
        self.tasks.append(task)
        return 0

    def remove(self, name):
        """ Detele task from cron by name """
        found = None
        for task in self.tasks:
            if task.name == name:
                found = task
        if found != None:
            self.tasks.remove(found)
            return 0
        else:
            return -1

    def isExist(self, name):
        for task in self.tasks:
            if task.name == name:
                return True
        return False

    def replace(self, name, time, foo):
        """ Create or replace a new task to cron.
        Name - str
        time - datetime
        foo - pointer to function"""
        self.remove(name)
        task = Task(name, time, foo)
        for t in self.tasks:
            if t.name == task.name:         # If we alredy have task with this name
                return -1
        self.tasks.append(task)
        return 0

    def ls(self):
        print "Tasks in cron:"
        for task in self.tasks:
            print task.show()

    def __check(self):
        """ Cron tick """
        while True:
            now = datetime.datetime.now()
            remove = list()
            for task in self.tasks:
                if task.when < now:
                    t = Thread(target = task.do, args= () )
                    t.start()
                    remove.append(task)
            for task in remove:
                self.tasks.remove(task)
            sleep(1)
            if self.glob is not None:
                if self.glob.get('terminate'):
                    print("Crontab: found the terminate flag. Exit.")
                    return

class gpioLight:
    def __init__(self, pin, state = 0, mode = LIGHT_MOTE_MANUAL):
        #self._pin = pin
        # to use Raspberry Pi board pin numbers
        #GPIO.setmode(GPIO.BOARD)
        #GPIO.setup(self._pin, GPIO.OUT)
        self._mode = mode
        if self._mode == LIGHT_MOTE_MANUAL:
            self.setManualState(state)
        else:
            self.setAutoState(state)

    def _set(self, state):
        self._state = state
        if state == 1:
            subprocess.call(["gpio_11", "1"])
        else:
            subprocess.call(["gpio_11", "0"])

    def setAutoState(self, state):
        """ Turn on/off light (1,0)"""
        self._autoState = state
        if self._mode == LIGHT_MOTE_MANUAL:
            return
        self._set(state)

    def setManualState(self, state):
        self._mode = LIGHT_MOTE_MANUAL
        self._set(state)

    def setManualStateOff(self):
        self.setManualState(0)

    def setManualStateOn(self):
        self.setManualState(1)

    def setMode(self, mode):
            self._mode = mode
            if mode == LIGHT_MODE_AUTO:
                self._set(self._autoState)

    def getMode(self):
        return self._mode
