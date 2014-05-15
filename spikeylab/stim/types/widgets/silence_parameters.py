from PyQt4 import QtGui
            
from spikeylab.stim.abstract_parameters import AbstractParameterWidget
from spikeylab.stim.incrementer import IncrementInput
from spikeylab.stim.smart_spinbox import SmartSpinBox
from spikeylab.stim.common_parameters import CommonParameterWidget
            
class SilenceParameterWidget(AbstractParameterWidget):
    include_in_stack = False
    def __init__(self, parent=None):
        super(SilenceParameterWidget, self).__init__(parent)

        self.dur_spnbx = SmartSpinBox()
        self.dur_spnbx.setRange(1,5000)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.dur_spnbx)

        self.setLayout(layout)
        self.setWindowTitle("Silence")

    def setComponent(self, component):
        self.dur_spnbx.setValue(component.duration()/self.scales[0])
        self._component = component

    def saveToObject(self):
        self._component.setDuration(self.dur_spnbx.value()*self.scales[0])
        self.attributes_saved.emit(self._component.__class__.__name__, self._component.stateDict())

    def setContentFocus(self):  
        self.dur_spnbx.setFocus()
        self.dur_spnbx.selectAll()

class NoiseParameterWidget(AbstractParameterWidget):
    def __init__(self, parent=None):
        super(NoiseParameterWidget, self).__init__(parent)

        self.common = CommonParameterWidget()

        # use grid layout for subclasses to add to 
        layout = QtGui.QGridLayout()

        layout.addWidget(self.common, 0,0,1,3)

        self.setLayout(layout)
        self.setWindowTitle("Noise")

        self.common.valueChanged.connect(self.valueChanged.emit)
        # self.valueChanged.connect(self.saveToObject)
        
    def setComponent(self, component):
        self.common.setFields(component)
        self._component = component

    def saveToObject(self):
        self._component.setIntensity(self.common.intensityValue())
        self._component.setDuration(self.common.durationValue())
        self._component.setRisefall(self.common.risefallValue())
        self.attributes_saved.emit(self._component.__class__.__name__, self._component.stateDict())

    def setContentFocus(self):
        self.common.dur_spnbx.setFocus()
        self.common.dur_spnbx.selectAll()

    def duration_input_widget(self):
        return self.common.dur_spnbx


class ChirpParameterWidget(NoiseParameterWidget):
    def __init__(self, parent=None):
        super(ChirpParameterWidget, self).__init__(parent)
        layout = self.layout()

        self.start_freq_spnbx = SmartSpinBox()
        self.start_freq_spnbx.setMaximum(110)
        self.stop_freq_spnbx = SmartSpinBox()
        self.stop_freq_spnbx.setMaximum(110)
        layout.addWidget(QtGui.QLabel("Start Frequency"), 2, 0)
        layout.addWidget(self.start_freq_spnbx, 2, 1)
        layout.addWidget(QtGui.QLabel("kHz"), 2, 2)
        layout.addWidget(QtGui.QLabel("Stop Frequency"), 3, 0)
        layout.addWidget(self.stop_freq_spnbx, 3, 1)
        layout.addWidget(QtGui.QLabel("kHz"), 3, 2)
        
        self.start_freq_spnbx.valueChanged.connect(self.valueChanged.emit)
        self.stop_freq_spnbx.valueChanged.connect(self.valueChanged.emit)
        self.start_freq_spnbx.setKeyboardTracking(False)
        self.stop_freq_spnbx.setKeyboardTracking(False)

    def setComponent(self, component):
        super(ChirpParameterWidget, self).setComponent(component)
        self.start_freq_spnbx.setValue(component.startFrequency()/self.scales[1])
        self.stop_freq_spnbx.setValue(component.stopFrequency()/self.scales[1])

    def saveToObject(self):
        self._component.setStartFrequency(self.start_freq_spnbx.value()*self.scales[1])
        self._component.setStopFrequency(self.stop_freq_spnbx.value()*self.scales[1])
        super(ChirpParameterWidget, self).saveToObject()