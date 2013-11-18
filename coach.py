#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
import pickle
import os.path

NewItems = 5

Steps = 5
MaxLevel = 3
ProbStep = 10

class Item(object):
	def __init__(self, d):
		self.data = d
		self.step = 0
		self.level = 0
		self.level_changed = 0;

	def dec(self):
		self.level_changed = 0;
		if self.level < MaxLevel:
			self.step += 1
			if self.step >= Steps:
				self.step = 0
				self.level += 1 
				self.level_changed = 1
		else:
			self.step = 1

	def inc(self):
		self.level_changed = 0;
		if self.level:
			self.step = Steps-(2 if Steps > 2 else 1)
			self.level -= 1
			self.level_changed = 1
		else:
			self.step = 0

	def weight(self):
		return (ProbStep**(MaxLevel - self.level)) - self.step

	def __hash__(self):
		return hash(self.data)

class Coach(object):

	def __init__(self, data = None):
		self.__log('init')
		self.__wlist = [] #Список изучаемых элементов
		self.nicount = 0
		self.__sum_weight = 0
		self.__wait_list = []
		self.cur_item = None
		self.file_name = None
		self.__new_wlist = [] #Лист ожидания (из него в __wlist)
		self.__items = {}
		if data: self.add(data)

	def add(self, data):
		for i in data:
			item = Item(i)
			if hash(item) not in self.__items:
				self.__new_wlist.append(item)
				self.__items[hash(item)] = item

	def __log(self, str):
		print str

	def __append(self, item):
		if not item.weight(): return
		self.__sum_weight += item.weight()
		self.__wlist.append(item)

	def __new_item(self):
		if not self.__new_wlist:
			return
		self.__log('+1')
		self.nicount += 1
		item = self.__new_wlist.pop(random.randint(0, len(self.__new_wlist)-1))
		self.__append(item)

	def __to_wait(self):
		if self.__wait_list:
			self.__append(self.__wait_list.pop(0))
		self.__wait_list.append(self.cur_item)
		self.cur_item = None

	def __pop(self, pos):
		item = self.__wlist[pos] 
		last = self.__wlist.pop()
		if pos < len(self.__wlist): 
			self.__wlist[pos] = last 
		self.__sum_weight -= item.weight()
		return item

	def __iter__(self):
		if self.cur_item:
			self.__append(self.cur_item);
			self.cur_item = None
		while self.__sum_weight or self.__new_wlist:
			if self.nicount < NewItems:
				self.__new_item()
			r = random.randint(1, self.__sum_weight)
			self.__log('r = %i (%i)' % (r, self.__sum_weight));
			cur_sum = 0
			for n, w in enumerate(self.__wlist):
				cur_sum += w.weight()
				if r <= cur_sum:
					self.cur_item = self.__pop(n)
					yield w.data
					self.__to_wait()
					break

	def __len__(self):
		return len(self.__items)

	def new_count(self):
		return self.nicount

	def studied_count(self):
		return len(self.__wlist) + len(self.__wait_list) + 1 - self.nicount 

	def lesson_count(self):
		return len(self.__items) - len(self.__new_wlist) - self.studied_count() - self.nicount

	def cur_weight(self):
		return self.cur_item.weight()

	def ok(self):
		self.__log('ok')
		self.cur_item.dec()
		if self.cur_item.level_changed and self.cur_item.level == 1:
			self.nicount -= 1

	def error(self):
		self.__log('error')
		self.cur_item.inc()
		if self.cur_item.level_changed and self.cur_item.level == 0:
			self.nicount += 1

def load(file_name):
	if not os.path.exists(file_name):
		return Coach()
	with open(file_name, 'r') as f:
		return pickle.load(f)

def save(file_name, coach):
	with open(file_name, 'w') as f:
		pickle.dump(coach, f)


class Task(object):

	def __init__(self, *prop):
		if len(prop) == 1 and type(prop[0]) is dict:
			for name in ('question', 'ques_descr', 'ques_sound', 'answer', 'description', 'sound'):
				self.__setattr__(name, prop[0][name] if name in prop[0] else '')
		else:
			self.question, self.ques_descr, self.answer, self.description = prop

	def get_list(self):
		return [self.question, self.ques_descr, self.answer, self.description]

	def __eq__(self, answer):
		return self.answer.find(answer) > -1

	def __hash__(self):
		return hash(self.question)


def _test_item():
	item = Item(1)
	while item.weight():
		print 't1-',item.weight(), item.level, item.level_changed
		item.dec()

	item.dec()
	print 't2-', item.weight(), item.level, item.level_changed

	last_weight = -1
	while last_weight != item.weight():
		last_weight = item.weight() 
		item.inc()
		print 't3-', item.weight(), item.level, item.level_changed

def _test_all_ok():
	c = Coach([(x, '', x, '') for x in range(11)])
	for i in c:
		print 't1-', i, c.cur_weight(), c.new_count(), c.studied_count()
		c.ok()

def _test_levelup():
	c = Coach([(x, '', x, '') for x in range(3)])
	it = iter(c)
	x = it.next()
	while c.new_count():
		c.ok()
		print 't2-', x, c.cur_weight(), c.new_count(), c.studied_count()

	c.error()
	print 't2-', x, c.cur_weight(), c.new_count(), c.studied_count()

if __name__ == '__main__':
	_test_levelup()
