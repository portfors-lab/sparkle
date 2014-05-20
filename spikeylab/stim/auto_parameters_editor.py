import sip
sip.setapi('QVariant', 2)
sip.setapi('QString', 2)

from PyQt4 import QtGui, QtCore

from spikeylab.main.drag_label import DragLabel
from spikeylab.stim.auto_parameter_view import AutoParameterTableView, AddLabel
from spikeylab.stim.auto_parameter_model import AutoParameterModel
from spikeylab.main.trashcan import TrashWidget
from spikeylab.main.hidden_widget import WidgetHider
from spikeylab.stim.reorder import order_function


class Parametizer(QtGui.QWidget):
    hintRequested = QtCore.pyqtSignal(str)
    def __init__(self, stimulusview=None, parent=None):
        QtGui.QWidget.__init__(self, parent)

        layout = QtGui.QVBoxLayout()
        btn_layout = QtGui.QHBoxLayout()
        
        add_lbl = DragLabel(AddLabel)

        separator = QtGui.QFrame()
        separator.setFrameShape(QtGui.QFrame.VLine)
        separator.setFrameShadow(QtGui.QFrame.Sunken)
        
        self.trash_lbl = TrashWidget(self)
        
        self.randomize_ckbx = QtGui.QCheckBox("Randomize order")
        self.randomize_ckbx.toggled.connect(self.randomToggle)

        btn_layout.addWidget(add_lbl)
        btn_layout.addWidget(self.trash_lbl)
        btn_layout.addWidget(separator)
        btn_layout.addWidget(self.randomize_ckbx)

        self.param_list = AutoParameterTableView()
        self.param_list.installEventFilter(self.trash_lbl)
        self.param_list.hintRequested.connect(self.hintRequested)

        if stimulusview is not None:
            self.setStimulusView(stimulusview)

        layout.addWidget(self.param_list)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.setWindowTitle('Auto Parameters')

    def randomToggle(self, randomize):
        if randomize:
            self.param_model.stimModel().setReorderFunc(order_function('random'), 'random')
        else:
            self.param_model.stimModel().reorder = None

    def setParameterList(self, paramlist):
        self.param_model.setParameterList(paramlist)

    def setStimulusView(self, view):
        self.param_model = view.model().autoParams()
        self.param_model.setStimView(view)
        self.param_list.setModel(self.param_model)
        self.randomize_ckbx.setChecked(bool(view.model().reorder))

        self.param_model.emptied.connect(self.table_emptied)
        self.param_model.hintRequested.connect(self.hintRequested)
        self.param_model.stimChanged.connect(view.dataChanged)

    def table_emptied(self, empty):
        self.param_model.stimView().setEnabled(not empty)
        if empty:
            self.param_model.stimView().setSelectionModel(QtGui.QItemSelectionModel(self.param_model.stimView().model()))


    def sizeHint(self):
        return QtCore.QSize(560,200)

    def showEvent(self, event):
        selected = self.param_list.selectedIndexes()
        if len(selected) > 0:
            self.param_model.updateSelectionModel(selected[0])
            self.hintRequested.emit('Select parameter to edit. \
                Parameter must have selected components in order to edit fields')
        elif self.param_model.rowCount() > 0:
            # just select first item
            self.param_list.selectRow(0)
            self.param_model.updateSelectionModel(self.param_model.index(0,0))
        else:
            self.param_model.stimView().setEnabled(False)
            self.hintRequested.emit('Drag to add parameter first')
        self.param_model.stimView().setMode(1)

    def hideEvent(self, event):
        self.param_model.stimView().setMode(0)
        # change stimulus components to reflect auto-parameter start values
        self.param_model.updateComponentStartVals()
        self.hintRequested.emit('Drag Components onto view to Add. Double click to edit; right drag to move.')

    def closeEvent(self, event):
        self.param_model.stimView().setMode(0)
        self.param_model.updateComponentStartVals()


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