from PyQt4 import QtGui, QtCore

from spikeylab.stim.auto_parameter_modelview import AutoParameterDelegate, AutoParameterModel, AutoParamWidget



class Parametizer(QtGui.QWidget):
    def __init__(self, stimulusmodel, parent=None):
        QtGui.QWidget.__init__(self, parent)

        layout = QtGui.QVBoxLayout()
        btn_layout = QtGui.QHBoxLayout()
        
        add_btn = QtGui.QPushButton('Add')
        ok_btn = QtGui.QPushButton('OK')
        cancel_btn = QtGui.QPushButton('Cancel')
        add_btn.clicked.connect(self.addParameter)
        ok_btn.clicked.connect(self.saveParameters)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)

        self.param_list = QtGui.QListView()
        self.param_list.setItemDelegate(AutoParameterDelegate())
        # self.param_list.setEditTriggers(QtGui.QAbstractItemView.CurrentChanged)
        self.param_list.setAcceptDrops(True)
        # self.param_list.setDragEnabled(True)

        self.param_list.setDragDropMode(QtGui.QAbstractItemView.InternalMove)

        self.param_model = AutoParameterModel()
        self.param_model.setStimModel(stimulusmodel)
        self.param_list.setModel(self.param_model)

        layout.addWidget(self.param_list)
        layout.addLayout(btn_layout)
        self.setLayout(layout)


    def setParameterList(self, paramlist):
        self.param_model.setParameterList(paramlist)

    def addParameter(self):
        self.param_model.insertRows(-1,1)

    def saveParameters(self):
        print 'save to stim model'

    def sizeHint(self):
        return QtCore.QSize(500,500)

if __name__ == '__main__':
    import sys
    from spikeylab.stim.stimulusmodel import *

    app  = QtGui.QApplication(sys.argv)

    stim = StimulusModel()
    automagic = Parametizer(stim)
    automagic.show()

    app.exec_()