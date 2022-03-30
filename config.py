import os
import sys
from ConfigParser import ConfigParser

from PyQt4 import QtGui


def findDataDirectory():
    folder = str(QtGui.QFileDialog.getExistingDirectory(None, "Find the Attorney Investigations Online \"data\" folder, then click 'Select folder'", "."))
    if folder:
       if os.path.exists(folder+"/characters") and\
          os.path.exists(folder+"/zones") and\
          os.path.exists(folder+"/themes") and\
          os.path.exists(folder+"/evidence") and\
          os.path.exists(folder+"/sounds"):
            return folder

       QtGui.QMessageBox(QtGui.QMessageBox.Critical, "Data folder", "%s\nis not a valid Attorney Investigations Online data folder." % folder).exec_()
       return ""

    QtGui.QMessageBox(QtGui.QMessageBox.Critical, "Data folder", "No folder specified.").exec_()
    return ""

def getDataDirectory():
    f = ConfigParser()
    if not f.read("AIO-tools.ini"): # file does not exist
        QtGui.QMessageBox(QtGui.QMessageBox.Information, "First run", "Hey! This is the first time you open AIO-tools.\nPlease point me to your Attorney Investigations Online \"data\" folder.").exec_()
        folder = findDataDirectory()

        if folder:
            f.add_section("General")
            f.set("General", "data_path", folder)
            f.write(open("AIO-tools.ini", "w"))
        return folder

    return f.get("General", "data_path")


datadir = getDataDirectory()
if not datadir:
    sys.exit(-3)
