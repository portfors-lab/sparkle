import cPickle

from PyQt4 import QtGui, QtCore

class DragLabel(QtGui.QLabel):
    def __init__(self, factoryclass, parent=None):
        super(DragLabel, self).__init__(parent)
        self.setFrameStyle(QtGui.QFrame.Raised | QtGui.QFrame.Panel)
        self.setLineWidth(2)
        self.setClass(factoryclass)
        self.setMinimumSize(QtCore.QSize(100,32))
        self.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

    def setClass(self, factoryclass):
        """Constructor for the component type this label is to represent"""
        self.factoryclass = factoryclass
        self.setText(str(factoryclass.name))

    def mousePressEvent(self, event):
        # create a new component with default values
        self.dragStartPosition = event.pos()
        
    def mouseMoveEvent(self, event):
        if (event.pos() - self.dragStartPosition).manhattanLength() < 10:
            return
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

        result = drag.exec_(QtCore.Qt.MoveAction)


if __name__ == '__main__':


    import sys
    app  = QtGui.QApplication(sys.argv)
    labelgrid = StimulusLabelTable()
    labelgrid.show()
    app.exec_()
