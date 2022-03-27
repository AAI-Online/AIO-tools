from PyQt4 import QtCore, QtGui

import zoneeditor
import charactereditor

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        tabs = QtGui.QTabWidget()

        tab1 = zoneeditor.ZoneEditor()
        tab2 = charactereditor.CharacterEditor()

        tabs.addTab(tab1, "Zone editor")
        tabs.addTab(tab2, "Character editor")

        self.setCentralWidget(tabs)

        self.setWindowTitle("Attorney Investigations Online Tools")

    def sucks(self): # noby
        self.resize(1024, 768)
        self.show()