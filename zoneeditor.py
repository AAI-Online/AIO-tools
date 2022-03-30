import os
from functools import partial

from PyQt4 import QtCore, QtGui

import config


class ZoneSceneView(QtGui.QGraphicsView):
    def __init__(self, scene):
        super(ZoneSceneView, self).__init__(scene)
        self.scene = scene
        self.setMouseTracking(True)
        self.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.gray))
        self.Scale = 1

    @QtCore.pyqtSlot()
    def zoomIn(self):
        self.Scale += 1
        self.scale(2, 2)

    @QtCore.pyqtSlot()
    def zoomOut(self):
        self.Scale -= 1
        if self.Scale <= 0:
            self.Scale = 1
            return False
        self.scale(0.5, 0.5)
        return True

class ZoneEditor(QtGui.QWidget):
    def __init__(self):
        super(ZoneEditor, self).__init__()

        self.changes = False

        layout = QtGui.QHBoxLayout(self)
        leftlayout = QtGui.QVBoxLayout()
        leftlayout.setAlignment(QtCore.Qt.AlignTop)
        rightlayout = QtGui.QVBoxLayout()
        rightlayout.setAlignment(QtCore.Qt.AlignTop)

        ######### left layout #########
        # zone list
        self.zonelist = QtGui.QListWidget()
        self.zonelist.setMaximumSize(200, 300)
        self.zonelist.setMinimumSize(200, 300)
        self.zonelist.itemDoubleClicked.connect(self.onClickZoneItem)
        self.refreshZoneList()

        # tool layout
        toollayout = QtGui.QGridLayout()
        toollayout.setAlignment(QtCore.Qt.AlignLeft)
        toollayout.setHorizontalSpacing(2)
        toollayout.setVerticalSpacing(2)

        # select tool
        self.selecttool = QtGui.QPushButton()
        self.selecttool.setMaximumSize(32,32)
        self.selecttool.setToolTip("Selection tool")
        selecttoolicn = QtGui.QIcon(QtGui.QPixmap("img/tool-select.png"))
        self.selecttool.setIcon(selecttoolicn)
        self.selecttool.setIconSize(selecttoolicn.availableSizes()[0])
        self.selecttool.setCheckable(True)
        self.selecttool.toggled.connect(partial(self.onClickTool, 0))
        # line tool
        self.linetool = QtGui.QPushButton()
        self.linetool.setMaximumSize(32,32)
        self.linetool.setToolTip("Draw collision line tool")
        linetoolicn = QtGui.QIcon(QtGui.QPixmap("img/tool-line.png"))
        self.linetool.setIcon(linetoolicn)
        self.linetool.setIconSize(linetoolicn.availableSizes()[0])
        self.linetool.setCheckable(True)
        self.linetool.toggled.connect(partial(self.onClickTool, 1))
        # all tools for use on the onClickTool slot
        self.tools = [self.selecttool, self.linetool]


        ######### right layout #########
        # zone view
        self.scene = QtGui.QGraphicsScene(0, 0, 1, 1)
        self.view = ZoneSceneView(self.scene)
        self.zonebg = None # qgraphicspixmapitem
        
        # some tools (zoom, etc)
        zonetoollayout = QtGui.QHBoxLayout()
        # zoom in
        self.zoomInbtn = QtGui.QPushButton()
        self.zoomInbtn.setMaximumSize(32,32)
        self.zoomInbtn.setToolTip("Zoom in")
        zoominicn = QtGui.QIcon(QtGui.QPixmap("img/zoom-in.png"))
        self.zoomInbtn.setIcon(zoominicn)
        self.zoomInbtn.setIconSize(zoominicn.availableSizes()[0])
        self.zoomInbtn.clicked.connect(self.view.zoomIn)
        # zoom out
        self.zoomOutbtn = QtGui.QPushButton()
        self.zoomOutbtn.setMaximumSize(32,32)
        self.zoomOutbtn.setToolTip("Zoom out")
        zoomouticn = QtGui.QIcon(QtGui.QPixmap("img/zoom-out.png"))
        self.zoomOutbtn.setIcon(zoomouticn)
        self.zoomOutbtn.setIconSize(zoomouticn.availableSizes()[0])
        self.zoomOutbtn.clicked.connect(self.view.zoomOut)

        ## left side layout: ##
        # add tools to tool layout
        toollayout.addWidget(self.selecttool, 0, 0)
        toollayout.addWidget(self.linetool, 0, 1)
        # add tool layout to left layout
        leftlayout.addWidget(self.zonelist)
        leftlayout.addLayout(toollayout)

        ## right side layout: ##
        # add tools below zone view to a layout
        zonetoollayout.setAlignment(QtCore.Qt.AlignLeft)
        zonetoollayout.addWidget(self.zoomInbtn)
        zonetoollayout.addWidget(self.zoomOutbtn)
        # add zone view and some tool buttons to right layout
        rightlayout.addWidget(self.view)
        rightlayout.addLayout(zonetoollayout)
        # add left & right layouts to the final main layout
        layout.addLayout(leftlayout)
        layout.addLayout(rightlayout)

        self.onClickTool(0, True) # default to the select tool

    def refreshZoneList(self):
        self.zonelist.clear()
        for f in os.listdir(config.datadir+"/zones"):
            if os.path.isdir(config.datadir+"/zones/"+f):
                self.zonelist.addItem(f)
        self.zonelist.sortItems()

    def loadZone(self, name):
        if os.path.isdir(config.datadir+"/zones/"+name):
            if self.changes:
                pass
            if self.zonebg: self.scene.removeItem(self.zonebg)
            self.zonebg = QtGui.QGraphicsPixmapItem(scene=self.scene)
            pixmap = QtGui.QPixmap(config.datadir+"/zones/"+name+"/zone.png")
            self.zonebg.setPixmap(pixmap)
            self.zonebg.setZValue(-10000)
            self.scene.setSceneRect(0, 0, pixmap.size().width(), pixmap.size().height())
            while self.view.zoomOut(): pass

    @QtCore.pyqtSlot("int", "bool")
    def onClickTool(self, ind, toggled):
        for tool in self.tools:
            tool.blockSignals(True)
            tool.setChecked(self.tools[ind] == tool)
            tool.blockSignals(False)

    @QtCore.pyqtSlot("QListWidgetItem")
    def onClickZoneItem(self, item):
        self.loadZone(item.text())