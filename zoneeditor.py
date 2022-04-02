import os
import math
from functools import partial

from PyQt4 import QtCore, QtGui

import config

lineRadius = 2
ITEM_LINE = 0
ITEM_FG = 1
ITEM_SPAWN = 2
ITEM_RECT = 3


class ZoneSceneView(QtGui.QGraphicsView):
    def __init__(self, scene, parent):
        super(ZoneSceneView, self).__init__(scene)
        self.scene = scene
        self.parent = parent
        self.setMouseTracking(True)
        self.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.gray))
        self.Scale = 1
        self.mousePrev = False
        self.objects = []
        self.linePreview = None
        self.selected = None
        self.moveSteps = 10
        self.keysDown = set()

    def snapToLine(self, pos, ignore=None):
        if QtCore.Qt.Key_Alt in self.keysDown: return # don't snap
        
        for obj in self.objects:
            if obj["obj"] == ignore: continue

            if obj["type"] == ITEM_LINE:
                x1 = obj["obj"].x()
                y1 = obj["obj"].y()
                x2 = x1 + obj["obj"].line().x2()
                y2 = y1 + obj["obj"].line().y2()
                if pos.x() >= x1-lineRadius and pos.x() <= x1+lineRadius and pos.y() >= y1-lineRadius and pos.y() <= y1+lineRadius:
                    pos.setX(x1)
                    pos.setY(y1)
                elif pos.x() >= x2-lineRadius and pos.x() <= x2+lineRadius and pos.y() >= y2-lineRadius and pos.y() <= y2+lineRadius:
                    pos.setX(x2)
                    pos.setY(y2)

    def lineToItemPos(self, lineItem): # convert line x1,y1,x2,y2 to qgraphicsitem position & width
        line = lineItem.line()
        if line.x1() == 0 and line.y1() == 0: return # already done

        x1 = line.x1()
        x2 = line.x2()
        y1 = line.y1()
        y2 = line.y2()

        lineItem.setPos(x1, y1)
        line.setP1(QtCore.QPointF(0, 0))
        line.setP2(QtCore.QPointF(x2-x1, y2-y1))
        lineItem.setLine(line)

    def addLine(self, line):
        self.lineToItemPos(line)
        self.objects.append({"type": ITEM_LINE, "obj": line, "angle": line.line().angle(), "rect": None})
        self.parent.changes = True

    def deselect(self):
        if self.selected:
            pen = self.selected["rect"].pen()
            pen.setColor(QtCore.Qt.red)
            self.selected["rect"].setPen(pen)
            self.selected = None

    def keyPressEvent(self, event):
        if not event.isAutoRepeat():
            self.keysDown.add(event.key())

    def keyReleaseEvent(self, event):
        if not event.isAutoRepeat():
            self.keysDown.remove(event.key())

    def mousePressEvent(self, event):
        pos = self.mapToScene(event.pos())
        if event.button() == QtCore.Qt.LeftButton:
            if self.parent.currtool == 0: # select
                self.deselect()

                for obj in self.objects:
                    if obj["type"] == ITEM_LINE:
                        x1 = obj["obj"].x()
                        y1 = obj["obj"].y()
                        x2 = x1 + obj["obj"].line().x2()
                        y2 = y1 + obj["obj"].line().y2()
                        if pos.x() >= x1-lineRadius and pos.x() <= x1+lineRadius and pos.y() >= y1-lineRadius and pos.y() <= y1+lineRadius:
                            pen = obj["rect"].pen()
                            pen.setColor(QtCore.Qt.green)
                            obj["rect"].setPen(pen)
                            self.selected = {"moveType": ITEM_LINE, "type": obj["type"], "obj": obj["obj"], "line": obj["obj"].line(), "linePoint": 1, "rect": obj["rect"]}
                            self.moveSteps = 10
                            break
                        elif pos.x() >= x2-lineRadius and pos.x() <= x2+lineRadius and pos.y() >= y2-lineRadius and pos.y() <= y2+lineRadius:
                            pen = obj["rect"].pen()
                            pen.setColor(QtCore.Qt.green)
                            obj["rect"].setPen(pen)
                            self.selected = {"moveType": ITEM_LINE, "type": obj["type"], "obj": obj["obj"], "line": obj["obj"].line(), "linePoint": 2, "rect": obj["rect"]}
                            self.moveSteps = 10
                            break

                    if pos.x() >= obj["rect"].x() and pos.y() >= obj["rect"].y() and pos.x() <= obj["rect"].x() + obj["rect"].rect().width() and pos.y() <= obj["rect"].y() + obj["rect"].rect().height(): # ordinary object
                        pen = obj["rect"].pen()
                        pen.setColor(QtCore.Qt.green)
                        obj["rect"].setPen(pen)
                        self.selected = {"moveType": ITEM_RECT, "type": obj["type"], "obj": obj["obj"], "rect": obj["rect"]}
                        self.moveSteps = 10
                        break

            elif self.parent.currtool == 1: # draw line
                if self.linePreview: self.scene.removeItem(self.linePreview)
                self.linePreview = QtGui.QGraphicsLineItem(QtCore.QLineF(round(pos.x()), round(pos.y()), round(pos.x()), round(pos.y())), scene=self.scene)
                pen = self.linePreview.pen()
                pen.setWidth(1)
                pen.setCosmetic(False)
                self.linePreview.setPen(pen)

    def mouseMoveEvent(self, event):
        pos = self.mapToScene(event.pos())
        if self.parent.currtool == 0: # select tool
            if self.selected:
                if self.moveSteps > 0:
                    self.moveSteps -= 1
                    return

                if self.selected["moveType"] == ITEM_RECT:
                    self.selected["obj"].setPos(round(pos.x()), round(pos.y()))
                    if self.selected["type"] == ITEM_LINE: # moving the line as well
                        line = self.selected["obj"].line()

                        # if line's p2 has a negative coordinate, align it so it's inside the rect
                        if line.x2() < 0: self.selected["obj"].setX(self.selected["obj"].x() - line.x2())
                        if line.y2() < 0: self.selected["obj"].setY(self.selected["obj"].y() - line.y2())

                        # if line isn't diagonal, align it to be centered in the rect instead of the top
                        if line.x1() == line.x2(): self.selected["obj"].setX(self.selected["obj"].x() + 1)
                        if line.y1() == line.y2(): self.selected["obj"].setY(self.selected["obj"].y() + 1)
                    self.selected["rect"].setPos(round(pos.x()), round(pos.y()))
                elif self.selected["moveType"] == ITEM_LINE:
                    self.snapToLine(pos, self.selected["obj"])
                    line = self.selected["obj"].line() # copy
                    linePoint = getattr(line, "p%d"%self.selected["linePoint"])() # get line point
                    linePoint.setX(round(pos.x()) - self.selected["obj"].x())
                    linePoint.setY(round(pos.y()) - self.selected["obj"].y())
                    getattr(line, "setP%d"%self.selected["linePoint"])(linePoint) # set line point
                    self.selected["obj"].setLine(line)
                    

        elif self.parent.currtool == 1: # draw line tool
            if self.linePreview:
                pos = QtCore.QPointF(round(pos.x()), round(pos.y()))
                self.snapToLine(pos)
                self.linePreview.setLine(self.linePreview.line().x1(), self.linePreview.line().y1(), pos.x(), pos.y())

    def mouseReleaseEvent(self, event):
        pos = self.mapToScene(event.pos())
        if event.button() == QtCore.Qt.LeftButton:
            if self.parent.currtool == 0: # select
                if self.selected and self.moveSteps <= 0:
                    pass # add undo action

                    if self.selected["moveType"] == ITEM_LINE:
                        line = self.selected["obj"].line()
                        x = self.selected["obj"].x()
                        y = self.selected["obj"].y()
                        x1 = line.x1()
                        y1 = line.y1()
                        x2 = line.x2()
                        y2 = line.y2()
                        line.setP1(QtCore.QPointF(x1 + x, y1 + y))
                        line.setP2(QtCore.QPointF(x2 + x, y2 + y))
                        self.selected["obj"].setPos(0, 0)
                        self.selected["obj"].setLine(line)
                        self.lineToItemPos(self.selected["obj"])

                        x1 = min(self.selected["obj"].x(), self.selected["obj"].x() + self.selected["obj"].line().x2())
                        x2 = max(self.selected["obj"].x(), self.selected["obj"].x() + self.selected["obj"].line().x2())
                        y1 = min(self.selected["obj"].y(), self.selected["obj"].y() + self.selected["obj"].line().y2())
                        y2 = max(self.selected["obj"].y(), self.selected["obj"].y() + self.selected["obj"].line().y2())
                        if x1 == x2:
                            x1 -= 1
                            x2 += 1
                        elif y1 == y2:
                            y1 -= 1
                            y2 += 1
                        self.selected["rect"].setPos(x1, y1)
                        self.selected["rect"].setRect(0, 0, x2-x1, y2-y1)

                self.deselect()
                    
            elif self.parent.currtool == 1: # draw line
                if self.linePreview:
                    self.addLine(self.linePreview)
                    x1 = min(self.linePreview.x(), self.linePreview.x() + self.linePreview.line().x2())
                    x2 = max(self.linePreview.x(), self.linePreview.x() + self.linePreview.line().x2())
                    y1 = min(self.linePreview.y(), self.linePreview.y() + self.linePreview.line().y2())
                    y2 = max(self.linePreview.y(), self.linePreview.y() + self.linePreview.line().y2())
                    if x1 == x2:
                        x1 -= 1
                        x2 += 1
                    elif y1 == y2:
                        y1 -= 1
                        y2 += 1
                    rect = QtGui.QGraphicsRectItem(0, 0, x2-x1, y2-y1, scene=self.scene)
                    rect.setPos(x1, y1)
                    rect.setZValue(self.linePreview.zValue()-1)
                    pen = QtGui.QPen(QtCore.Qt.red)
                    pen.setWidth(1)
                    pen.setCosmetic(False)
                    rect.setPen(pen)
                    self.objects[-1]["rect"] = rect
                    self.linePreview = None

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
        self.currtool = 0

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
        self.view = ZoneSceneView(self.scene, self)
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
                answer = QtGui.QMessageBox(QtGui.QMessageBox.Question, "Unsaved changes", "Would you like to save changes?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel).exec_()
                if answer == QtGui.QMessageBox.Yes:
                    pass
                elif answer == QtGui.QMessageBox.Cancel:
                    return # stop loading
                self.changes = False

            self.scene.clear()
            self.view.objects = []

            self.zonebg = QtGui.QGraphicsPixmapItem(scene=self.scene)
            pixmap = QtGui.QPixmap(config.datadir+"/zones/"+name+"/zone.png")
            self.zonebg.setPixmap(pixmap)
            self.zonebg.setZValue(-10000)
            self.scene.setSceneRect(0, 0, pixmap.size().width(), pixmap.size().height())
            while self.view.zoomOut(): pass # set to normal scale

    @QtCore.pyqtSlot("int", "bool")
    def onClickTool(self, ind, toggled):
        self.currtool = ind
        for tool in self.tools:
            tool.blockSignals(True)
            tool.setChecked(self.tools[ind] == tool)
            tool.blockSignals(False)

    @QtCore.pyqtSlot("QListWidgetItem")
    def onClickZoneItem(self, item):
        self.loadZone(item.text())