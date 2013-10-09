import httplib
import json

KEY="dict.1.1.20130906T203615Z.e5c162533d4550a7.2b015ab99c0ffaa623970378ee2bd7e771bf6063"
HOST="dictionary.yandex.net"
URL="/api/v1/dicservice.json/lookup?key={key}&lang={lang}&ui={ui}&text={word}"

def get_artdict(word):
	conn = httplib.HTTPSConnection(HOST)
	url =  URL.format(key=KEY, lang="en-ru", ui="en", word=word)
	print url
	conn.request('GET', url)
	response = conn.getresponse()
	result = {}
	if response.status == 200:
		data = json.loads(response.read())
		data = data['def'][0]
		result = {
			'word'	: data['text'],
			'pos'	: data['pos'],
			'ts'	: data['ts'],
			'tr'	: data['tr'][0]['text'],
			'ex'	: data['tr'][0]['ex'][0]
		}
	else:
		print "{0} {1}".format(response.status, response.reason)
	conn.close()
	return result

if __name__ == '__main__':
	import sys
	print get_artdict(sys.argv[1])
