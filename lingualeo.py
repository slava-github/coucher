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
import multidict

from PyQt4 import QtGui
import gui
import mgui

PATH = os.path.dirname(os.path.realpath(__file__))
FileName = PATH + '/dicts/lingualeo.st2'

#http://lingualeo.ru/glossary/getGlossary?glossaryId=244&_hash=20131129154330


def getresponse(conn):
    response = conn.getresponse()
    if response.status == 200:
        data = response.read()
        conn.close()
        return data
    else:
        raise Exception("{0} {1}".format(response.status, response.reason))


class RemoteDict(object):

    host = "lingualeo.ru"
    header = {"Cookie": "lingualeouid=137898470726105; userid=5538388; servid=9d164a0a257a3d0d7a3669e6cf15a52b8ccf41ea1a5767f626fdaccbd97479b9840340dd59b1ff27; AWSELB=75C701150A9420ACA77B49A59BB2636792D3E5911E5E4FF2265D8AB1ABE56C8DFAABF4477CD9A02BF6901A6DF3885A0F9280A5D9D7DAAFCF9613C0F7B6A2A2DEFDC6AD67EE; fun_quest_wordset=11336; remember=54825400f81d2928a3c409ddc8b1d4a8dca3ecc9310f169a0c66ff7cd5cb00add75be52e03c1f7cd; fun_quest_completed=1; fun_quest_repaired=1; abmainv2=payment_timer;"}

    def __init__(self):
        self.conn = httplib.HTTPConnection(self.host)
        self._hash = None

    def gethash(self):
        if not self._hash:
            self.conn.request('GET', '/ru/userdict/json', headers=self.header)
            data = json.loads(getresponse(self.conn))
#            data = re.search(r'"serverHash":"(?P<hash>[0-9]+)"', data)
            self._hash = data["_hash"]
        return self._hash

    def __iter__(self):
        page = 1
        while True:
            self.conn.request('GET', '/ru/userdict/json?sortBy=date&wordType=0&filter=all&page={page}&_hash={hash}'.format(page=page, hash=self.gethash()), headers=self.header)
            data = json.loads(getresponse(self.conn))
            yield data
            #attributes of pages
            if data['show_more']:
                page += 1
            else:
                break


class RemoteVerbs(RemoteDict):
    def __iter__(self):
        self.conn.request('GET', '/glossary/getGlossary?glossaryId=244&_hash={hash}'.format(hash=self.gethash()), headers=self.header)
        data = json.loads(getresponse(self.conn))
        for word in data['glossary']['glossaryWords'].itervalues():
            yield word


def answer_split(s):
    s = s.replace(';', ',')
    delim = '.' if s.find('.') > -1 else ','
    s = re.split(r' ?[' + delim + r'] ?', s)
    return (s, delim)


class dicts:

    def __init__(self):
        self.dicts = multidict.MultiDict()
        self.verbs = False
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

    def update(self):
        self.dict_update()
        self.import_verbs()

    def dict_update(self):
        if self.last_update and time.time() < self.last_update + 60 * 60:
            print "Data is fresh"
            return
        print 'Get dictionary...'
        for data in RemoteDict():
            for group in data['userdict3']:
                date = int(group['data'].split(":", 1)[1])
                if self.last_update and self.last_update > date:
                    self.last_update = time.time()
                    return
                print group['data']
                for word in group['words']:
                    (translate, delim) = answer_split(word['user_translates'][0]['translate_value'])
                    struct = {
                        'question': {
                            'string': word['word_value'].lower(),
                            'desc': u"[{}]\n{}".format(word['transcription'], word['context']),
                            'sound': word['sound_url'],
                        },
                        'answer': {
                            'list': translate,
                            'delimiter': delim,
                            'desc': '',
                            'sound': word['sound_url'],
                        }
                    }
                    self.dicts.append(struct)
        self.last_update = time.time()

    def import_verbs(self):
        if self.verbs:
            return
        print "Get Verbs..."
        for verb in RemoteVerbs():
            (v1, v2v3) = verb['word_value'].split(', ', 1)
            if v1 not in self.dicts:
                (translate, delim) = answer_split(verb['translate_value'])
                struct = {
                    'question': {
                        'string': v1,
                        'desc': u'Неправильный глагол',
                        'sound': verb['sound_url']
                    },
                    'answer': {
                        'list': translate,
                        'delimiter': delim,
                        'desc': u'Неправильный глагол',
                        'sound': verb['sound_url']
                    }
                }
            else:
                struct = self.dicts.base[v1]
            struct['verb_forms'] = {
                'string': v2v3,
                'desc': u'[{}]\n{}'.format(verb['transcription'], verb['translate_value']),
                'sound': verb['sound_url']
            }
            self.dicts.append(struct)
        self.verbs = True


def load():
    if not os.path.exists(FileName):
        return dicts()
    with open(FileName, 'r') as f:
        return pickle.load(f)


def save(_dicts):
    with open(FileName, 'w') as f:
        pickle.dump(_dicts, f)


def add_ru_translate(_dicts, words):
    _dicts['ru'].items()[hash(_dicts['en'].cur_item())].data.question += u', '.join([u''] + words)
    _dicts['en'].cur_item().answer += u', '.join([u''] + words)
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
        trans = trans.split(' ', 1)[0] + ']'
        print d.question, trans, answer
        _dicts['en'].add([coach.Task({
            'question': d.question,
            'ques_descr': u"{}\nverbs".format(trans),
            'answer': answer
        })])
        _dicts['ru'].add([coach.Task({
            'answer': d.question,
            'description': u"{}\nverbs".format(trans),
            'question': answer,
            '_hash': d.question
        })])


def run(arg):
    _dicts = load()
    if arg == 'update':
        print (_dicts['en'].cur_item().answer('list')[0] == u'Чему быть, того не миновать')
#        print _dicts['verbs'].items()[hash('hear')].data.answer_list
#        split_ru_translate(_dicts)
#        add_ru_translate(_dicts, [u'отдых'])
#        change_ru_translate(_dicts, [u'дать', u'давать', u'отдавать'])
#        pass
    else:
        _dicts.sync()
        _dicts.update()
        gui.MainForm(_dicts[arg]).exec_()

    save(_dicts)


def main():
    app = QtGui.QApplication([])
    if len(sys.argv) < 2 or sys.argv[1] not in ('en', 'ru', 'verbs', 'update'):
        form = mgui.MainForm()
        while 1:
            result = form.exec_()
            if result:
                run(result)
            else:
                break
#        raise Exception('usage: %s [en|ru|verbs|update]' % sys.argv[0])
    else:
        run(sys.argv[1])

if __name__ == '__main__':
    main()
