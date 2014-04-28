#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
import os
import sys
import pickle
import time

NEW_ITEMS = 5
QUEUES = 3
MAX_WEIGHT = 5


class MaxWeight(Exception):
    pass


class MinWeight(Exception):
    pass


class ROStatus(Exception):
    pass


class Item(object):
    """
    >>> i = Item(5)
    >>> i.data, i.weight() == MAX_WEIGHT
    (5, True)
    >>> i == 5
    True

    >>> i.dec(2)
    >>> i.weight() == MAX_WEIGHT - 2
    True

    >>> i.inc()
    >>> i.weight() == MAX_WEIGHT - 1
    True

    >>> try: i.inc(2);
    ... except MaxWeight: "MaxWeight", i.weight() == MAX_WEIGHT - 1
    ('MaxWeight', True)

    >>> while i.weight():
    ...   i.dec()
    >>> try: i.dec();
    ... except MinWeight: "MinWeight", i.weight() == 0
    ('MinWeight', True)
    """

    def __init__(self, data, weight=MAX_WEIGHT, max_weight=MAX_WEIGHT):
        self.data = data
        self.__weight = weight
        self.__max_weight = max_weight
        self.owner = None
        self.last_update = time.time()

    def weight(self):
        return self.__weight

    def max_weight(self):
        return self.__max_weight

    def inc(self, i=1):
        if self.__weight + i > self.__max_weight:
            raise MaxWeight
        self.__weight += i
        self.last_update = time.time()
        if self.owner:
            self.owner.inc_sum_weight(i)

    def dec(self, i=1):
        if self.__weight - i < 0:
            raise MinWeight()
        self.__weight -= i
        self.last_update = time.time()
        if self.owner:
            self.owner.dec_sum_weight(i)

    def __eq__(self, value):
        return self.data == value

    def __hash__(self):
        return hash(self.data)


class Queue():
    """
    >>> q = Queue()

    >>> i = Item(1)
    >>> q.append(i)
    >>> q.sum_weight() == MAX_WEIGHT, q[0].data, len(q)
    (True, 1, 1)
    >>> i.dec()
    >>> q.sum_weight() == MAX_WEIGHT-1
    True
    >>> i.inc()
    >>> q.sum_weight() == MAX_WEIGHT
    True

    >>> q.append([Item(2), Item(3)])
    >>> q.sum_weight() == MAX_WEIGHT*3, q[1].data, q[2].data, len(q)
    (True, 2, 3, 3)

    >>> q.index(MAX_WEIGHT), q.index(MAX_WEIGHT+MAX_WEIGHT/2), q.index(MAX_WEIGHT*3)
    (0, 1, 2)

    >>> try:
    ...   q.index(MAX_WEIGHT*3+1)
    ... except IndexError:
    ...   "IndexError"
    'IndexError'

    >>> q.find_by_value(2)
    1
    >>> i = q.pop(1)
    >>> i.data, q.sum_weight() == MAX_WEIGHT*2, len(q)
    (2, True, 2)

    >>> del q[1]
    >>> q.sum_weight() == MAX_WEIGHT, len(q)
    (True, 1)
    """

    def __init__(self, data=None):
        self.__items = []
        self.__sum_weight = 0
        if data is not None:
            self.append(data)

    def __delitem__(self, index):
        item = self.__items[index]
        last = self.__items.pop()
        if index < len(self.__items):
            self.__items[index] = last
        self.__sum_weight -= item.weight()

    def __getitem__(self, index):
        return self.__items[index]

    def __len__(self):
        return len(self.__items)

    def sum_weight(self):
        return self.__sum_weight

    def inc_sum_weight(self, i=1):
        self.__sum_weight += i

    def dec_sum_weight(self, i=1):
        self.__sum_weight -= i

    def index(self, windex):
        cur_sum = 0
        for n, v in enumerate(self.__items):
            cur_sum += v.weight()
            if windex <= cur_sum:
                return n
        raise IndexError

    def find_by_value(self, value):
        for n, v in enumerate(self.__items):
            if v == value:
                return n

    def append(self, item):
        if type(item) is Item:
            item = [item]
        elif type(item) is not list:
            raise TypeError("Expected type Item or List")
        for i in item:
            i.owner = self
            self.__items.append(i)
            self.__sum_weight += i.weight()

    def pop(self, index):
        item = self.__items[index]
        del self[index]
        item.owner = None
        return item


