from PyQt4 import QtGui, QtCore

from spikeylab.stim.types.stimuli_classes import PureTone, Vocalization, Silence, FMSweep

class ComponentTemplateLabel(QtGui.QLabel):
    def __init__(self, componentclass, parent=None):
        super(ComponentTemplateLabel, self).__init__(parent)
        self.setFrameStyle(QtGui.QFrame.Raised | QtGui.QFrame.StyledPanel)
        self.setClass(componentclass)

    def setClass(self, componentclass):
        """Constructor for the component type this label is to represent"""
        self.componentclass = componentclass
        self.setText(str(componentclass().name))

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            # create a new component with default values
            newcomponent = self.componentclass()

            mimeData = QtCore.QMimeData()
            mimeData.setData("application/x-component", newcomponent.serialize())

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

class ComponentTemplateTable(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ComponentTemplateTable, self).__init__(parent)

        layout = QtGui.QGridLayout()

        tone_lbl = ComponentTemplateLabel(PureTone)
        vocal_lbl = ComponentTemplateLabel(Vocalization)
        silence_lbl = ComponentTemplateLabel(Silence)
        fmsweep_lbl = ComponentTemplateLabel(FMSweep)

        layout.addWidget(tone_lbl, 0,0)
        layout.addWidget(vocal_lbl, 0,1)
        layout.addWidget(silence_lbl, 1,0)
        layout.addWidget(fmsweep_lbl, 1,1)

        self.setLayout(layout)


if __name__ == '__main__':
    import sys
    app  = QtGui.QApplication(sys.argv)
    labelgrid = ComponentTemplateTable()
    labelgrid.show()
    app.exec_()
