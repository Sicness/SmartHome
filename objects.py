# -*- coding: UTF-8 -*-

class Vars:
	def	__init__(self):
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
					self.onOff()
			else:
				if self.onOff != None:
					self.onOff()

