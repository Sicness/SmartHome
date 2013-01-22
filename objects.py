# -*- coding: UTF-8 -*-

class Vars:
	""" Class for global vars """
	def	__init__(self):
		self.vars = dict()

	def get(self, var):
	""" Get value of global var """
		if var in self.vars:
			return vars[var]
		else:
			return ''

	def set(self, name, value):
	""" Set value of global var """
		self.vars[name] = value

	def exist(var):
	""" return True if global var exist """
		return var in self.vars
