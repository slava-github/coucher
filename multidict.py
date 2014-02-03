#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import coach
import unittest

class smartTask(coach.Task):
	def __init__(self, _type, struct):
		self._type = _type
		self.data = struct
		self._hash = struct['question']['string']

	def get(self, key, name):
		if(self._type == 'ru'):
			key = 'question' if key == 'answer' else 'answer'
			if name == 'string':
				s = self.data['answer']['delimiter']+' '
				return s.join(self.data[key]['list'])
			if key == 'answer' and name == 'sound':
				return None
			if name == 'list':
				return [self.data[key]['string']]
		elif(self._type == 'verb_forms'):
			if(key == 'question' and name == 'sound'):
				return None
			if(key == 'answer'):
				key = 'verb_forms'
				if name == 'list': 
					return [self.data[key]['string']]
		return super(smartTask, self).get(key, name)

	def set(self, key, name, val):
		if(self._type == 'ru'):
			key = 'question' if key == 'answer' else 'answer'
			if name == 'string':
				name = 'list'
				val = re.split(r' ?['+self.data['answer']['delimiter']+'] ?', val)
			elif name == 'sound':
				return
			elif name == 'list':
				name = 'string'
				val = val[0]
		elif(self._type == 'verb_forms'):
			if(key == 'question' and name == 'sound'):
				return
			if(key == 'answer'):
				key = 'verb_forms'
				if name == 'list': 
					name = 'string'
					val = val[0]

		self.data[key][name] = val
	
	def __getattr__(self, name):
		if name == 'norm_answer':
			self.normalize_answer()
			return self.__dict__['norm_answer']
		return super(smartTask, self).__getattr__(name)

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
		#			'list':,
		#			'delimiter':,
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

class TestCase(unittest.TestCase):

	def setUp(self):
		self.test = MultiDict()
		self.ustr = u'Щёрс'
		self.data = {
			'question':{
				'string': 'test1',
				'desc': 'This is test1',
				'sound': 'file1'
			},
			'answer':{
				'list': [u'Тест1', u'Тест2', self.ustr],
				'delimiter': '.',
				'desc' : u'Это Текст1, Текст2',
				'sound': 'file2'
			},
			'verb_forms':{
				'string': 'vII, vIII',
				'desc': u'Глаголы',
				'sound': 'file3'
			}
		} 
		self.test.append(self.data)

	def testGet(self):
		c1 = iter(self.test['ru']).next()
		delim = self.data['answer']['delimiter']+' '
		self.assertEqual(c1.question('string'), delim.join(self.data['answer']['list']))
		self.assertEqual(c1.question('sound'), None)
		self.assertEqual(c1.answer('list'), [self.data['question']['string']])

		c2 = iter(self.test['en']).next()
		self.assertEqual(c2.question('string'), self.data['question']['string'])
		self.assertEqual(c2.question('sound'), self.data['question']['sound'])
		self.assertEqual(c2.answer('list'), self.data['answer']['list'])

		c3 = iter(self.test['verbs']).next()
		self.assertEqual(c3.question('string'), self.data['question']['string'])
		self.assertEqual(c3.question('sound'), None)
		self.assertEqual(c3.answer('list'), [self.data['verb_forms']['string']])
	
	def testSet(self):
		c1 = iter(self.test['ru']).next()
		c2 = iter(self.test['en']).next()
		s = 'test3, test4'
		c2.question('string', s)
		self.assertEqual(self.data['question']['string'], s)
		self.assertEqual(c1.answer('list'), [s])
		self.assertEqual(c2.question('string'), s)
		self.assertEqual(c2.answer('list'), self.data['answer']['list'])

		l = ['test5', 'test6']
		c1.question('string', self.data['answer']['delimiter'].join(l))
		self.assertEqual(c2.answer('list'), l)
		c1.answer('list', l)
		self.assertEqual(self.data['question']['string'], l[0])
		c1.question('sound', 'ff')
		self.assertNotEqual(self.data['answer']['sound'], 'ff')
		self.assertNotEqual(self.data['answer']['sound'], None)

		c3 = iter(self.test['verbs']).next()
		s = 'test7'
		c3.question('string', s)
		self.assertEqual(self.data['question']['string'], s)
		l = ['test8', 'test9']
		c3.answer('list', l)
		self.assertEqual(self.data['verb_forms']['string'], l[0])
		c3.question('sound', 'ff')
		self.assertNotEqual(self.data['answer']['sound'], 'ff')
		self.assertNotEqual(self.data['answer']['sound'], None)
	
	def testNormalize(self):
		c1 = iter(self.test['en']).next()
		self.assertTrue(c1 == self.ustr.replace(u'ё', u'е'))

if __name__ == '__main__':
	unittest.main()
