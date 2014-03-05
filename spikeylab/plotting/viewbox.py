from PyQt4 import QtCore, QtGui
import pyqtgraph as pg
from pyqtgraph.Point import Point
import pyqtgraph.functions as fn

import numpy as np

class SpikeyViewBox(pg.ViewBox):
    def __init__(self, *args, **kwargs):
        super(SpikeyViewBox, self).__init__(*args, **kwargs)

        # because of pyqtgraph internals, we can't just remove this action from menu
        self.fake_action = QtGui.QAction("", None)
        self.fake_action.setVisible(False)
        self.fake_action.setCheckable(True)
        self.menu.leftMenu = self.fake_action
        self.menu.mouseModes = [self.fake_action]

        self.menu.viewAll.triggered.disconnect()
        self.menu.viewAll.triggered.connect(self.auto_range)

        self._custom_mouse = False
        self._zero_wheel = False

    def set_custom_mouse(self):
        self._custom_mouse = True

    def set_zero_wheel(self):
        self._zero_wheel = True
        # want padding in this case
        self.menu.viewAll.triggered.disconnect()
        self.menu.viewAll.triggered.connect(self.autoRange)

    def mouseDragEvent(self, ev, axis=None):
        if self._custom_mouse and ev.button() == QtCore.Qt.LeftButton:
            ev.accept()  ## we accept all buttons

            # directly copy-pasted from ViewBox for ViewBox.RectMode
            if ev.isFinish():  ## This is the final move in the drag; change the view scale now
                #print "finish"
                pos = ev.pos()

                self.rbScaleBox.hide()
                #ax = QtCore.QRectF(Point(self.pressPos), Point(self.mousePos))
                ax = QtCore.QRectF(Point(ev.buttonDownPos(ev.button())), Point(pos))
                ax = self.childGroup.mapRectFromParent(ax)
                self.showAxRect(ax)
                self.axHistoryPointer += 1
                self.axHistory = self.axHistory[:self.axHistoryPointer] + [ax]
            else:
                ## update shape of scale box
                self.updateScaleBox(ev.buttonDownPos(), ev.pos())
        else:
            super(SpikeyViewBox, self).mouseDragEvent(ev, axis)


    def auto_range(self):
        self.autoRange(padding=0)

    def wheelEvent(self, ev, axis=None):
        if self._zero_wheel:
            ev.pos = lambda : self.mapViewToScene(QtCore.QPoint(0,0))
        super(SpikeyViewBox, self).wheelEvent(ev, axis)
