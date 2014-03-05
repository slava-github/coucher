#!/usr/bin/python
# -*- coding: utf-8 -*-

import coach
import gui
import sys

if __name__ == '__main__':
	
	file_name = sys.argv[1]
	c = coach.load(file_name)
	gui.main(c)
	coach.save(file_name, c)
