import sip
sip.setapi('QVariant', 2)
sip.setapi('QString', 2)

from PyQt4 import QtGui

from spikeylab.gui.drag_label import DragLabel
from spikeylab.gui.stim.factory import BuilderFactory, TCFactory, TemplateFactory
from spikeylab.gui.trashcan import TrashWidget

class StimulusLabelTable(QtGui.QWidget):
    def __init__(self, parent=None):
        super(StimulusLabelTable, self).__init__(parent)

        layout = QtGui.QGridLayout()

        self.builderLbl = DragLabel(BuilderFactory)
        self.tcLbl = DragLabel(TCFactory)
        self.templateLbl = DragLabel(TemplateFactory)
        self.trashLbl = TrashWidget()
        self.trashLbl.setMinimumWidth(100)

        layout.addWidget(self.builderLbl, 0,0)
        layout.addWidget(self.tcLbl,0,1)
        layout.addWidget(self.templateLbl,0,2)
        layout.addWidget(self.trashLbl, 0,3)

        self.setLayout(layout)
        self.setToolTip("Drag to list")

    def trash(self):
        return self.trashLbl


if __name__ == '__main__':


    import sys
    app  = QtGui.QApplication(sys.argv)
    labelgrid = StimulusLabelTable()
    labelgrid.show()
    app.exec_()
