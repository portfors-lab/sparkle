import sip
sip.setapi('QVariant', 2)
sip.setapi('QString', 2)

from PyQt4 import QtGui, QtCore

from spikeylab.main.drag_label import DragLabel
from spikeylab.stim.auto_parameter_view import AutoParameterTableView, AddLabel
from spikeylab.main.trashcan import TrashWidget
from spikeylab.main.hidden_widget import WidgetHider
from spikeylab.stim.reorder import order_function


class Parametizer(QtGui.QWidget):
    hintRequested = QtCore.pyqtSignal(str)
    def __init__(self, stimulusview=None, parent=None):
        QtGui.QWidget.__init__(self, parent)

        layout = QtGui.QVBoxLayout()
        btnLayout = QtGui.QHBoxLayout()
        
        self.addLbl = DragLabel(AddLabel)

        separator = QtGui.QFrame()
        separator.setFrameShape(QtGui.QFrame.VLine)
        separator.setFrameShadow(QtGui.QFrame.Sunken)
        
        self.trashLbl = TrashWidget(self)
        
        self.randomizeCkbx = QtGui.QCheckBox("Randomize order")
        self.randomizeCkbx.toggled.connect(self.randomToggle)

        btnLayout.addWidget(self.addLbl)
        btnLayout.addWidget(self.trashLbl)
        btnLayout.addWidget(separator)
        btnLayout.addWidget(self.randomizeCkbx)

        self.paramList = AutoParameterTableView()
        self.paramList.installEventFilter(self.trashLbl)
        self.paramList.hintRequested.connect(self.hintRequested)

        if stimulusview is not None:
            self.setStimulusView(stimulusview)

        layout.addWidget(self.paramList)
        layout.addLayout(btnLayout)
        self.setLayout(layout)
        self.setWindowTitle('Auto Parameters')

    def randomToggle(self, randomize):
        if randomize:
            self.paramModel.stimModel().setReorderFunc(order_function('random'), 'random')
        else:
            self.paramModel.stimModel().reorder = None

    def setParameterList(self, paramlist):
        self.paramModel.setParameterList(paramlist)

    def setStimulusView(self, view):
        self.paramModel = view.model().autoParams()
        self.paramModel.setStimView(view)
        self.paramList.setModel(self.paramModel)
        self.randomizeCkbx.setChecked(bool(view.model().reorder))

        self.paramModel.emptied.connect(self.tableEmptied)
        self.paramModel.hintRequested.connect(self.hintRequested)
        self.paramModel.stimChanged.connect(view.dataChanged)

    def tableEmptied(self, empty):
        self.paramModel.stimView().setEnabled(not empty)
        if empty:
            self.paramModel.stimView().setSelectionModel(QtGui.QItemSelectionModel(self.paramModel.stimView().model()))


    def sizeHint(self):
        return QtCore.QSize(560,200)

    def showEvent(self, event):
        selected = self.paramList.selectedIndexes()
        if len(selected) > 0:
            self.paramModel.updateSelectionModel(selected[0])
            self.hintRequested.emit('Select parameter to edit. \
                Parameter must have selected components in order to edit fields')
        elif self.paramModel.rowCount() > 0:
            # just select first item
            self.paramList.selectRow(0)
            self.paramModel.updateSelectionModel(self.paramModel.index(0,0))
        else:
            self.paramModel.stimView().setEnabled(False)
            self.hintRequested.emit('Drag to add parameter first')
        self.paramModel.stimView().setMode(1)

    def hideEvent(self, event):
        self.paramModel.stimView().setMode(0)
        # change stimulus components to reflect auto-parameter start values
        self.paramModel.updateComponentStartVals()
        self.hintRequested.emit('Drag Components onto view to Add. Double click to edit; right drag to move.')

    def closeEvent(self, event):
        self.paramModel.stimView().setMode(0)
        self.paramModel.updateComponentStartVals()


class HidableParameterEditor(WidgetHider):
    def __init__(self, parent=None):
        self.parametizer = Parametizer()
        WidgetHider.__init__(self, self.parametizer, parent=parent)

        # wrap methods from parametizer
        for m in ['setStimulusView', 'hintRequested']:
            setattr(self, m, getattr(self.parametizer, m))

    def sizeHint(self):
        return QtCore.QSize(560,40)


if __name__ == '__main__':
    import sys
    from spikeylab.stim.stimulusview import *
    from spikeylab.stim.stimulusmodel import *

    app  = QtGui.QApplication(sys.argv)

    stim = StimulusModel()
    stimview = StimulusView()
    stimview.setModel(stim)
    automagic = Parametizer(stimview)
    automagic.show()

    app.exec_()