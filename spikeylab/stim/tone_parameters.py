from PyQt4 import QtGui
from tone_parameters_form import Ui_ToneParameterWidget

class ToneParameterWidget(QtGui.QWidget, Ui_ToneParameterWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)

        self.tscale = 0.001 # display in ms
        self.fscale = 1000

    def setComponent(self, component):
        self.common.setFields(component)
        self.freq_spnbx.setValue(component.frequency()/self.fscale)
        self._component = component

    def saveToObject(self):
        self._component.setFrequency(self.freq_spnbx.value()*self.fscale)
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


class SilenceParameterWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.tscale = 0.001 # display in ms

        self.dur_spnbx = QtGui.QSpinBox()
        self.dur_spnbx.setRange(1,5000)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.dur_spnbx)

        self.setLayout(layout)


    def setComponent(self, component):
        self.dur_spnbx.setValue(component.duration()/self.tscale)
        self._component = component

    def saveToObject(self):
        self._component.setDuration(self.dur_spnbx.value()*self.tscale)

    def component(self):
        return self._component

    def setContentFocus(self):
        self.dur_spnbx.setFocus()
        self.dur_spnbx.selectAll()