#!/usr/bin/python
# -*- coding: utf-8 -*-
import httplib
import json
import re
import pickle
import sys
import os
import time

import coach
import gui


FileName = 'dicts/lingualeo.st2'

#http://lingualeo.ru/glossary/getGlossary?glossaryId=244&_hash=20131129154330

def getresponse(conn):
	response = conn.getresponse()
	if response.status == 200:
		data = response.read()
		conn.close()
		return data
	else:
		raise Exception("{0} {1}".format(response.status, response.reason))

class remote_dict(object):

	host="lingualeo.ru"
	header = {"Cookie":"remember=q=eyJzaWQiOiIwOWMxNTQwYWQxMDhjMDYzN2RjMDM5OWMwOWE1YWJiOCIsImVkIjoiIiwiYXRpbWUiOjEzODQ0NTU5MTIsInVpZCI6NTUzODM4OH0=&sig=1b7d54e5e734b0134572a62ad805d6bf3d3774c719712ea0d29dc9eb31ad653b; lotteryPromo_seen=1; lotteryPromoNew_seen=1;newYear2014_promo_seen=1;promo_redirect_newYear2014_seen=1;"}\
#	header = {"Cookie":"remember=q=eyJzaWQiOiIwOWMxNTQwYWQxMDhjMDYzN2RjMDM5OWMwOWE1YWJiOCIsImVkIjoiIiwiYXRpbWUiOjEzODQ0NTU5MTIsInVpZCI6NTUzODM4OH0=&sig=1b7d54e5e734b0134572a62ad805d6bf3d3774c719712ea0d29dc9eb31ad653b; lotteryPromo_seen=1; lotteryPromoNew_seen=1"}\

	def __init__(self):
		self.conn = httplib.HTTPConnection(self.host)
		self._hash = None

	def gethash(self):
		if not self._hash:
			self.conn.request('GET', '/dashboard', headers=self.header)
			data = getresponse(self.conn)
			data = re.search(r'"serverHash":"(?P<hash>[0-9]+)"', data)
			self._hash = data.group("hash")
		return self._hash

	def __iter__(self):
		page = 1
		while True:
			self.conn.request('GET', '/userdict/json?sortBy=date&wordType=0&filter=all&page={page}&_hash={hash}'.format(page=page, hash=self.gethash()), headers=self.header) 
			data = json.loads(getresponse(self.conn))
			yield data
			#attributes of pages
			if data['show_more']:
				page += 1
			else:
				break

class remote_verbs(remote_dict):
	def __iter__(self):
		self.conn.request('GET', '/glossary/getGlossary?glossaryId=244&_hash={hash}'.format(hash=self.gethash()), headers=self.header) 
		data = json.loads(getresponse(self.conn))
		for word in data['glossary']['glossaryWords'].itervalues():
			yield word

class dicts:

	def __init__(self):
		self.dicts = {
				'en': coach.Coach(), 
				'ru': coach.Coach()
			}
		self.last_update = None
		self.update()

	def __getitem__(self, lang):
		return self.dicts[lang]

	def sync(self):
		l = ('ru', 'en', 'verbs')
		for i1 in l:
			for i2 in l:
				if i1 != i2:
					self.dicts[i1].set_priority(self.dicts[i2])

	def import_verbs(self):
		self.dicts['verbs'] = coach.Coach()
		for verb in remote_verbs():
			(v1, v2v3) = verb['word_value'].split(', ', 1)
			self.dicts['verbs'].add([coach.Task({
				'question'		: v1,
				'ques_descr'	: u'Введите II, III формы глагола',
				'answer'		: verb['word_value'],
				'answer_list'	: [v2v3],
				'description'	: u'[{}]\n{}'.format(verb['transcription'], verb['translate_value']),
				'sound'			: verb['sound_url']
			})])

	def update(self):
		self.dict_update()
		if 'verbs' not in self.dicts: self.import_verbs()

	def dict_update(self):
		if self.last_update and time.time() < self.last_update + 60*60:
			print "Data is fresh"
			return
		for data in remote_dict():
			for group in data['userdict3']:
				date = int(group['data'].split(":", 1)[1])
				if self.last_update and self.last_update > date:
					self.last_update = time.time()
					return
				print group['data']
				for word in group['words']:
					self.dicts['ru'].add([coach.Task({
						'answer'		: word['word_value'].lower(), 
						'_hash'			: word['word_value'], 
						'description'	: u"[{}]\n{}".format(word['transcription'], word['context']),
						'sound'			: word['sound_url'],
						'question'		: word['user_translates'][0]['translate_value']
					})])
					a =  word['user_translates'][0]['translate_value'] 
					al = re.split(r'[,;]\s*', a.lower()) 
					if a.find(u'ё') > -1:
						tst = re.split(r'[,;]\s*', al)
						for w in al:
							if w.find(u'ё') >-1:
								s = w.replace(u'ё', u'е')
								tst.append(s)
								a += u', '+s
						al = tst
					self.dicts['en'].add([coach.Task({
						'question'		: word['word_value'], 
						'ques_descr'	: u"[{}]\n{}".format(word['transcription'], word['context']),
						'ques_sound'	: word['sound_url'],
						'answer'		: a,
						'answer_list'	: al
					})])
		self.last_update = time.time()

def load():
	if not os.path.exists(FileName):
		return dicts()
	with open(FileName, 'r') as f:
		return pickle.load(f)

def save(_dicts):
	with open(FileName, 'w') as f:
		pickle.dump(_dicts, f)

def add_ru_translate(_dicts, words):
	_dicts['ru'].items()[hash(_dicts['en'].cur_item())].data.question += u', '.join([u'']+words)
	_dicts['en'].cur_item().answer += u', '.join([u'']+words)
	for word in words:
		_dicts['en'].cur_item().answer_list.append(word)

def change_ru_translate(_dicts, words):
	_dicts['en'].cur_item().answer = u', '.join(words)
	_dicts['en'].cur_item().answer_list = (words)
	_dicts['ru'].items()[hash(_dicts['en'].cur_item())].data.question = u', '.join(words)
	print ' '.join(_dicts['en'].cur_item().answer_list)

def split_ru_translate(_dicts):
	a = _dicts['en'].cur_item().answer
	_dicts['en'].cur_item().answer_list = re.split(r'[,;]\s*', a.lower())
	print ' '.join(_dicts['en'].cur_item().answer_list) 


def add_verbs(_dicts):
	for i in _dicts['verbs'].items().itervalues():
		d = i.data
		trans, answer = d.description.split("\n")
		trans = trans.split(' ', 1)[0]+']'
		print d.question, trans, answer
		_dicts['en'].add([coach.Task({
				'question'		: d.question,
				'ques_descr'	: u"{}\nverbs".format(trans),
				'answer'		: answer
				})])
		_dicts['ru'].add([coach.Task({
				'answer'		: d.question,
				'description'	: u"{}\nverbs".format(trans),
				'question'		: answer,
				'_hash'			: d.question
				})])
def main():
	if len(sys.argv) < 2 or sys.argv[1] not in ('en', 'ru', 'verbs', 'update'):
		raise Exception('usage: %s [en|ru|verbs|update]' % sys.argv[0])
	_dicts = load()
	if len(sys.argv) > 1 and sys.argv[1] == 'update':
#		split_ru_translate(_dicts)
		add_ru_translate(_dicts, [u'отдых'])
#		change_ru_translate(_dicts, [u'дать', u'давать', u'отдавать'])
#
		pass
	else:
		_dicts.sync()
		_dicts.update()
		gui.start(_dicts[(sys.argv[1])])

	save(_dicts)

if __name__ == '__main__':
	main()
