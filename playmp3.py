#!/usr/bin/python

import subprocess as pr
#import httplib
import os

CACHE_PATH = 'sound.cache'

def playfile(fname):
	pr.call(['play', fname])

def playurl(url):
	fname = "{}{}".format(CACHE_PATH, url[url.rfind('/'):])
	if not os.path.exists(fname):
		pr.call('curl {} >{}'.format(url, fname), shell=True)
	playfile(fname)

def play(name):
	if name[0:4] == 'http':
		playurl(name)
	else:
		playfile(name)

if __name__ == '__main__':
	play('http://d2x1jgnvxlnz25.cloudfront.net/v2/1/61567-631152008.mp3')
