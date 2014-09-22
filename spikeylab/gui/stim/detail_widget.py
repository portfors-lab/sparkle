from PyQt4 import QtGui

from spikeylab.gui.stim.detail_form import Ui_StimDetailWidget

class StimDetailWidget(QtGui.QWidget):
    """Container widget for presenting Stimulus details from the doc"""
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self)
        self.ui = Ui_StimDetailWidget()
        self.ui.setupUi(self)

    def setTestNum(self, num):
        """Sets the Test number to display"""
        self.ui.testNum.setNum(num+1)

    def setTraceNum(self, num):
        """Sets the Trace number to display"""
        self.ui.traceNum.setNum(num+1)

    def setRepNum(self, num):
        """Sets the Repetition number to display"""
        self.ui.repNum.setNum(num+1)

    def setDoc(self, doc):
        """Presents the documentation

        :param doc: documentation for StimulusModel. i.e. returned from 
        :meth:`componentDoc<spikeylab.stim.stimulusmodel.StimulusModel.componentDoc>`
        or :meth:`templateDoc<spikeylab.stim.stimulusmodel.StimulusModel.templateDoc>`
        """
        self.ui.overAtten.setNum(doc['overloaded_attenuation'])
        # also set composite stim type
        # self.ui.traceType.setText(doc['testtype'])

        self.ui.componentDetails.clearDoc()
        self.ui.componentDetails.setDoc(doc['components'])

    def setDisplayAttributes(self, attrs):
        """Sets which attributes to display

        Actually just calls :meth:`setDisplayTable<spikeylab.gui.stim.component_detail.ComponentsDetailWidget.setDisplayTable>`
        """
        self.ui.componentDetails.setDisplayTable(attrs)