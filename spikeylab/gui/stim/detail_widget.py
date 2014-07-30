from PyQt4 import QtGui

from spikeylab.gui.stim.detail_form import Ui_StimDetailWidget

class StimDetailWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self)
        self.ui = Ui_StimDetailWidget()
        self.ui.setupUi(self)

    def setTestNum(self, num):
        self.ui.testNum.setNum(num+1)

    def setTraceNum(self, num):
        self.ui.traceNum.setNum(num+1)

    def setRepNum(self, num):
        self.ui.repNum.setNum(num+1)

    def setDoc(self, doc):
        self.ui.overAtten.setNum(doc['overloaded_attenuation'])
        # also set composite stim type
        self.ui.traceType.setText(doc['testtype'])

        self.ui.componentDetails.clearDoc()
        self.ui.componentDetails.setDoc(doc['components'])

    def setDisplayAttributes(self, attrs):
        self.ui.componentDetails.setDisplayTable(attrs)