from PyQt4 import QtGui, QtCore

from spikeylab.gui.drag_label import DragLabel
from spikeylab.gui.stim.auto_parameter_view import AutoParameterTableView, AddLabel
from spikeylab.gui.trashcan import TrashWidget
from spikeylab.gui.hidden_widget import WidgetHider
from spikeylab.stim.reorder import order_function


class Parametizer(QtGui.QWidget):
    hintRequested = QtCore.pyqtSignal(str)
    visibilityChanged = QtCore.pyqtSignal(bool)
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        layout = QtGui.QVBoxLayout()
        btnLayout = QtGui.QHBoxLayout()
        
        self.addLbl = DragLabel(AddLabel)

        separator = QtGui.QFrame()
        separator.setFrameShape(QtGui.QFrame.VLine)
        separator.setFrameShadow(QtGui.QFrame.Sunken)
        
        self.trashLbl = TrashWidget(self)
        
        self.randomizeCkbx = QtGui.QCheckBox("Randomize order")

        btnLayout.addWidget(self.addLbl)
        btnLayout.addWidget(self.trashLbl)
        btnLayout.addWidget(separator)
        btnLayout.addWidget(self.randomizeCkbx)

        self.paramList = AutoParameterTableView()
        self.paramList.installEventFilter(self.trashLbl)
        self.paramList.hintRequested.connect(self.hintRequested)

        layout.addWidget(self.paramList)
        layout.addLayout(btnLayout)
        self.setLayout(layout)
        self.setWindowTitle('Auto Parameters')

    def view(self):
        return self.paramList

    def setModel(self, model):
        self.paramList.setModel(model)

        model.hintRequested.connect(self.hintRequested)

    def sizeHint(self):
        return QtCore.QSize(560,200)

    def showEvent(self, event):
        selected = self.paramList.selectedIndexes()
        model = self.paramList.model()

        # model.stimView().setMode(1)
        self.visibilityChanged.emit(1)
        if len(selected) > 0:
            # model.updateSelectionModel(selected[0])
            self.paramList.parameterChanged.emit(model.selection(selected[0]))
            self.hintRequested.emit('Select parameter to edit. \
                Parameter must have selected components in order to edit fields')
        elif model.rowCount() > 0:
            # just select first item
            self.paramList.selectRow(0)
            self.paramList.parameterChanged.emit(model.selection(model.index(0,0)))
            # model.updateSelectionModel(model.index(0,0))
        else:
            model.emptied.emit(True)
            # model.stimView().setEnabled(False)
            self.hintRequested.emit('Drag to add parameter first')

    def hideEvent(self, event):
        self.visibilityChanged.emit(0)
        # self.paramModel.stimView().setMode(0)
        # change stimulus components to reflect auto-parameter start values
        # self.paramModel.updateComponentStartVals()
        self.hintRequested.emit('Drag Components onto view to Add. Double click to edit; right drag to move.')

    def closeEvent(self, event):
        self.paramModel.stimView().setMode(0)
        self.paramModel.updateComponentStartVals()


class HidableParameterEditor(WidgetHider):
    def __init__(self, parent=None):
        self.parametizer = Parametizer()
        WidgetHider.__init__(self, self.parametizer, parent=parent)

        # wrap methods from parametizer
        for m in ['setModel', 'hintRequested', 'visibilityChanged', 
                    'view', 'randomizeCkbx']:
            setattr(self, m, getattr(self.parametizer, m))

    def sizeHint(self):
        return QtCore.QSize(560,40)


if __name__ == '__main__':
    import sys
    from spikeylab.gui.stim.stimulusview import *
    from spikeylab.stim.stimulusmodel import *

    app  = QtGui.QApplication(sys.argv)

    stim = StimulusModel()
    stimview = StimulusView()
    stimview.setModel(stim)
    automagic = Parametizer(stimview)
    automagic.show()

    app.exec_()