class Coach(object):

    def __init__(self, data=None, limit_new_items=NEW_ITEMS):
        self._log('init')
        self.info = ''
        self.__new_count = 0
        self.limit_new_items = limit_new_items
        self.__items = {}
        self.__wait_list = [[], []]
        self.__queues = Queue([Item(Queue(), 0, 5 ** i) for i in range(QUEUES - 1, -1, -1)] + [Item(Queue(), 0, 0)])
        self.__deferred = []
        self.__oppinut = self.__queues[-1].data
        self.__cur_item = None
        self.__cur_queue_index = None
        self.__cur_new = 0
        self.__test = 1
        self.file_name = None
        if data:
            self.add(data)

    def __contains__(self, item):
        return hash(item) in self.__items

    def _log(self, mess):
        print >> sys.stderr, mess

    def __add_in_queue(self, item, index):
        queue = self.__queues[index]
        queue.data.append(item)
        if (not queue.weight()):
            queue.inc(queue.max_weight())

    def _correct_queues_weight(self):
        for item in self.__queues:
            if len(item.data):
                if len(item.data) < 4:
                    item.dec(item.weight() - int(item.max_weight() * len(item.data) / 4.0))
                elif item.weight() < item.max_weight():
                    item.inc(item.max_weight() - item.weight())
                return

    def __new_item(self):
        for _list in reversed(self.__wait_list):
            if _list:
                self._log('+1')
                self.__cur_new = 1
                self.__new_count += 1
                item = _list.pop(random.randint(0, len(_list) - 1))
                return item

    def cur_reset(self):
        if self.__cur_item:
            self.__add_in_queue(self.__cur_item, self.__cur_queue_index)
            self.__cur_item = None
            self.__cur_queue_index = None
            self.__cur_new = 0

    def __to_deferred(self):
        if self.__cur_item is not None:
            if self.__deferred:
                ar = self.__deferred.pop(0)
                self.__add_in_queue(ar[0], ar[1])
            if self.__queues.sum_weight():
                self.__deferred.append([self.__cur_item, self.__cur_queue_index])
                self.__cur_item = None
                self.__cur_queue_index = None
                self.__cur_new = 0

    def __pop(self, qitem, index):
        item = qitem.data.pop(index)
        if qitem.data.sum_weight() == 0:
            qitem.dec(qitem.weight())
        return item

    def __iter__(self):
        self.cur_reset()
        while (len(self.__oppinut) < len(self.__items)) or sum(len(i) for i in self.__wait_list):
            if self.__new_count < self.limit_new_items:
                self.__cur_queue_index = 0
                self.__cur_item = self.__new_item()

            if not self.__cur_item:
                self._correct_queues_weight()
                r = random.randint(1, self.__queues.sum_weight())
                self.info = s = 'qr = %i (%i)' % (r, self.__queues.sum_weight())
                self._log(s)
                self.__cur_queue_index = self.__queues.index(r)
                qitem = self.__queues[self.__cur_queue_index]

                r = random.randint(1, qitem.data.sum_weight())
                s = 'r = %i (%i)' % (r, qitem.data.sum_weight())
                self.info = self.info + ' ' + s
                self._log(s)
                i = qitem.data.index(r)
                self.__cur_item = self.__pop(qitem, i)

            yield self.__cur_item.data
            self.__to_deferred()
            self.cur_reset()

    def add(self, data):
        for i in data if type(data) is list else [data]:
            item = Item(i)
            if hash(item) not in self.__items:
                self.__wait_list[0].append(item)
                self.__items[hash(item)] = item

    def ok(self):
        self._log('ok')
        self.__cur_item.dec()
        if not self.__cur_item.weight():
            if self.__cur_queue_index < len(self.__queues) - 1:
                self.__cur_item.inc(self.__cur_item.max_weight())
                self.__cur_queue_index += 1
                self._log("next queue")
                if self.__cur_queue_index == 1:
                    self.__new_count -= 1
            else:
                self.__cur_item.inc()

    def error(self):
        self._log('error')
        if self.__cur_queue_index:
            self.__new_count += 1
        self.__cur_queue_index = 0
        self.__cur_item.inc(self.__cur_item.max_weight() - self.__cur_item.weight())

    def __len__(self):
        return len(self.__items)

    def new_count(self):
        return self.__new_count

    def studied_count(self):
        return len(self.__items) \
            - self.__new_count \
            - len(self.__oppinut) \
            - sum(len(i) for i in self.__wait_list)

    def lesson_count(self):
        return len(self.__oppinut)

    def cur_weight(self):
        return self.__cur_item.weight() + (len(self.__queues) - 2 - self.__cur_queue_index) * MAX_WEIGHT

    def cur_item(self):
        return self.__cur_item.data

    def cur_isNew(self):
        return self.__cur_new

    def items(self):
        return self.__items

    def is_waiting_item(self, item):
        hitem = hash(item)
        for i in self.__wait_list[0] + self.__wait_list[1]:
            if hash(i) == hitem:
                return True
        return False

    def set_priority(self, brother):
        for (num, item) in enumerate(self.__wait_list[0]):
            if item in brother and not brother.is_waiting_item(item):
                self._log('{} move to priority'.format(hash(item)))
                self.__wait_list[1].append(item)
                self.__wait_list[0].pop(num)

    def delete(self, task):
        self.cur_reset()
        self._log(u"try delete " + str(task))
        if hash(task) in self.__items:
            self.__items.pop(hash(task))
            for (iq, q) in enumerate(self.__queues):
                for (i, d) in enumerate(q.data):
                    if d == task:
                        self._log(u"Delete from queues {}".format(task.question))
                        self.__pop(q, i)
                        if iq == 0:
                            self.__new_count -= 1
                        return
            for (i, d) in enumerate(self.__deferred):
                if d[0] == task:
                    self._log(u"Delete from deferred {}".format(task.question))
                    self.__deferred.pop(i)
                    if d[1] == 0:
                        self.__new_count -= 1
                    return
            for l in self.__wait_list:
                for (i, d) in enumerate(l):
                    if d == task:
                        self._log(u"Delete from wait_list {}".format(task.question))
                        l.pop(i)
                        return


