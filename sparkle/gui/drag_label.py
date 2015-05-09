import cPickle

from sparkle.QtWrapper import QtCore, QtGui
from sparkle.resources import cursors


class DragLabel(QtGui.QLabel):
    dragActive = QtCore.Signal(bool)
    def __init__(self, factoryclass, parent=None):
        super(DragLabel, self).__init__(parent)
        self.setFrameStyle(QtGui.QFrame.Raised | QtGui.QFrame.Panel)
        self.setLineWidth(2)
        self.setClass(factoryclass)
        self.setMinimumSize(QtCore.QSize(100,32))
        self.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.setToolTip("Drag to add")
        self.setCursor(cursors.openHand())

    def setClass(self, factoryclass):
        """Sets the constructor for the component type this label is to 
        represent

        :param factoryclass: a class that, when called, results in an instance of the desired class
        :type factoryclass: callable
        """
        self.factoryclass = factoryclass
        self.setText(str(factoryclass.name))

    def mousePressEvent(self, event):
        """saves the drag position, so we know when a drag should be initiated"""
        self.dragStartPosition = event.pos()
        
    def mouseMoveEvent(self, event):
        """Determines if a drag is taking place, and initiates it"""
        if (event.pos() - self.dragStartPosition).manhattanLength() < 10:
            return
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
        factory = self.factoryclass()

        mimeData = QtCore.QMimeData()
        try:
            mimeData.setData("application/x-protocol", factory.serialize())
        except:
            mimeData.setData("application/x-protocol", cPickle.dumps(factory))

        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)

        pixmap = QtGui.QPixmap()
        pixmap = pixmap.grabWidget(self, self.frameRect())

        # below makes the pixmap half transparent
        # painter = QtGui.QPainter(pixmap)
        # painter.setCompositionMode(painter.CompositionMode_DestinationIn)
        # painter.fillRect(pixmap.rect(), QtGui.QColor(0, 0, 0, 127))
        # painter.end()

        drag.setPixmap(pixmap)

        drag.setHotSpot(QtCore.QPoint(pixmap.width()/2, pixmap.height()/2))
        drag.setPixmap(pixmap)

        self.dragActive.emit(True)
        result = drag.exec_(QtCore.Qt.MoveAction)

        QtGui.QApplication.restoreOverrideCursor()

    def childEvent(self, event):
        if event.type() == QtCore.QEvent.ChildRemoved:
            self.dragActive.emit(False)

if __name__ == '__main__':


    import sys
    app  = QtGui.QApplication(sys.argv)
    labelgrid = StimulusLabelTable()
    labelgrid.show()
    app.exec_()
