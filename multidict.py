#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import coach

BindKeys = {
	'en':{
		'question' : ['question','string'],
		'ques_descr' : ['question','desc'],
		'ques_sound' : ['question','sound'],
		'answer' : ['answer','string'],
		'description' : ['answer','desc'],
		'sound' : ['answer','sound'],
	},
	'ru':{
		'question' : ['answer','string'],
		'ques_descr' : ['answer','desc'],
		'answer' : ['question','string'],
		'description' : ['question','desc'],
		'sound' : ['question','sound'],
	},
	'verb_forms':{
		'question' : ['question','string'],
		'ques_descr' : ['question','desc'],
		'ques_sound' : ['question','sound'],
		'answer' : ['verb_forms','string'],
		'description' : ['verb_forms','desc'],
		'sound' : ['verb_forms','sound'],
	},
}
BindKeys['verb'] = BindKeys['en']

class smartTask(coach.Task):
	def __init__(self, _type, struct):
		self.__dict__['_type'] = _type
		self.__dict__['data'] = struct
		self.__dict__['_hash'] = struct['question']['string']

	def __getattr__(self, name):
		if name == 'answer_list':
			keys = BindKeys[self.__dict__['_type']]['answer']
			val = self.__dict__['data'][keys[0]][keys[1]].lower()
			if self.__dict__['_type'] == 'verb_forms':
				result = [val]
			else:
				if '.' in val:
					delimiters = '.'
				else:
					delimiters = ';,'
				result = self.normalize_answer(delimiters)
			return result

		elif '_type' in self.__dict__ and name in BindKeys[self.__dict__['_type']]:
			keys = BindKeys[self.__dict__['_type']][name]
			return self.__dict__['data'][keys[0]][keys[1]]
		else:
			return super(smartTask, self).__getattr__(name)

	def __setattr__(self, name, value):
		if name not in ['answer_list']:
			if name in BindKeys[self._type]: 
				keys = BindKeys[self._type][name]
				self.data[keys[0]][keys[1]] = value
			else:
				super(smartTask, self).__setattr__(name, value)

class MultiDict:
	
	def __init__(self):
		self.dicts = {
				'en' : coach.Coach(),
				'ru' : coach.Coach(),
				'verbs' : coach.Coach()
		}
		self.base = {}
		# Структура данных
		#		'question': {
		#			'string':,
		#			'desc'	:,
		#			'sound'	:,
		#		},
		#		'answer': {
		#			'string':,
		#			'desc'	:,
		#			'sound'	:,
		#		}
		#		'verb_forms': {
		#			'string':,
		#			'desc'	:,
		#			'sound'	:,
		#		}
		#

	def append(self, struct):
		self.base[struct['question']['string'].lower()] = struct
		for i in ['en', 'ru']:
			self.dicts[i].add([smartTask(i, struct)])
		if 'verb_forms' in struct:
			self.dicts['verbs'].add([smartTask('verb_forms', struct)])

	def __getitem__(self, name):
		return self.dicts[name]

	def __contains__(self, key):
		return key in self.base

def main():
	test = MultiDict()
	test.append({
		'question':{
			'string': 'test1, test2',
			'desc': 'This is test1, test2',
			'sound': 'file1'
		},
		'answer':{
			'string': u'Тест1, Тест2, Щёрс',
			'desc' : u'Это Текст1, Текст2',
			'sound': 'file2'
		}
	})
	c1 = test['ru']
	print iter(c1).next().question
	print iter(c1).next().answer_list

	c2 = test['en']
	print iter(c2).next().question
	print iter(c2).next().answer_list

	c2.cur_item().question = 'test3'
	print c1.cur_item().answer
	print c1.cur_item().answer_list

if __name__ == '__main__':
	main()
