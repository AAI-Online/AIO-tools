from PyQt4 import QtCore, QtGui

import mainwindow

app = QtGui.QApplication([])
noby = mainwindow.MainWindow()
noby.sucks()
app.exec_()