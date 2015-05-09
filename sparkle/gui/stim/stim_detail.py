from sparkle.QtWrapper import QtGui
from sparkle.gui.stim.stim_detail_form import Ui_StimDetailWidget


class StimDetailWidget(QtGui.QWidget):
    """Container widget for presenting Stimulus details from the doc"""
    def __init__(self, parent=None):
        super(StimDetailWidget, self).__init__(parent)
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
        :meth:`componentDoc<sparkle.stim.stimulus_model.StimulusModel.componentDoc>`
        or :meth:`templateDoc<sparkle.stim.stimulus_model.StimulusModel.templateDoc>`
        """
        self.ui.overAtten.setNum(doc['overloaded_attenuation'])
        # also set composite stim type
        # self.ui.traceType.setText(doc['testtype'])

        self.ui.componentDetails.clearDoc()
        self.ui.componentDetails.setDoc(doc['components'])

    def setDisplayAttributes(self, attrs):
        """Sets which attributes to display

        Actually just calls :meth:`setDisplayTable<sparkle.gui.stim.component_detail.ComponentsDetailWidget.setDisplayTable>`
        """
        self.ui.componentDetails.setDisplayTable(attrs)
