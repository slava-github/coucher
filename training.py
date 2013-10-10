#!/usr/bin/python
# -*- coding: utf-8 -*-

import coach
import gui

import dicts.slava

if __name__ == '__main__':

	file_name, data = dicts.slava.get()

	c = coach.load(file_name)
	c.add([coach.Task(*i) for i in data])
	gui.start(c);
	coach.save(file_name, c)
