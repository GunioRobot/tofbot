#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

class Tofades(object):
	"""
	Awesome tofades
	"""
	
	__sentences = [
		("Ho ho ho"),
		("Ha ha ha")
	]
	
	def get(self, index = None):
		pool = self.__class__.__sentences
		if index:
			return pool[index % len(pool)];
		else:
			random.seed()
			return pool[ random.randint(0, len(pool)-1) ];

if __name__ == "__main__":
	tof = Tofades()
	print tof.get()
	print tof.get(1)
