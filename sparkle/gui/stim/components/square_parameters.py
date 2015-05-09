from sparkle.QtWrapper import QtGui
from sparkle.gui.stim.abstract_component_editor import AbstractComponentWidget
from sparkle.gui.stim.incrementer import IncrementInput
from sparkle.gui.stim.smart_spinbox import SmartSpinBox


class SquareWaveParameterWidget(AbstractComponentWidget):
    """Editor widget intended to work with (almost) any possible 
    stimulus component (well, or create a custom one if it doesn't)"""
    def __init__(self, component, parent=None):
        super(SquareWaveParameterWidget, self).__init__(parent)

        layout = QtGui.QGridLayout()

        self.setWindowTitle(component.name)

        details = component.auto_details()

        layout.addWidget(QtGui.QLabel('duration'), 0, 0)
        self.duration_input = SmartSpinBox()
        layout.addWidget(self.duration_input, 0, 1)
        self.duration_input.setMinimum(details['duration']['min'])
        self.duration_input.setMaximum(details['duration']['max'])
        self.duration_input.setScale(self._scales[0])
        self.tunit_fields.append(self.duration_input)
        self.duration_input.valueChanged.connect(self.valueChanged.emit)

        layout.addWidget(QtGui.QLabel('frequency'), 1, 0)
        self.freq_input = IncrementInput()
        layout.addWidget(self.freq_input, 1, 1)
        self.freq_input.setMinimum(details['frequency']['min'])
        self.freq_input.setMaximum(details['frequency']['max'])
        self.freq_input.setScale(self._scales[1])
        self.freq_input.valueChanged.connect(self.valueChanged.emit)

        amp_input_layout = QtGui.QHBoxLayout()
        self.amp_input = SmartSpinBox()
        self.amp_input.setMinimum(details['amplitude']['min'])
        self.amp_input.setMaximum(details['amplitude']['max'])
        self.amp_input.setScale('mV/V')
        self.amp_input.valueChanged.connect(self.valueChanged.emit)
        amp_input_layout.addWidget(self.amp_input)
        self.outVLabel = QtGui.QLabel('= ?V to amplifier')
        amp_input_layout.addWidget(self.outVLabel)
        self.amp_input.valueChanged.connect(self.updateConversionMessage)

        amp_box = QtGui.QGroupBox("Amplitude")
        scale_layout = QtGui.QHBoxLayout()
        scale_layout.addWidget(QtGui.QLabel("scaling:"))
        self.vradio = QtGui.QRadioButton("mV/V")
        self.aradio = QtGui.QRadioButton("pA/V")
        self.vradio.setChecked(True)
        scale_layout.addWidget(self.vradio)
        scale_layout.addWidget(self.aradio)
        scale_layout.addWidget(QtGui.QLabel("factor:"))
        self.amp_factor_input = SmartSpinBox()
        self.amp_factor_input.setSuffix(' mV/V')
        self.amp_factor_input.setMaximum(500000) #just something really high
        self.amp_factor_input.setValue(1000)
        self.amp_factor_input.valueChanged.connect(self.updateFactor)
        scale_layout.addWidget(self.amp_factor_input)
        self.btn_group = QtGui.QButtonGroup()
        self.btn_group.addButton(self.vradio)
        self.btn_group.addButton(self.aradio)
        self.btn_group.buttonClicked.connect(self.changeScale)

        join_layout = QtGui.QVBoxLayout()
        join_layout.addLayout(scale_layout)
        join_layout.addLayout(amp_input_layout)
        amp_box.setLayout(join_layout)

        editor_layout = QtGui.QVBoxLayout()
        editor_layout.addLayout(layout)
        editor_layout.addWidget(amp_box)
        editor_layout.addWidget(QtGui.QWidget()) # add empty widget to get spacing
        editor_layout.setStretch(2, 1)
        self.setLayout(editor_layout)

        self.setComponent(component)
        self.updateFactor(self.amp_factor_input.value())
        self.inputWidgets = {'duration': self.duration_input,
                             'frequency': self.freq_input,
                             'amplitude': self.amp_input}

    def setComponent(self, component):
        values = component.stateDict()
        self.duration_input.setValue(values['duration'])
        self.freq_input.setValue(values['frequency'])
        self.amp_input.setValue(values['amplitude'])
        self._component = component

    def saveToObject(self):
        self._component.set('duration', self.duration_input.value())
        self._component.set('frequency', self.freq_input.value())
        self._component.set('amplitude', self.amp_input.value())
        self.attributesSaved.emit(self._component.__class__.__name__, self._component.stateDict())

    def setContentFocus(self):
        """ Builder calls this to get cursor in editor"""
        self.duration_input.setFocus()
        self.duration_input.selectAll()

    def durationInputWidget(self):
        return self.duration_input

    def changeScale(self, button):
        self.amp_input.setScale(button.text())
        self.amp_factor_input.setSuffix(' '+button.text())
        self.amp_factor_input.setValue(self.amp_input.scalarFactor(button.text()))
        self.updateConversionMessage(0)

    def updateConversionMessage(self, val):
        outV = self.amp_input.value()
        self.outVLabel.setText("= {}V output to amplifier".format(outV))

    def updateFactor(self, val):
        self.amp_input.setScalarFactor(self.btn_group.checkedButton().text(), val)
        self.updateConversionMessage(0)
