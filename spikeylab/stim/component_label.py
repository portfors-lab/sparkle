from PyQt4 import QtGui

from spikeylab.stim.types import get_stimuli_models
from spikeylab.main.trashcan import TrashWidget
from spikeylab.main.drag_label import DragLabel

class ComponentTemplateTable(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ComponentTemplateTable, self).__init__(parent)

        layout = QtGui.QGridLayout()
        ncolumns = 2

        stimuli = get_stimuli_models()
        count = 0
        for stimulus in stimuli:
            if stimulus.protocol:
                label = DragLabel(stimulus)
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
