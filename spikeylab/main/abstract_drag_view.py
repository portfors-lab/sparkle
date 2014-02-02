from PyQt4 import QtGui, QtCore

import cPickle

class AbstractDragView():
    DragRole = 33
    def __init__(self):
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.dragline = None
        self.original_pos = None

    def grabImage(self, index):
        raise NotImplementedError

    def cursor(self, index):
        raise NotImplementedError

    def indexXY(self, index):
        raise NotImplementedError

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            index = self.indexAt(event.pos())
            selected = self.model().data(index, QtCore.Qt.UserRole+1)

            ## convert to  a bytestream
            bstream = cPickle.dumps(selected)
            mimeData = QtCore.QMimeData()
            mimeData.setData("application/x-protocol", bstream)

            self.limbo_component = selected
            drag = QtGui.QDrag(self)
            drag.setMimeData(mimeData)

            pixmap = self.grabImage(index)

            # below makes the pixmap half transparent
            painter = QtGui.QPainter(pixmap)
            painter.setCompositionMode(painter.CompositionMode_DestinationIn)
            painter.fillRect(pixmap.rect(), QtGui.QColor(0, 0, 0, 127))
            painter.end()
            
            drag.setPixmap(pixmap)

            x, y = self.indexXY(index)
            drag.setHotSpot(QtCore.QPoint(event.x()-x, event.y()-y))
            # drag.setHotSpot(QtCore.QPoint(pixmap.width()/2, pixmap.height()/2))
            drag.setPixmap(pixmap)

            self.original_pos = index

            self.model().removeItem(index)
            result = drag.start(QtCore.Qt.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-protocol"):
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()


    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-protocol"):
            # find the nearest break to cursor
            self.dragline = self.cursor(event.pos())
            self.viewport().update()
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.dragline = None
        self.viewport().update()
        event.accept()

    def dropAssist(self, event):
        self.dragline = None
        self.original_pos = None
        data = event.mimeData()
        stream = data.retrieveData("application/x-protocol",
            QtCore.QVariant.ByteArray)
        return cPickle.loads(str(stream))

    def childEvent(self, event):
        if event.type() == QtCore.QEvent.ChildRemoved:
            # hack to catch drop offs   
            if self.original_pos is not None:
                selected = self.limbo_component
                self.model().insertItem(self.original_pos, selected)
                self.original_pos = None
                self.viewport().update()