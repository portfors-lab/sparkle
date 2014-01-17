from PyQt4 import QtGui, QtCore

from spikeylab.stim.types import get_stimuli_models
# from spikeylab.stim.types.stimuli_classes import PureTone, Vocalization, Silence, FMSweep
from spikeylab.main.trashcan import TrashWidget

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
            mimeData.setData("application/x-protocol", newcomponent.serialize())

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
        ncolumns = 2

        stimuli = get_stimuli_models()
        count = 0
        for stimulus in stimuli:
            if stimulus.protocol:
                label = ComponentTemplateLabel(stimulus)
                layout.addWidget(label, count/ncolumns, count % ncolumns)
                count += 1

        self.trash_lbl = TrashWidget()
        layout.addWidget(self.trash_lbl, count/ncolumns, count % ncolumns)

        self.setLayout(layout)

    def trash(self):
        return self.trash_lbl

if __name__ == '__main__':
    import sys
    app  = QtGui.QApplication(sys.argv)
    labelgrid = ComponentTemplateTable()
    labelgrid.show()
    app.exec_()
