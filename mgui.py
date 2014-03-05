#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui, uic  # подключает основные модули PyQt

class MainForm(QtGui.QDialog):

	def __init__(self):
		super(MainForm, self).__init__()
		uic.loadUi("ui/multilanguage.ui", self)
#		self.form.setAttribute(QtCore.Qt.WA_DeleteOnClose, 0);

	def exec_(self):
		super(MainForm, self).exec_()
		return self.result()

	def result(self):
		if super(MainForm, self).result():
			for (class_, result) in ((self.verbs, 'verbs'), (self.ru, 'ru'), (self.en, 'en')):
				if class_.isChecked():
					return result

def main():
	app = QtGui.QApplication([])
	form = MainForm()
	form.show()
	app.exec_()
	return self.form.result()


if __name__ == '__main__':
	print main()
