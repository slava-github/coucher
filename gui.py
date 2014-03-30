#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from PyQt4 import QtCore, QtGui, uic  # подключает основные модули PyQt
import playmp3


class EditForm(QtGui.QDialog):

    def __init__(self, task):
        super(EditForm, self).__init__()

        self.task = task
        path = os.path.dirname(os.path.abspath(__file__))
        uic.loadUi(path + "/ui/taskEditor.ui", self)

        self.Question.setText(task.question('string'))
        self.QuestDesc.setText(task.question('desc'))
        self.Answer.setText(' | '.join(task.answer('list')))
        self.AnswerDesc.setText(task.answer('desc'))

    def accept(self):
        self.task.question('string', str(self.Question.text().toUtf8()).decode('utf8'))
        self.task.question('desc', str(self.QuestDesc.toPlainText().toUtf8()).decode('utf8'))
        self.task.answer('list', str(self.Answer.text().toUtf8()).decode('utf8').split(' | '))
        self.task.answer('desc', str(self.AnswerDesc.toPlainText().toUtf8()).decode('utf8'))
        super(EditForm, self).accept()


class MainForm(QtGui.QDialog):
    task = None
    sound = None

    def __init__(self, coach):
        super(MainForm, self).__init__()
        self.path = os.path.dirname(os.path.abspath(__file__))
        uic.loadUi(self.path + "/ui/test.ui", self)

        self.templ = (self.Text.toHtml().toUtf8()).data().decode('utf8')
        self.frame_2.hide()
        self.LNew.hide()
        self.state = 1

        self.coach = coach
        self.coach_iter = iter(coach)

        self.ok_count = 0
        self.error_count = 0
        self.words_count = 0

        self.setQuestion()
        self.setStat()

        self.connect(self.TEdit, QtCore.SIGNAL("clicked()"), self.taskEdit)

        self.connect(self.OkButton, QtCore.SIGNAL("clicked()"), self.answerReady)

        self.connect(self.DeleteButton, QtCore.SIGNAL("clicked()"), self.deleteItem)

        self.connect(self.PlayButton, QtCore.SIGNAL("clicked()"), self.PlaySound)

    def setQuestion(self):
        self.task = self.coach_iter.next()
        self.statusbar.showMessage(self.coach.info)
        self.taskUpdated()
        self.Answer.clear()
        self.Answer.setFocus()
        self.setSound('question')
        if self.coach.cur_isNew():
            self.LNew.show()
        else:
            self.LNew.hide()

    def answerReady(self):
        if self.state:
            ans = self.Answer.text()
            if self.task == ans.toUtf8().data().decode('utf8').lower():
                self.coach.ok()
                self.ok_count += 1
                self.show_ok()
            else:
                self.coach.error()
                self.error_count += 1
                self.show_no()
            self.Status.setText(str(self.coach.cur_weight()))
            self.frame_2.show()
            self.setSound('answer')
            self.state = 0
        else:
            self.words_count += 1
            self.setQuestion()
            self.frame_2.hide()
            self.state = 1
        self.setStat()

    def setSound(self, field):
        self.sound = self.task.sound(field)
        if self.sound:
            self.PlayButton.show()
        else:
            self.PlayButton.hide()

    def PlaySound(self):
        if self.sound:
            playmp3.play(self.sound)

    def deleteItem(self):
        print 'gui try delete task: ' + str(hash(self.task))
        self.coach.delete(self.task)
        if self.state:
            self.setQuestion()
            self.setStat()
        else:
            self.answerReady()

    def show_ok(self):
        self.lOk.show()
        self.lNo.hide()

    def show_no(self):
        self.lNo.show()
        self.lOk.hide()

    def taskUpdated(self):
        self.Question.setText(self.task.question('string'))
        self.Question.home(False)
        self.textEdit.setText(self.task.question('desc'))
        data = self.task.get_list()
        data[2] = ', '.join(data[2])
        s = self.templ
        for key, val in zip(['Question', 'question_desc', 'Answer', 'answer_desc'], data):
            s = s.replace('$%s$' % key, val.replace('\n', "<br>"))
        self.Text.setHtml(s)

    def setStat(self):
        self.tableWidget.item(0, 0).setText(str(self.words_count))
        self.tableWidget.item(0, 1).setText(str(self.ok_count))
        self.tableWidget.item(0, 2).setText(str(self.error_count))
        self.tableWidget.item(0, 3).setText(
            "%i (%i)" % (
                len(self.coach),
                len(self.coach)
                - self.coach.new_count()
                - self.coach.studied_count()
                - self.coach.lesson_count()
            )
        )
        self.tableWidget.item(0, 4).setText(str(self.coach.new_count()))
        self.tableWidget.item(0, 5).setText(str(self.coach.studied_count()))
        self.tableWidget.item(0, 6).setText(str(self.coach.lesson_count()))

    def taskEdit(self):
        edit_form = EditForm(self.task)
        edit_form.exec_()
        if edit_form.result():
            self.taskUpdated()


def main(coach):
    app = QtGui.QApplication([])
    form = MainForm(coach)
    form.show()
    app.exec_()
