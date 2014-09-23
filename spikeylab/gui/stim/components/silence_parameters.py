from PyQt4 import QtGui
            
from spikeylab.gui.stim.abstract_component_editor import AbstractComponentWidget
from spikeylab.gui.stim.incrementer import IncrementInput
from spikeylab.gui.stim.smart_spinbox import SmartSpinBox
            
class SilenceParameterWidget(AbstractComponentWidget):
    include_in_stack = False
    def __init__(self, parent=None):
        super(SilenceParameterWidget, self).__init__(parent)

        self.dur_spnbx = SmartSpinBox()
        self.dur_spnbx.setRange(1,5000)
        self.dur_spnbx.setDecimals(3)
        layout = QtGui.QGridLayout(self)
        layout.addWidget(QtGui.QLabel("Duration"), 0, 0)
        layout.addWidget(self.dur_spnbx, 0, 1)
        self.tunit_label = QtGui.QLabel("ms")
        layout.addWidget(self.tunit_label, 0, 2)

        self.setLayout(layout)
        self.setWindowTitle("Silence")

    def setComponent(self, component):
        details = component.auto_details()
        self.dur_spnbx.setMinimum(details['duration']['min']/self.scales[0])
        self.dur_spnbx.setValue(component.duration()/self.scales[0])
        self.dur_spnbx.setMaximum(details['duration']['max']/self.scales[0])
        self.tunit_label.setText(details['duration']['label'])
        self._component = component

    def saveToObject(self):
        self._component.setDuration(self.dur_spnbx.value()*self.scales[0])
        self.attributes_saved.emit(self._component.__class__.__name__, self._component.stateDict())

    def setContentFocus(self):  
        self.dur_spnbx.setFocus()
        self.dur_spnbx.selectAll()

