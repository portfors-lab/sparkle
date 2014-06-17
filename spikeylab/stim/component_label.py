from PyQt4 import QtGui

from spikeylab.stim.types import get_stimuli_models
from spikeylab.main.trashcan import TrashWidget
from spikeylab.main.drag_label import DragLabel

class ComponentTemplateTable(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ComponentTemplateTable, self).__init__(parent)

        layout = QtGui.QGridLayout()
        ncolumns = 2

        self.stim_labels = {}
        stimuli = get_stimuli_models()
        count = 0
        for stimulus in stimuli:
            if stimulus.protocol:
                label = DragLabel(stimulus)
                layout.addWidget(label, count/ncolumns, count % ncolumns)
                count += 1
                self.stim_labels[stimulus.name.lower()] = label

        self.trash_lbl = TrashWidget()
        layout.addWidget(self.trash_lbl, count/ncolumns, count % ncolumns)

        self.setLayout(layout)

    def trash(self):
        return self.trash_lbl

    def getLabelByName(self, name):
        print 'stim labels', self.stim_labels
        name = name.lower()
        if name in self.stim_labels:
            return self.stim_labels[name]
        else:
            return None

if __name__ == '__main__':
    import sys
    app  = QtGui.QApplication(sys.argv)
    labelgrid = ComponentTemplateTable()
    labelgrid.show()
    app.exec_()
