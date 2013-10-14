#!/usr/bin/python
# -*- coding: utf-8 -*-

def plural():
	sdata = u"""\
wheel колесо wheels колеса
house дом houses дома
box коробка boxes коробки
\
shelf полка shelves полки
\
belief вера,убеждение beliefs убеждения
chief начальник chiefs начальники
dwarf гном dwarfs гномы
goof оплошность goofs оплошности
proof доказательство proofs доказательства
roof крыша roofs крыши
safe сейф safes сейфы
gulf залив gulfs заливы
reef риф reefs рифы
\
deer олень deer олени
mouse мышь mice мыши
tooth зуб teeth зубы
fish рыба fish рыбы
foot ступны feet ступни
louse вош lice вши
goose гусь geese гуси
sheep овца sheep овцы
woman женщина women женщины
man мужчина men мужчины
child ребенок children дети\
"""
	data = []
	for i in [s.split(' ') for s in sdata.split('\n')]:
		data += [
				(i[1], u'', i[0], u''),
				(i[3], u'', i[2], u'%s - %s' % (i[1],i[0])),
				(i[0], u'множ. число', i[2], i[3])
		]
	return data

def get():
	data = plural() 
	return 'slava.st', data

if __name__ == '__main__':
	print get()
