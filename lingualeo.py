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
	header = {"Cookie":"remember=q=eyJzaWQiOiIwOWMxNTQwYWQxMDhjMDYzN2RjMDM5OWMwOWE1YWJiOCIsImVkIjoiIiwiYXRpbWUiOjEzODQ0NTU5MTIsInVpZCI6NTUzODM4OH0=&sig=1b7d54e5e734b0134572a62ad805d6bf3d3774c719712ea0d29dc9eb31ad653b; lotteryPromo_seen=1;"}\

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

class dicts:

	def __init__(self):
		self.dicts = {'en': coach.Coach(), 'ru': coach.Coach()}
		self.last_update = None
		self.update()

	def get(self, lang):
		return self.dicts[lang]

	def sync(self):
		self.dicts['ru'].set_priority(self.dicts['en'])
		self.dicts['en'].set_priority(self.dicts['ru'])

	def update(self):
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
					self.dicts['en'].add([coach.Task({
						'question'		: word['word_value'], 
						'ques_descr'	: u"[{}]\n{}".format(word['transcription'], word['context']),
						'ques_sound'	: word['sound_url'],
						'answer'		: word['user_translates'][0]['translate_value'],
						'answer_list'	: re.split(r',\s*', word['user_translates'][0]['translate_value'].lower())
					})])
					self.dicts['ru'].add([coach.Task({
						'answer'		: word['word_value'], 
						'_hash'			: word['word_value'], 
						'description'	: u"[{}]\n{}".format(word['transcription'], word['context']),
						'sound'			: word['sound_url'],
						'question'		: word['user_translates'][0]['translate_value']
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

def main():
	if len(sys.argv) < 2 or sys.argv[1] not in ('en', 'ru'):
		raise Exception('usage: %s [en|ru]' % sys.argv[0])
	_dicts = load()
	if len(sys.argv) > 3 and sys.argv[1] == 'update':
		print 1
	else:
		_dicts.sync()
		_dicts.update()
		gui.start(_dicts.get(sys.argv[1]))

	save(_dicts)

if __name__ == '__main__':
	main()
