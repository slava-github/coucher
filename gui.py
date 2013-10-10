#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui, uic  # подключает основные модули PyQt

class Dialog(QtGui.QDialog):

	def __init__(self):
		super(Dialog, self).__init__()
		uic.loadUi("answer.ui", self)
		self.templ = (self.Text.toHtml().toUtf8()).data().decode('utf8')

	def set_text(self, data):
		s = self.templ
		for key, val in zip([u'Question', u'question_desc', u'Answer', u'answer_desc'], data):
			s = s.replace('$%s$' % key, val)
		self.Text.setHtml(s)

	def show_ok(self):
		self.lOk.show()
		self.lNo.hide()
		self.show()

	def show_no(self):
		self.lNo.show()
		self.lOk.hide()
		self.show()

# прототип главной формы
class MainForm(QtGui.QMainWindow):

	def __init__(self, coach):
		super(MainForm, self).__init__()
		uic.loadUi("test.ui", self)

		self.DAnswer = Dialog()

		self.coach = coach
		self.coach_iter = iter(coach)

		self.ok_count = 0
		self.error_count = 0
		self.words_count = 0

		self.setStat()
		self.setQuestion()

		self.connect(self.OkButton, QtCore.SIGNAL("clicked()"),
			self.answerReady)
 
	def setQuestion(self):
		self.task = self.coach_iter.next()
		self.Question.setText(self.task.question)
		self.textEdit.setText(self.task.ques_descr)
		self.Answer.clear()
		self.Answer.setFocus()

	def answerReady(self):
		self.DAnswer.set_text(self.task.get_list());
		ans = self.Answer.text()
		if self.task == ans.toUtf8():
			self.coach.ok()
			self.ok_count += 1
			self.DAnswer.show_ok()
		else:
			self.coach.error()
			self.error_count += 1
			self.DAnswer.show_no()
		self.words_count += 1
		self.setStat();
		self.setQuestion()
	
	def setStat(self):
		self.tableWidget.item(0, 0).setText(str(self.words_count))
		self.tableWidget.item(0, 1).setText(str(self.ok_count))
		self.tableWidget.item(0, 2).setText(str(self.error_count))
		self.tableWidget.item(0, 3).setText(str(len(self.coach)))
		self.tableWidget.item(0, 4).setText(str(self.coach.new_count()))
		self.tableWidget.item(0, 5).setText(str(self.coach.wcount()))


def start(coach):
	app = QtGui.QApplication([])  # создаёт основной объект программы
	form = MainForm(coach)  # создаёт объект формы
	form.show()  # даёт команду на отображение объекта формы и содержимого
	app.exec_()  # запускает приложение
 
