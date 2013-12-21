from PyQt4 import QtGui

from common_parametersform import Ui_ParameterWidget
from spikeylab.stim.abstract_parameters import AbstractParameterWidget

class CommonParameterWidget(AbstractParameterWidget,Ui_ParameterWidget):
    """ Widget that accepts input for parameters that all stimuli
     types have in common"""
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.tunit_labels.append(self.tunit_lbl_0)
        self.tunit_labels.append(self.tunit_lbl_1)

    def intensityValue(self):
        return self.db_spnbx.value()

    def durationValue(self):
        return self.dur_spnbx.value()*self.scales[0]

    def risefallValue(self):
        return self.risefall_spnbx.value()*self.scales[0]

    def setField(self, **field):
        if 'intensity' in field:
            self.db_spnbx.setValue(field['intensity'])
        if 'duration' in field:
            self.dur_spnbx.setValue(field['duration']/self.scales[0])
        if 'risefall' in field:
            self.risefall_spnbx.setValue(field['risefall']/self.scales[0])

    def setFields(self, component):
        """Set all the input fields to the values in the provided component"""
        self.db_spnbx.setValue(component.intensity())
        self.dur_spnbx.setValue(component.duration()/self.scales[0])
        self.risefall_spnbx.setValue(component.risefall()/self.scales[0])

    def setDuration(self, duration):
        self.dur_spnbx.setValue(duration/self.scales[0])
