#!/usr/bin/python
# -*- coding: utf-8 -*-

def simple():
	return [
		[u'Тест', '', u'test', ''],
		[u'Слово', '', u'word', ''],
		[u'Бежать', '', u'run', ''],
		[u'Класс', '', u'class', ''],
		[u'День', '', u'day', ''],
		[u'Вверх', '', u'up', ''],
		[u'Сейчас', '', u'now', '']
	]

def multtable():
	return [("{0}x{1}".format(2,x), '', 2*x, '') for x in range(11)]

