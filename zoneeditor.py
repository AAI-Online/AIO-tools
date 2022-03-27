from PyQt4 import QtCore, QtGui

class ZoneEditor(QtGui.QWidget):
    def __init__(self):
        super(ZoneEditor, self).__init__()

        layout = QtGui.QHBoxLayout(self)

        soon = QtGui.QLabel(text="Coming soon...")

        layout.addWidget(soon)