import sys

from PyQt4 import QtCore, QtGui

import mainwindow
import config

app = QtGui.QApplication([])
noby = mainwindow.MainWindow()
noby.sucks()
app.exec_()