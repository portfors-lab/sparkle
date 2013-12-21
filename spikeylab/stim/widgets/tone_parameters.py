from PyQt4 import QtGui
from tone_parameters_form import Ui_ToneParameterWidget

from spikeylab.stim.abstract_parameters import AbstractParameterWidget

class ParameterWidget(AbstractParameterWidget, Ui_ToneParameterWidget):
    include_in_stack = True
    name = "Tone"

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        # include in class variable list of all unit labels
        self.funit_labels.append(self.funit_lbl)

    def setComponent(self, component):
        self.common.setFields(component)
        self.freq_spnbx.setValue(component.frequency()/self.scales[1])
        self._component = component

    def saveToObject(self):
        self._component.setFrequency(self.freq_spnbx.value()*self.scales[1])
        self._component.setIntensity(self.common.intensityValue())
        self._component.setDuration(self.common.durationValue())
        self._component.setRisefall(self.common.risefallValue())

    def intensityValue(self):
        return self.common.intensityValue()

    def durationValue(self):
        return self.common.durationValue()

    def risefallValue(self):
        return self.common.risefallValue()

    def component(self):
        return self._component

    def setIntensity(self, db):
        self.common.setField(intensity=db)

    def setRisefall(self, rf):
        self.common.setField(risefall=rf)

    def setDuration(self, dur):
        self.common.setField(duration=dur)

    def setContentFocus(self):
        self.freq_spnbx.setFocus()
        # self.freq_spnbx.selectAll()

    def inputsDict(self):
        inputs = {
            'freq': self.freq_spnbx.value(),
            'db': self.intensityValue(),
            'dur': self.durationValue(),
            'rf' : self.risefallValue()
            }
        return inputs

    def loadInputsDict(self, inputs):
        try:
            self.setIntensity(inputs.get('db', 60))
            self.setDuration(inputs.get('dur', 200))
            self.setRisefall(inputs.get('rf', 0))
            self.freq_spnbx.setValue(inputs.get('freq', 5))
        except:
            print 'failure to initize', self.name, 'inputs'
            raise
