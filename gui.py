#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui, uic  # подключает основные модули PyQt

# прототип главной формы
class MainForm(QtGui.QMainWindow):

	def __init__(self, coach):
		super(MainForm, self).__init__()
		uic.loadUi("test.ui", self)

		self.templ = (self.Text.toHtml().toUtf8()).data().decode('utf8')
		self.frame_2.hide()
		self.state = 1


		self.coach = coach
		self.coach_iter = iter(coach)

		self.ok_count = 0
		self.error_count = 0
		self.words_count = 0

		self.setQuestion()
		self.setStat()

		self.connect(self.OkButton, QtCore.SIGNAL("clicked()"),
			self.answerReady)
 
	def setQuestion(self):
		self.task = self.coach_iter.next()
		self.Question.setText(self.task.question)
		self.textEdit.setText(self.task.ques_descr)
		self.Answer.clear()
		self.Answer.setFocus()

	def answerReady(self):
		if self.state:
			ans = self.Answer.text()
			if self.task == ans.toUtf8():
				self.coach.ok()
				self.ok_count += 1
				self.show_ok()
			else:
				self.coach.error()
				self.error_count += 1
				self.show_no()
			self.set_text(self.task.get_list(), self.coach.cur_weight());
			self.frame_2.show()
			self.state = 0
		else:
			self.words_count += 1
			self.setQuestion()
			self.frame_2.hide()
			self.state = 1
		self.setStat();

	def set_text(self, data, status):
		s = self.templ
		for key, val in zip(['Question', 'question_desc', 'Answer', 'answer_desc', 'status'], data+[str(status)]):
			s = s.replace('$%s$' % key, val)
		self.Text.setHtml(s)

	def show_ok(self):
		self.lOk.show()
		self.lNo.hide()

	def show_no(self):
		self.lNo.show()
		self.lOk.hide()
	
	def setStat(self):
		self.tableWidget.item(0, 0).setText(str(self.words_count))
		self.tableWidget.item(0, 1).setText(str(self.ok_count))
		self.tableWidget.item(0, 2).setText(str(self.error_count))
		self.tableWidget.item(0, 3).setText(
				"%i (%i)" % (len(self.coach), 
					len(self.coach) 
					- self.coach.new_count() 
					- self.coach.studied_count()
					- self.coach.lesson_count()
					)
				)
		self.tableWidget.item(0, 4).setText(str(self.coach.new_count()))
		self.tableWidget.item(0, 5).setText(str(self.coach.studied_count()))
		self.tableWidget.item(0, 6).setText(str(self.coach.lesson_count()))


def start(coach):
	app = QtGui.QApplication([])  # создаёт основной объект программы
	form = MainForm(coach)  # создаёт объект формы
	form.show()  # даёт команду на отображение объекта формы и содержимого
	app.exec_()  # запускает приложение
 
