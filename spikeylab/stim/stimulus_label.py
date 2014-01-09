import sip
sip.setapi('QVariant', 2)
sip.setapi('QString', 2)

from PyQt4 import QtGui, QtCore

import cPickle

from spikeylab.stim.stimulus_editor import BuilderFactory

class StimulusLabel(QtGui.QLabel):
    def __init__(self, factoryclass, parent=None):
        super(StimulusLabel, self).__init__(parent)
        self.setFrameStyle(QtGui.QFrame.Raised | QtGui.QFrame.StyledPanel)
        self.setClass(factoryclass)

    def setClass(self, factoryclass):
        """Constructor for the component type this label is to represent"""
        self.factoryclass = factoryclass
        self.setText(str(factoryclass.name))

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            # create a new component with default values
            factory = self.factoryclass()

            mimeData = QtCore.QMimeData()
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

            result = drag.start(QtCore.Qt.MoveAction)

class StimulusLabelTable(QtGui.QWidget):
    def __init__(self, parent=None):
        super(StimulusLabelTable, self).__init__(parent)

        layout = QtGui.QGridLayout()

        builder_lbl = StimulusLabel(BuilderFactory)

        layout.addWidget(builder_lbl, 0,0)

        self.setLayout(layout)

if __name__ == '__main__':


    import sys
    app  = QtGui.QApplication(sys.argv)
    labelgrid = StimulusLabelTable()
    labelgrid.show()
    app.exec_()
