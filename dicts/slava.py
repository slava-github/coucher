#!/usr/bin/python
# -*- coding: utf-8 -*-

def plural():
	sdata = u"""\
calf теленок calves телята
shelf полка shelves полки
leaf лист leaves листы
half половина halves половины
knife нож knives ножи
life жизнь lives жизни
thief вор theves воры
elf эльф elves эльфы
wife жена wives жены\
\
man мужчина men мужчины
child ребенок children дети\
"""
	data = []
	for i in [s.split(' ') for s in sdata.split('\n')]:
		data += [
				(i[1], u'', i[0], u''),
				(i[3], u'', i[2], u''),
				(i[0], u'множ. число', i[2], u'')
		]
	return data

def get():
	data = plural() 
	return 'slava.st', data

if __name__ == '__main__':
	print get()
