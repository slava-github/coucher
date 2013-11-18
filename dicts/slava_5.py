#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
sys.path.append(sys.path[0]+'/..')
import coach 

def generate(cdict):
	sdata = u"""\
good хороший
better лучше
the_best лучший
bad плохой
worse хуже
the_worst худший
far далеко
further дальше
the_furthest дальний\
"""
	for i in [s.split(' ') for s in sdata.split('\n')]:
		cdict.add([ coach.Task(i[1], u'', i[0].replace('_',' '), u'') ])
	return cdict

file_name = 'slava_5.st'

if __name__ == '__main__':
	coach.save(file_name, generate(coach.load(file_name)))
