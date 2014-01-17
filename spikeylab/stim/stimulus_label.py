import sip
sip.setapi('QVariant', 2)
sip.setapi('QString', 2)

from PyQt4 import QtGui, QtCore

import cPickle

from spikeylab.main.drag_label import FactoryLabel
from spikeylab.stim.stimulus_editor import BuilderFactory
from spikeylab.main.trashcan import TrashWidget

class StimulusLabelTable(QtGui.QWidget):
    def __init__(self, parent=None):
        super(StimulusLabelTable, self).__init__(parent)

        layout = QtGui.QGridLayout()

        builder_lbl = FactoryLabel(BuilderFactory)
        self.trash_lbl = TrashWidget()

        layout.addWidget(builder_lbl, 0,0)
        layout.addWidget(self.trash_lbl, 0,1)

        self.setLayout(layout)

    def trash(self):
        return self.trash_lbl


if __name__ == '__main__':


    import sys
    app  = QtGui.QApplication(sys.argv)
    labelgrid = StimulusLabelTable()
    labelgrid.show()
    app.exec_()
