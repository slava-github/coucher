#!/usr/bin/python
import httplib
import json
import re
import pickle
import sys

sys.path.append(sys.path[0]+'/..')
import coach 

def getresponse(conn):
	response = conn.getresponse()
	if response.status == 200:
		data = response.read()
		conn.close()
		return data
	else:
		raise Exception("{0} {1}".format(response.status, response.reason))

class lingualeo(object):

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

	def get_dicts_page(self, page):
		self.conn.request('GET', '/userdict/json?sortBy=date&wordType=0&filter=all&page={page}&_hash={hash}'.format(page=page, hash=self.gethash()), headers=self.header) 
		data = json.loads(getresponse(self.conn))
		return data

def get(dicts):
	ll = lingualeo()
#	print pickle.dumps(ll.get_dicts_page(1))

	data = pickle.load(open('dump'))

	#attributes of pages
	print data['show_more']

	en_dict = []
	ru_dict = []
	#group by date
	for group in data['userdict3']:
		print group['data']
		for word in group['words']:
			dicts['en'][1].add([coach.Task({
				'question'		: word['word_value'], 
				'ques_descr'	: u"[{}]\n{}".format(word['transcription'], word['context']),
				'ques_sound'	: word['sound_url'],
				'answer'		: word['user_translates'][0]['translate_value']
			})])
	return dicts

if __name__ == '__main__':
	dicts = {}
	for lang in ('en', 'ru'):
		name = 'lingualeo_{}.st'.format(lang)
		dicts[lang] = [name, coach.load(name)]
	dicts = get(dicts)
	for data in dicts.itervalues():
		coach.save(data[0], data[1])