def load(file_name):
    if not os.path.exists(file_name):
        return Coach()
    with open(file_name, 'r') as f:
        return pickle.load(f)


def save(file_name, coach):
    with open(file_name, 'w') as f:
        pickle.dump(coach, f)


class Task(object):
#
#question
#    string
#    desc
#    sound
#answer
#    list
#    desc
#    sound
#
    def __init__(self, *prop):
        if len(prop) == 1 and type(prop[0]) is dict:
            self.data = prop
            if 'hash' is prop:
                self._hash = prop.pop('hash')
            else:
                self._hash = prop['question']['string']
        else:
            self.data = {
                'question': {
                    'string': prop[0],
                    'desc': prop[1],
                },
                'answer': {
                    'list': prop[2],
                    'desc': prop[3]
                }
            }
            self._hash = prop[0]
        if type(self.data['answer']['list']) is not list:
            self.data['answer']['list'] = [self.data['answer']['list']]
        self.norm_answer = None
        self.normalize_answer()

    def get(self, key, name):
        return self.data[key][name]

    def set(self, key, name, val):
        self.data[key][name] = val
        if (key, name) == ('answer', 'list'):
            self.normalize_answer()

    def question(self, key, data=None):
        if data is not None:
            self.set('question', key, data)
        else:
            return self.get('question', key)

    def answer(self, key, data=None):
        if data is not None:
            self.set('answer', key, data)
            if key == 'list':
                self.normalize_answer()
        else:
            return self.get('answer', key)

    def sound(self, key):
        try:
            return self.get(key, 'sound')
        except KeyError:
            return None

    def get_list(self):
        return [
            self.question('string'),
            self.question('desc'),
            self.answer('list'),
            self.answer('desc')
        ]

    def __eq__(self, answer):
        return answer in self.norm_answer

    def __hash__(self):
        return hash(self._hash)

    def normalize_answer(self):
        addition = []
        for w in self.answer('list'):
            if type(w) in (str, unicode) and w.find(u'ё') > -1:
                addition.append(w.replace(u'ё', u'е'))
        self.norm_answer = self.answer('list') + addition

