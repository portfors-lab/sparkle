import sip
sip.setapi('QVariant', 2)
sip.setapi('QString', 2)

from PyQt4 import QtGui, QtCore

from spikeylab.main.drag_label import FactoryLabel
from spikeylab.stim.auto_parameter_view import AutoParameterListView, AutoParameterDelegate,  AutoParamWidget
from spikeylab.stim.auto_parameter_model import AutoParameterModel
from spikeylab.main.trashcan import TrashWidget

class AddLabel():
    name = "Add"

class Parametizer(QtGui.QWidget):
    def __init__(self, stimulusview, parent=None):
        QtGui.QWidget.__init__(self, parent)

        layout = QtGui.QVBoxLayout()
        btn_layout = QtGui.QHBoxLayout()
        
        add_lbl = FactoryLabel(AddLabel)
        ok_btn = QtGui.QPushButton('OK')
        ok_btn.clicked.connect(self.saveParameters)

        separator = QtGui.QFrame()
        separator.setFrameShape(QtGui.QFrame.VLine)
        separator.setFrameShadow(QtGui.QFrame.Sunken)
        
        self.trash_lbl = TrashWidget()
        

        btn_layout.addWidget(add_lbl)
        btn_layout.addWidget(self.trash_lbl)
        btn_layout.addWidget(separator)
        btn_layout.addWidget(ok_btn)

        self.param_list = AutoParameterListView()
        self.param_list.installEventFilter(self)

        self.param_model = stimulusview.model().autoParams()
        self.param_model.setStimView(stimulusview)
        self.param_list.setModel(self.param_model)

        layout.addWidget(self.param_list)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def setParameterList(self, paramlist):
        self.param_model.setParameterList(paramlist)

    def saveParameters(self): 
        # print 'save to stim model'
        # this is the same model from stimulusview.model() we set in contructor
        # do I need to do this?
        # self.param_model.parentModel().setAutoParams(self.param_model)

        self.close()

    def sizeHint(self):
        return QtCore.QSize(560,200)

    def closeEvent(self, event):
        self.param_model.stimView().setMode(0)

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.ChildRemoved and self.trash_lbl.underMouse():
            return True
        else:
            return super(Parametizer, self).eventFilter(source, event)


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