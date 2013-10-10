#!/usr/bin/python
# -*- coding: utf-8 -*-

import getdict
import json

class Dict():

	conf_file = 'dict.dat'

	def __init__(self, words):
		self.__load()
		for word in words:
			if word not in self.__dict:
				self.__dict[word] = self.__from_yandex(word)
		self.__save()

	def __save(self):
		with open(self.conf_file, 'w') as f:
			f.write(json.dumps(self.__dict))

	def __load(self):
		self.__dict = {}
		try:
			f = open(self.conf_file)
			self.__dict = json.load(f)
		except:
			pass

	def __from_yandex(self, word):
		print "GET "+word
		return getdict.get_artdict(word)

	def as_tasks(self):
		return [(
				x['tr'], 
				u"<i>{0}</i><br/>{1}".format(x['pos'], x['ex']['tr'][0]['text']),
				x['word'], 
				x['ex']['text']
			) for x in self.__dict.itervalues()]


def get():
	file_name = 'dict.st'
	dc = coach.load(file_name)
	dc.add(Dict([
		'cat', 'class', 'now', 'day', 'up', 'down', 'get', 'go', 'find', 'found'
		]).as_tasks())
	return (file_name, dc)

