#!/usr/bin/python
# -*- coding: utf-8 -*-

import coach
import gui
import sys

def init(c):
	for i in range(10):
		for j in range(10):
			c.add(coach.Task("{}x{}=".format(i, j), '', str(i*j), ''))

if __name__ == '__main__':
	
	file_name = 'test.st'
	c = coach.load(file_name)
	if len(c) == 0:	init(c)
	gui.main(c)
	coach.save(file_name, c)