import unittest


class CoachTestCase(unittest.TestCase):
    def testOneNew(self):
        _list = [1, 2, 3]
        c = Coach(_list, 1)
        self.assertEqual(len(c), len(_list))
        i = iter(c)
        data = next(i)
        self.assertIn(data, _list)
        self.assertEqual(next(i), data)

    def testNew(self):
        _list = [1, 2, 3]
        c = Coach(_list)
        old = []
        i = iter(c)
        for n in range(3):
            item = next(i)
            self.assertEqual(c.new_count(), n + 1)
            self.assertEqual(c.cur_isNew(), 1)
            self.assertIn(item, _list)
            self.assertNotIn(item, old)
            old.append(item)

    def testAllOk(self):
        _list = [1]
        c = Coach(_list)
        self.assertEqual(len(c), 1)
        _iter = iter(c)
        next(_iter)
        self.assertEqual(c.new_count(), 1)
        self.assertEqual(c.studied_count(), 0)
        self.assertEqual(c.cur_weight(), MAX_WEIGHT * QUEUES)
        for _ in range(MAX_WEIGHT - 1):
            c.ok()
        self.assertEqual(c.new_count(), 1)
        c.ok()
        self.assertEqual(c.new_count(), 0)
        self.assertEqual(c.studied_count(), 1)
        self.assertEqual(c.cur_weight(), MAX_WEIGHT * (QUEUES - 1))
        next(_iter)
        for _ in range((MAX_WEIGHT) * (QUEUES - 1) - 1):
            c.ok()
        next(_iter)
        c.ok()
        self.assertEqual(c.cur_weight(), 0)
        with self.assertRaises(StopIteration):
            next(_iter)
        self.assertEqual(c.lesson_count(), 1)
        self.assertEqual(c.studied_count(), 0)

    def testError(self):
        _list = [1]
        c = Coach(_list)
        for weight in range(1, MAX_WEIGHT * QUEUES):
            _iter = iter(c)
            next(_iter)
            for _ in range(MAX_WEIGHT * QUEUES - weight):
                c.ok()
            next(_iter)
            c.error()
            self.assertEqual(c.new_count(), 1)
            self.assertEqual(c.cur_weight(), MAX_WEIGHT * QUEUES)

    def testPrior(self):
        _list = range(100)
        c1 = Coach(_list)
        c2 = Coach(_list)
        i = next(iter(c1))
        c2.set_priority(c1)
        self.assertEqual(next(iter(c2)), i)
        c2.set_priority(c1)
        self.assertNotEqual(next(iter(c2)), i)
        c1 = Coach([101])
        i = next(iter(c1))
        c2.set_priority(c1)
        self.assertNotEqual(next(iter(c2)), i)

    def testDelItem(self):
        data = [Task(i, '', i, '') for i in range(3)]
        c1 = Coach(data)
        i1 = iter(c1)
        items = [i1.next()]  # old
        while c1.new_count():
            c1.ok()
        items.append(i1.next())  # new
        items.append(i1.next())  # wait

        task5 = Task(5, '', 5, '')  # priority
        c2 = Coach([task5])
        items.append(iter(c2).next())
        c1.add([task5])
        c1.set_priority(c2)

        items.append(Task(6, '', 6, ''))
        task7 = Task(7, '', 7, '')
        c1.add([task7, items[-1]])

        for i in items:
            c1.delete(i)
        self.assertEqual(len(c1), 1)
        self.assertEqual(c1.new_count(), 0)
        self.assertEqual([i1.next(), i1.next()], [task7, task7])

    def testDecWeightQueue(self):
        pass
"""
        c = Coach()
        for i in range(1, QUEUES + 1):
            c.add(i)
            print "--", c._queues.sum_weight()
            iter(c).next()
            for _ in range((QUEUES - i) * MAX_WEIGHT):
                c.ok()
            print c.cur_weight()
"""

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False)
    unittest.main()
