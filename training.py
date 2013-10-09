#!/usr/bin/python
# -*- coding: utf-8 -*-

import coach
import gui


def simple_coach():
	return coach.Coach(coach.Task(*x) for x in [
				[u'Тест', '', u'test', ''],
				[u'Слово', '', u'word', ''],
				[u'Бежать', '', u'run', ''],
				[u'Класс', '', u'class', ''],
				[u'День', '', u'day', ''],
				[u'Вверх', '', u'up', ''],
				[u'Сейчас', '', u'now', '']
			])

def multtable_coach():
	return coach.Coach([["{0}x{1}".format(2,x), 2*x] for x in range(11)])


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
		return [coach.Task(
				x['tr'], 
				u"<i>{0}</i><br/>{1}".format(x['pos'], x['ex']['tr'][0]['text']),
				x['word'], 
				x['ex']['text']
			) for x in self.__dict.itervalues()]


def dict_coach():
	file_name = 'dict.st'
	dc = coach.load(file_name)
	dc.add(Dict([
		'cat', 'class', 'now', 'day', 'up', 'down', 'get', 'go', 'find', 'found'
		]).as_tasks())
	return (file_name, dc)


def triple():
	file_name = 'triple.st'
	data = [
			(u'calf', u'теленок', u'calves', u'телята'),
			(u'shelf', u'полка', u'shelves', u'полки'),
			(u'leaf', u'лист', u'leaves', u'листы'),
			(u'half', u'половина', u'halves', u'половины'),
			(u'knife', u'нож', u'knives', u'ножи'),
			(u'life', u'жизнь', u'lives', u'жизни'),
			(u'thief', u'вор', u'theves', u'воры'),
			(u'elf', u'эльф', u'elves', u'эльфы'),
			(u'wife', u'жена', u'wives', u'жены'),
			(u'man', u'мужчина', u'men', u'мужчины'),
			(u'child', u'ребенок', u'children', u'дети'),
		]
	cdata = []
	for i in data:
		cdata[len(cdata):] = (
				coach.Task(i[1], u'', i[0], u''),
				coach.Task(i[3], u'', i[2], u''),
				coach.Task(i[0], u'множ. число', i[2], u'')
			)

	c = coach.load(file_name)
	c.add(cdata)
	return (file_name, c)

if __name__ == '__main__':
	file_name, c = triple()
	gui.start(c);
	coach.save(file_name, c)
