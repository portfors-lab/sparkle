from PyQt4 import QtGui
            
from spikeylab.stim.abstract_parameters import AbstractParameterWidget
from spikeylab.stim.incrementer import IncrementInput
            
class SilenceParameterWidget(AbstractParameterWidget):
    include_in_stack = False
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.dur_spnbx = QtGui.QSpinBox()
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

    def component(self):
        return self._component

    def setContentFocus(self):  
        self.dur_spnbx.setFocus()
        self.dur_spnbx.selectAll()

class NoiseParameterWidget(AbstractParameterWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.db_spnbx = IncrementInput()
        self.dur_spnbx = QtGui.QSpinBox()
        self.dur_spnbx.setRange(1,5000)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.db_spnbx)
        layout.addWidget(self.dur_spnbx)
        layout.addStretch(1)

        self.setLayout(layout)
        self.setWindowTitle("Silence")

    def setComponent(self, component):
        self.dur_spnbx.setValue(component.duration()/self.scales[0])
        self.db_spnbx.setValue(component.intensity())
        self._component = component

    def saveToObject(self):
        self._component.setDuration(self.dur_spnbx.value()*self.scales[0])
        self._component.setIntensity(self.db_spnbx.value())

    def component(self):
        return self._component

    def setContentFocus(self):
        self.dur_spnbx.setFocus()
        self.dur_spnbx.selectAll()