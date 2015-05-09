from sparkle.QtWrapper import QtGui
from sparkle.gui.drag_label import DragLabel
from sparkle.gui.stim.factory import BuilderFactory, TCFactory, TemplateFactory
from sparkle.gui.trashcan import TrashWidget


class StimulusLabelTable(QtGui.QWidget):
    """A Container with draggable Stimulus labels that drop StimulusModels"""
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

    def trash(self):
        """Returns the trash widget"""
        return self.trashLbl

    def labels(self):
        return [self.builderLbl, self.tcLbl, self.templateLbl]


if __name__ == '__main__':


    import sys
    app  = QtGui.QApplication(sys.argv)
    labelgrid = StimulusLabelTable()
    labelgrid.show()
    app.exec_()
