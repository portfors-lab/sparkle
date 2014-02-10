import sip
sip.setapi('QVariant', 2)
sip.setapi('QString', 2)

import random

from PyQt4 import QtGui, QtCore

from spikeylab.main.drag_label import DragLabel
from spikeylab.stim.auto_parameter_view import AutoParameterTableView, AddLabel
from spikeylab.stim.auto_parameter_model import AutoParameterModel
from spikeylab.main.trashcan import TrashWidget
from spikeylab.main.hidden_widget import WidgetHider


class Parametizer(QtGui.QWidget):
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
        # btn_layout.addWidget(QtGui.QLabel())
        btn_layout.addWidget(self.randomize_ckbx)

        self.param_list = AutoParameterTableView()
        self.param_list.installEventFilter(self.trash_lbl)

        if stimulusview is not None:
            self.param_model = stimulusview.model().autoParams()
            self.param_model.setStimView(stimulusview)
            self.param_list.setModel(self.param_model)
            # this may mislead/clobber other orderings if present on model
            self.randomize_ckbx.setChecked(bool(stimulusview.model().reorder))

        layout.addWidget(self.param_list)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.setWindowTitle('Auto Parameters')

    def randomToggle(self, randomize):
        if randomize:
            self.param_model.stimModel().reorder = random_order
        else:
            self.param_model.stimModel().reorder = None

    def setParameterList(self, paramlist):
        self.param_model.setParameterList(paramlist)

    def setStimulusView(self, view):
        self.param_model = view.model().autoParams()
        self.param_model.setStimView(view)
        self.param_list.setModel(self.param_model)
        self.randomize_ckbx.setChecked(bool(view.model().reorder))

    def sizeHint(self):
        return QtCore.QSize(560,200)

    def showEvent(self, event):
        selected = self.param_list.selectedIndexes()
        if len(selected) > 0:
            print 'selected indexes', selected[0].row()
            self.param_model.updateSelectionModel(selected[0])
        self.param_model.stimView().setMode(1)
    def hideEvent(self, event):
        self.param_model.stimView().setMode(0)
    def closeEvent(self, event):
        self.param_model.stimView().setMode(0)

class HidableParameterEditor(WidgetHider):
    def __init__(self, parent=None):
        self.parametizer = Parametizer()
        WidgetHider.__init__(self, self.parametizer, parent=parent)

    def setStimulusView(self, view):
        self.parametizer.setStimulusView(view)

    def sizeHint(self):
        return QtCore.QSize(560,40)

def random_order(listofthings):
    order = range(len(listofthings))
    random.shuffle(order)
    return order

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