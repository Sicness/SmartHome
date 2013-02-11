# -*- coding: UTF-8 -*-

import datetime
from threading import Thread
from time import sleep

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


class Crontab:
    def __init__(self):
        self.tasks = list()
        self._thread = Thread(target = self.__check, args = ())
        self._thread.start()

    def add(self, task):
        """ Add new task to cron.
        Task - object of 'Task' class """
        for t in self.tasks:
            if t.name == task.name:         # If we alredy have task with this name
                return -1
        self.tasks.append(task)

    def remove(self, name):
        """ Detele task from cron by name """
        found = None
        for task in self.tasks:
            if task.name == name:
                found = task
        if found != None:
            self.tasks.remove(found)

    def isExist(self, name):
        for task in self.tasks:
            if task.name == name:
                return True
        return False

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
