import cPickle

from sparkle.QtWrapper import QtCore, QtGui
from sparkle.gui.border import QBorder
from sparkle.gui.qconstants import CursorRole


class AbstractDragView(object):
    """Class to keep drag and drop behaviour consistent across UI"""
    DragRole = 33
    def __init__(self):
        super(AbstractDragView, self).__init__()
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.dragline = None
        self.originalPos = None
        self.dragStartPosition = None
        self.setMouseTracking(True)
        self._frame = QBorder(self)

    def grabImage(self, index):
        """Gets a pixmap image of the item located at index

        Must be implemented by subclass.

        :param index: index of the item
        :type index: :qtdoc:`QModelIndex`
        :returns: :qtdoc:`QPixMap`
        """
        # should return a QPixMap to represent the item at index
        raise NotImplementedError

    def cursor(self, index):
        """Gets a line to draw to indicate where a drop will occur

        Must be implemented by subclass.

        :param index: index of the item
        :type index: :qtdoc:`QModelIndex`
        :returns: :qtdoc:`QLine`
        """
        raise NotImplementedError

    def indexXY(self, index):
        """Return the top left coordinates for the given *index*, relative
        to self.

        Must be implemented by subclass.

        :param index: index of the item
        :type index: :qtdoc:`QModelIndex`
        :returns: (int, int) -- (x, y) coordinates
        """
        raise NotImplementedError

    def mousePressEvent(self, event):
        """saves the drag position, so we know when a drag should be initiated"""
        super(AbstractDragView, self).mousePressEvent(event)
        self.dragStartPosition = event.pos()

    def mouseMoveEvent(self, event):
        """Determines if a drag is taking place, and initiates it"""
        super(AbstractDragView, self).mouseMoveEvent(event)
        if self.dragStartPosition is None or \
            (event.pos() - self.dragStartPosition).manhattanLength() < QtGui.QApplication.startDragDistance():
            # change cursor to reflect actions for what its hovering on
            index = self.indexAt(event.pos())
            cursor = self.model().data(index, CursorRole)
            self.setCursor(cursor)
            return
        # mouse has been dragged past a threshold distance

        index = self.indexAt(self.dragStartPosition)
        if not index.isValid():
            return
        # grab the pixmap first, as it may be cleared from component,
        # and slows GUI due to redraw.
        pixmap = self.grabImage(index)

        # get the item at the drug index
        selected = self.model().data(index, self.DragRole)
        if selected is None:
            return
            
        ## convert to  a bytestream
        bstream = cPickle.dumps(selected)
        mimeData = QtCore.QMimeData()
        mimeData.setData("application/x-protocol", bstream)

        # save this component in case the drag ends not in a droppable region, 
        # and we want to return it to it's original place
        self.limbo_component = selected
        self.originalPos = index
        
        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)

        # this makes the pixmap half transparent
        painter = QtGui.QPainter(pixmap)
        painter.setCompositionMode(painter.CompositionMode_DestinationIn)
        painter.fillRect(pixmap.rect(), QtGui.QColor(0, 0, 0, 127))
        painter.end()
        
        drag.setPixmap(pixmap)

        x, y = self.indexXY(index)
        drag.setHotSpot(QtCore.QPoint(event.x()-x, event.y()-y))
        # drag.setHotSpot(QtCore.QPoint(pixmap.width()/2, pixmap.height()/2))
        drag.setPixmap(pixmap)

        self.model().removeItem(index)
        result = drag.exec_(QtCore.Qt.MoveAction)

    def dragEnterEvent(self, event):
        """Determines if the widget under the mouse can recieve the drop"""
        super(AbstractDragView, self).dragEnterEvent(event)
        if event.mimeData().hasFormat("application/x-protocol"):
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """Determines if the widget under the mouse can recieve the drop"""
        super(AbstractDragView, self).dragMoveEvent(event)
        if event.mimeData().hasFormat("application/x-protocol"):
            # find the nearest break to cursor
            self.dragline = self.cursor(event.pos())
            self.viewport().update()
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        """Clears drop cursor line"""
        super(AbstractDragView, self).dragLeaveEvent(event)
        self.dragline = None
        self.viewport().update()
        event.accept()

    def dropped(self, item, event):
        """Deals with an item dropped on the view

        Must be implemented by subclass

        :param item: same item that was selected, and removed at the start of drag
        :param event: Qt event obect passed from dropEvent
        :type event: :qtdoc:`QDropEvent`
        """
        raise NotImplementedError

    def dropEvent(self, event):
        """Handles an item being dropped onto view, calls
        dropped -- implemented by subclass
        """
        super(AbstractDragView, self).dropEvent(event)
        self.dragStartPosition = None
        self.dragline = None
        self.originalPos = None
        data = event.mimeData()
        stream = data.retrieveData("application/x-protocol",
            QtCore.QVariant.ByteArray)
        item = cPickle.loads(str(stream.toByteArray()))

        self.dropped(item, event)

        event.accept()

    def childEvent(self, event):    
        """Catches items dropped off edge of view, 
        reinserts at original position

        :param event: contains event parameters for child object events
        :type event: :qtdoc:`QChildEvent`
        """
        super(AbstractDragView, self).childEvent(event)
        if event.type() == QtCore.QEvent.ChildRemoved:
            # hack to catch drop offs   
            if self.originalPos is not None:
                selected = self.limbo_component
                self.model().insertItem(self.originalPos, selected)
                self.originalPos = None
                self.dragStartPosition = None
                self.viewport().update()

    def mouseReleaseEvent(self, event):
        """Resets the drag start position"""
        super(AbstractDragView, self).mouseReleaseEvent(event)
        self.dragStartPosition = None

    def frame(self):
        return self._frame

    def showBorder(self, show):
        self._frame.showBorder(show)
