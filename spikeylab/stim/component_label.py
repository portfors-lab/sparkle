from PyQt4 import QtGui

from spikeylab.stim.types import get_stimuli_models
from spikeylab.main.trashcan import TrashWidget
from spikeylab.main.drag_label import DragLabel

class ComponentTemplateTable(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ComponentTemplateTable, self).__init__(parent)

        layout = QtGui.QGridLayout()
        ncolumns = 2

        self.stimLabels = {}
        stimuli = get_stimuli_models()
        count = 0
        for stimulus in stimuli:
            if stimulus.protocol:
                label = DragLabel(stimulus)
                layout.addWidget(label, count/ncolumns, count % ncolumns)
                count += 1
                self.stimLabels[stimulus.name.lower()] = label

        self.trashLbl = TrashWidget()
        layout.addWidget(self.trashLbl, count/ncolumns, count % ncolumns)

        self.setLayout(layout)

    def trash(self):
        return self.trashLbl

    def getLabelByName(self, name):
        print 'stim labels', self.stimLabels
        name = name.lower()
        if name in self.stimLabels:
            return self.stimLabels[name]
        else:
            return None

if __name__ == '__main__':
    import sys
    app  = QtGui.QApplication(sys.argv)
    labelgrid = ComponentTemplateTable()
    labelgrid.show()
    app.exec_()
