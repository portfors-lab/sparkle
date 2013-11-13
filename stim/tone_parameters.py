from PyQt4 import QtGui
from tone_parameters_form import Ui_ToneParameterWidget

class ToneParameterWidget(QtGui.QWidget, Ui_ToneParameterWidget):
    def __init__(self, tone, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)

        self.tscale = 0.001 # display in ms
        self.fscale = 1000

        self.common.setFields(tone)
        self.freq_spnbx.setValue(tone.frequency()/self.fscale)
        self._component = tone
        

    def saveToObject(self):
        self._component.setFrequency(self.freq_spnbx.value()*self.fscale)
        self._component.setIntensity(self.common.intensityValue())
        self._component.setDuration(self.common.durationValue())
        self._component.setRisefall(self.common.risefallValue())
        self._component.setSamplerate(self.common.samplerateValue())

    def component(self):
        return self._component