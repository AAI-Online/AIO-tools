from PyQt4 import QtCore, QtGui

class CharacterEditor(QtGui.QWidget):
    def __init__(self):
        super(CharacterEditor, self).__init__()

        layout = QtGui.QHBoxLayout(self)

        soon = QtGui.QLabel(text="Coming soon...")
        soon.setAlignment(QtCore.Qt.AlignCenter)

        layout.addWidget(soon)