from sparkle.QtWrapper import QtGui
from sparkle.gui.drag_label import DragLabel
from sparkle.gui.trashcan import TrashWidget
from sparkle.stim.types import get_stimuli_models


class ComponentTemplateTable(QtGui.QWidget):
    """A container filled with draggable labels that drop stimulus components"""
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
        """Returns the trash widget for this container

        :returns: :class:`TrashWidget<sparkle.gui.trashcan.TrashWidget>`
        """
        return self.trashLbl

    def getLabelByName(self, name):
        """Gets a label widget by it component name

        :param name: name of the AbstractStimulusComponent which this label is named after
        :type name: str
        :returns: :class:`DragLabel<sparkle.gui.drag_label.DragLabel>`
        """
        name = name.lower()
        if name in self.stimLabels:
            return self.stimLabels[name]
        else:
            return None

    def labels(self):
        return self.stimLabels.values()

if __name__ == '__main__':
    import sys
    app  = QtGui.QApplication(sys.argv)
    labelgrid = ComponentTemplateTable()
    labelgrid.show()
    app.exec_()
