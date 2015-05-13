import pyqtgraph as pg
from pyqtgraph.Point import Point

from sparkle.QtWrapper import QtCore, QtGui


class SpikeyViewBox(pg.ViewBox):
    """View box subclasses for the purpose of custom mouse interaction"""
    def __init__(self, *args, **kwargs):
        super(SpikeyViewBox, self).__init__(*args, **kwargs)

        self.menu = SpikeyViewBoxMenu(self)

        self._customMouse = True
        self._zeroWheel = False

    def setCustomMouse(self, usecustom=True):
        """Whether to use our custom defined mouse behaviour

        :param usecustom: whether to use the custom behaviour
        :type usecustom: bool
        """
        self._customMouse = usecustom

    def setZeroWheel(self):
        """Sets the zoom locus of the mouse wheel to the point 0,0
        (instead of the coordinates under the cursor)"""
        self._zeroWheel = True
        # want padding in this case
        self.menu.viewAll.triggered.disconnect()
        self.menu.viewAll.triggered.connect(self.autoRange)

    def mouseDragEvent(self, ev, axis=None):
        """Customized mouse dragging, where the right drag is bounding box zoom
        
        :param ev: event object containing drag state info
        :type ev: :py:class:`MouseDragEvent<pyqtgraph:pyqtgraph.GraphicsScene.mouseEvents.MouseDragEvent>`
        """
        if self._customMouse and ev.button() == QtCore.Qt.RightButton:
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
            state = None
            # ctrl reverses mouse operation axis
            if ev.modifiers() == QtCore.Qt.ControlModifier:
                state = self.mouseEnabled()
                self.setMouseEnabled(not state[0], not state[1])
            super(SpikeyViewBox, self).mouseDragEvent(ev, axis)
            if state is not None:
                self.setMouseEnabled(*state)

    def autoRange0(self):
        """autoRange with 0 padding"""
        return self.autoRange(padding=0)

    def wheelEvent(self, ev, axis=None):
        """Reacts to mouse wheel movement, custom behaviour switches zoom
        axis when ctrl is pressed, and sets the locus of zoom, if zeroWheel
        is set."""
        state = None
        # ctrl reverses mouse operation axis
        if ev.modifiers() == QtCore.Qt.ControlModifier:
            state = self.mouseEnabled()
            self.setMouseEnabled(not state[0], not state[1])
        if self._zeroWheel:
            ev.pos = lambda : self.mapViewToScene(QtCore.QPoint(0,0))
        super(SpikeyViewBox, self).wheelEvent(ev, axis)
        if state is not None:
            self.setMouseEnabled(*state)

class SpikeyViewBoxMenu(QtGui.QMenu):
    """Super simplified menu based from pyqtgraph ViewBoxMenu"""
    def __init__(self, view):
        super(SpikeyViewBoxMenu, self).__init__()

        self.setTitle("ViewBox options")
        self.viewAll = QtGui.QAction("View All", self)
        self.viewAll.triggered.connect(self.autoRange)
        self.addAction(self.viewAll)
        self.view = view

    def autoRange(self):
        """autoRange with zero padding"""
        self.view.autoRange(padding=0)

    def copy(self):
        """Adds menus to itself, required by ViewBox"""
        # copied from pyqtgraph ViewBoxMenu
        m = QtGui.QMenu()
        for sm in self.subMenus():
            if isinstance(sm, QtGui.QMenu):
                m.addMenu(sm)
            else:
                m.addAction(sm)
        m.setTitle(self.title())
        return m

    def subMenus(self):
        """Returns a List of all submenus"""
        return [self.viewAll] 

    def setViewList(self, views):
        """This will do nothing, required by ViewBox"""
        pass
