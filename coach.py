#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
import pickle
import os.path

NewItems = 5
MaxWeight = 100
BarrerNewWord = 90



class Item:
	def __init__(self, d, weight=0):
		self.data = d
		self.weight = weight

class Coach:

	def __init__(self, data = None):
		self.__wlist = []
		self.nicount = 0
		self.__sum_weight = 0
		self.__wait_list = []
		self.cur_item = None
		self.file_name = None
		self.__new_wlist = []
		self.__items = {}
		if data: self.add(data)

	def add(self, data):
		for i in data:
			item = Item(i)
			if hash(item) not in self.__items:
				self.__new_wlist.append(item)
				self.__items[hash(item)] = item
		if self.__items and not self.__wlist:
			self.__log('new')
			self.__new_item()

	def __log(self, str):
		print str

	def __append(self, item):
		if not item.weight: return
		self.__sum_weight += item.weight
		self.__wlist.append(item)

	def __new_item(self):
		if not self.__new_wlist:
			return
		self.__log('+1')
		self.nicount += 1
		item = self.__new_wlist.pop(random.randint(0, len(self.__new_wlist)-1))
		item.weight = MaxWeight
		self.__append(item)

	def __to_wait(self):
		if self.__wait_list:
			self.__append(self.__wait_list.pop(0))
		self.__wait_list.append(self.cur_item)

	def __pop(self, pos):
		item = self.__wlist[pos] 
		last = self.__wlist.pop()
		if pos < len(self.__wlist): 
			self.__wlist[pos] = last 
		self.__sum_weight -= item.weight
		return item

	def __iter__(self):
		while self.__sum_weight:
			if self.nicount < NewItems:
				self.__new_item()
			print self.__wlist
			r = random.randint(1, self.__sum_weight)
			cur_sum = 0
			for n, w in enumerate(self.__wlist):
				cur_sum += w.weight
				if r <= cur_sum:
					self.cur_item = self.__pop(n)
					yield w.data
					self.__to_wait()
					break

	def __len__(self):
		return len(self.__items)

	def new_count(self):
		return self.nicount

	def wcount(self):
		return len(self.__wlist)

	def cur_weight(self):
		return self.cur_item.weight

	def ok(self):
		self.__log('ok')
		self.cur_item.weight -= 1 if self.cur_item.weight > 0 else 0
		if self.cur_item.weight == BarrerNewWord:
			self.nicount -= 1
			self.cur_item.weight = BarrerNewWord / 2

	def error(self):
		self.__log('error')
		self.cur_item.weight += 1
		if self.cur_item.weight == BarrerNewWord + 1:
			self.nicount += 1

def load(file_name):
	if not os.path.exists(file_name):
		return Coach()
	with open(file_name, 'r') as f:
		return pickle.load(f)

def save(file_name, coach):
	with open(file_name, 'w') as f:
		pickle.dump(coach, f)


class Task:

	def __init__(self, *prop):
		self.question, self.ques_descr, self.answer, self.description = prop

	def get_list(self):
		return [self.question, self.ques_descr, self.answer, self.description]

	def __eq__(self, answer):
		return self.answer == answer

	def __hash__(self):
		return self.question


def __main__():
	pass


if __name__ == '__main__':
	__main__()
