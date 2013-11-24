#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
import pickle
import os.path
import re
import time

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
		self.last_update = time.time()

	def dec(self):
		self.last_update = time.time()
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
		self.last_update = time.time()
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
		self.__priority_wlist = [] #Первые в очереди ожидания (из него в __wlist) [используется для синхронизации ru и en словарей]
		self.__new_wlist = [] #Лист ожидания (из него в __wlist)
		self.__items = {}
		if data: self.add(data)

	def debug_print(self):
		print "Debug printing"
		for (key, val) in self.__dict__.iteritems():
			print " ", key, val

	def add(self, data):
		for i in data:
			item = Item(i)
			if hash(item) not in self.__items:
				self.__new_wlist.append(item)
				self.__items[hash(item)] = item

	def delete(self, task):
		self.cur_reset()
		print "try delete " + str(task)
		if hash(task) in self.__items:
			self.__items.pop(hash(task))
			for ar in (self.__priority_wlist, self.__new_wlist):
				for i in range(len(ar)):
					if hash(ar[i].data) == hash(task):
						print "Delete {}".format(task.question)
						ar.pop(i)
						break
			for i in range(len(self.__wlist)):
				if hash(self.__wlist[i].data) == hash(task):
					print "Delete {}".format(task.question)
					item = self.__pop(i)
					if item.level == 0:
						self.nicount -= 1
					break
			for i in range(len(self.__wait_list)):
				if hash(self.__wait_list[i].data) == hash(task):
					print "Delete {}".format(task.question)
					item = self.__wait_list.pop(i)
					if item.level == 0:
						self.nicount -= 1
					break

	def __log(self, str):
		print str

	def __append(self, item):
		if not item.weight(): return
		self.__sum_weight += item.weight()
		self.__wlist.append(item)

	def __new_item(self):
		for new_wlist in (self.__priority_wlist, self.__new_wlist):
			if new_wlist:
				self.__log('+1')
				self.nicount += 1
				item = new_wlist.pop(random.randint(0, len(new_wlist)-1))
				self.__append(item)
				break

	def set_priority(self, brother):
		for (num, item) in enumerate(self.__new_wlist):
			if item in brother and not brother.is_waiting_item(item):
				self.__log('{} move to priority'.format(hash(item))) 
				self.__priority_wlist.append(item)
				self.__new_wlist.pop(num)

	def __contains__(self, item):
		return hash(item) in self.__items

	def is_waiting_item(self, item):
		hitem = hash(item)
		for i in  self.__priority_wlist + self.__new_wlist:
			if hash(i) == hitem:
				return True
		return False

	def __to_wait(self):
		if self.cur_item != None:
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

	def cur_reset(self):
		if self.cur_item:
			self.__append(self.cur_item);
			self.cur_item = None

	def __iter__(self):
		self.cur_reset()
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
		return len(self.__items) - len(self.__priority_wlist) - len(self.__new_wlist) - self.studied_count() - self.nicount

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

	def get_item(self, hash_key):
		return seld.__items[hash_key].data

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
			for name in ('question', 'ques_descr', 'ques_sound', 'answer', 'answer_list', 'description', 'sound'):
				self.__setattr__(name, prop[0][name] if name in prop[0] else '')
			self._hash = prop[0].get('_hash', self.question)
		else:
			self.question, self.ques_descr, self.answer, self.description = prop
			self._hash = self.question
		if hasattr(self, 'answer_list'):
			self.answer_list = [self.answer]

	def get_list(self):
		return [self.question, self.ques_descr, self.answer, self.description]

	def __eq__(self, answer):
		return answer in self.answer_list

	def __hash__(self):
		return hash(self._hash)


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

def _test_del_item():
	data = [Task(i, '', i, '') for i in range(3)]
	c1 = Coach(data)
	i1 = iter(c1)
	items = [i1.next()] # old
	while c1.new_count():
		c1.ok()
	items.append(i1.next()) #new
	items.append(i1.next()) #wait
	task5 = Task(5, '', 5, '') #priority
	c2 = Coach([task5])
	items.append(iter(c2).next())
	c1.add([task5])
	c1.set_priority(c2)
	task6 = Task(6, '', 6, '')
	items.append(task6)
	c1.add([task6, Task(7, '', 7, '')])

	c1.debug_print()
	for i in items:
		c1.delete(i)
	c1.debug_print()


def _test_set_priority():
	data = [Task(i, '', i, '') for i in range(100)]
	c1 = Coach(data)
	c2 = Coach(data)
	i = iter(c1).next()
	c2.set_priority(c1)
	c2.set_priority(c1)
	print hash(iter(c2).next())
	if hash(i) == hash(iter(c2).next()):
		print "ok"

def _test_multianswer():
	data = Task('1', '', '0,1, 2 3,   5', '')
	for i in ('0', '1', '2 3', '5'):
		print i
		if not i == data:
			raise Exception('error on '+i)

if __name__ == '__main__':
	_test_del_item()
#	_test_multianswer()
#	_test_item()
#	_test_set_priority()
