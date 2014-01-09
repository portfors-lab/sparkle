import sip
sip.setapi('QVariant', 2)
sip.setapi('QString', 2)

from PyQt4 import QtGui, QtCore

from spikeylab.stim.auto_parameter_modelview import AutoParameterListView, AutoParameterDelegate, AutoParameterModel, AutoParamWidget


class Parametizer(QtGui.QWidget):
    def __init__(self, stimulusview, parent=None):
        QtGui.QWidget.__init__(self, parent)

        layout = QtGui.QVBoxLayout()
        btn_layout = QtGui.QHBoxLayout()
        
        add_btn = QtGui.QPushButton('Add')
        remove_btn = QtGui.QPushButton('Remove')
        ok_btn = QtGui.QPushButton('OK')
        cancel_btn = QtGui.QPushButton('Cancel')
        add_btn.clicked.connect(self.addParameter)
        remove_btn.clicked.connect(self.removeParameter)
        ok_btn.clicked.connect(self.saveParameters)

        separator = QtGui.QFrame()
        separator.setFrameShape(QtGui.QFrame.VLine)
        separator.setFrameShadow(QtGui.QFrame.Sunken)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addWidget(separator)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)

        self.param_list = AutoParameterListView()

        self.param_model = stimulusview.model().autoParams()
        self.param_model.setStimView(stimulusview)
        self.param_list.setModel(self.param_model)

        layout.addWidget(self.param_list)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def setParameterList(self, paramlist):
        self.param_model.setParameterList(paramlist)

    def addParameter(self):
        self.param_model.insertRows(-1,1)

    def removeParameter(self):
        current = self.param_list.currentIndex()
        self.param_model.removeRows(current.row(), 1)

    def saveParameters(self): 
        print 'save to stim model'
        # this is the same model from stimulusview.model() we set in contructor
        # do I need to do this?
        self.param_model.parentModel().setAutoParams(self.param_model)

        self.param_model.stimView().setMode(0)
        self.close()

    def sizeHint(self):
        return QtCore.QSize(500,500)

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