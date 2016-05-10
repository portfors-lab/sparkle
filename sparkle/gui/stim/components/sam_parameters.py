from sparkle.QtWrapper import QtGui
from sparkle.gui.stim.abstract_component_editor import AbstractComponentWidget
from sparkle.gui.stim.incrementer import IncrementInput
from sparkle.gui.stim.smart_spinbox import SmartSpinBox


class SAMParametersWidget(AbstractComponentWidget):
    def __init__(self, component, parent=None):
        super(SAMParametersWidget, self).__init__(parent)

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

        layout.addWidget(QtGui.QLabel('risefall'), 1, 0)
        self.risefall_input = SmartSpinBox()
        layout.addWidget(self.risefall_input, 1, 1)
        self.risefall_input.setMinimum(details['risefall']['min'])
        self.risefall_input.setMaximum(details['risefall']['max'])
        self.risefall_input.setScale(self._scales[0])
        self.tunit_fields.append(self.risefall_input)
        self.risefall_input.valueChanged.connect(self.valueChanged.emit)

        layout.addWidget(QtGui.QLabel('intensity'), 2, 0)
        self.intensity_input = IncrementInput()
        layout.addWidget(self.intensity_input, 2, 1)
        self.intensity_input.setMinimum(details['intensity']['min'])
        self.intensity_input.setMaximum(details['intensity']['max'])
        self.intensity_input.setScale('dB SPL')
        self.intensity_input.valueChanged.connect(self.valueChanged.emit)

        layout.addWidget(QtGui.QLabel('frequency'), 3, 0)
        self.freq_input = IncrementInput()
        layout.addWidget(self.freq_input, 3, 1)
        self.freq_input.setMinimum(details['frequency']['min'])
        self.freq_input.setMaximum(details['frequency']['max'])
        self.freq_input.setScale(self._scales[1])
        self.freq_input.valueChanged.connect(self.valueChanged.emit)

        layout.addWidget(QtGui.QLabel('modulation frequency'), 4, 0)
        self.mod_freq_input = IncrementInput()
        layout.addWidget(self.mod_freq_input, 4, 1)
        self.mod_freq_input.setMinimum(details['mod_frequency']['min'])
        self.mod_freq_input.setMaximum(details['mod_frequency']['max'])
        self.mod_freq_input.setScale(self._scales[1])
        self.mod_freq_input.valueChanged.connect(self.valueChanged.emit)

        layout.addWidget(QtGui.QLabel('modulation index'), 5, 0)
        self.modulation_input = SmartSpinBox()
        layout.addWidget(self.modulation_input, 5, 1)
        self.modulation_input.setMinimum(details['modulation']['min'])
        self.modulation_input.setMaximum(details['modulation']['max'])
        self.modulation_input.setScale('%')
        self.tunit_fields.append(self.modulation_input)
        self.modulation_input.valueChanged.connect(self.valueChanged.emit)

        editor_layout = QtGui.QVBoxLayout()
        editor_layout.addLayout(layout)
        # editor_layout.addWidget(amp_box)
        editor_layout.addWidget(QtGui.QWidget())  # add empty widget to get spacing
        editor_layout.setStretch(1, 1)
        self.setLayout(editor_layout)

        self.setComponent(component)
        self.inputWidgets = {'duration': self.duration_input,
                             'risefall': self.risefall_input,
                             'intensity': self.intensity_input,
                             'frequency': self.freq_input,
                             'mod_frequency': self.mod_freq_input,
                             'modulation': self.modulation_input}

    def setComponent(self, component):
        values = component.stateDict()
        self.duration_input.setValue(values['duration'])
        self.risefall_input.setValue(values['risefall'])
        self.intensity_input.setValue(values['intensity'])
        self.freq_input.setValue(values['frequency'])
        self.mod_freq_input.setValue(values['mod_frequency'])
        self.modulation_input.setValue(values['modulation'])
        self._component = component

    def saveToObject(self):
        self._component.set('duration', self.duration_input.value())
        self._component.set('risefall', self.risefall_input.value())
        self._component.set('intensity', self.intensity_input.value())
        self._component.set('frequency', self.freq_input.value())
        self._component.set('mod_frequency', self.mod_freq_input.value())
        self._component.set('modulation', self.modulation_input.value())
        self.attributesSaved.emit(self._component.__class__.__name__, self._component.stateDict())

    def setContentFocus(self):
        """ Builder calls this to get cursor in editor"""
        self.duration_input.setFocus()
        self.duration_input.selectAll()

    def durationInputWidget(self):
        return self.duration_input

    def changeScale(self, button):
        self.amp_input.setScale(button.text())
        self.amp_factor_input.setSuffix(' ' + button.text())
        self.amp_factor_input.setValue(self.amp_input.scalarFactor(button.text()))
        self.updateConversionMessage(0)

    def updateConversionMessage(self, val):
        outV = self.amp_input.value()
        self.outVLabel.setText("= {}V output to amplifier".format(outV))

    def updateFactor(self, val):
        self.amp_input.setScalarFactor(self.btn_group.checkedButton().text(), val)
        self.updateConversionMessage(0)
