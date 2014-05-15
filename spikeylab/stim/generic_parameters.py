from PyQt4 import QtGui, QtCore

from spikeylab.stim.abstract_parameters import AbstractParameterWidget
from spikeylab.stim.smart_spinbox import SmartSpinBox
from spikeylab.stim.incrementer import IncrementInput
from spikeylab.stim.common_parameters import CommonParameterWidget

class GenericParameterWidget(AbstractParameterWidget):
    
    def __init__(self, component, parent=None):
        super(GenericParameterWidget, self).__init__(parent)

        layout = QtGui.QGridLayout(self)
        self.common = CommonParameterWidget()
        layout.addWidget(self.common, 1,0,1,3)

        self.setWindowTitle(component.name)
        self.common.valueChanged.connect(self.valueChanged.emit)
        
        # create a field for each parameter
        # special cases for field keys intensity and frequency
        common_fields = self.common.fieldNames()
        row_counter = 2
        details = component.auto_details()
        self.input_widgets = {}
        for field, details in component.auto_details().items():
            if field in common_fields:
                pass # already handled
            else:
                if field == 'frequency':
                    # special case frequency field should get incrementer
                    inpt = IncrementInput()
                    layout.addWidget(QtGui.QLabel(field), 0, 0)
                    layout.addWidget(inpt, 0, 1)
                    lbl = QtGui.QLabel(details['label'])
                    layout.addWidget(lbl, 0, 2)
                else:
                    inpt = SmartSpinBox()
                    layout.addWidget(QtGui.QLabel(details.get('text', field)), row_counter, 0)
                    layout.addWidget(inpt, row_counter, 1)
                    lbl = QtGui.QLabel(details['label'])
                    layout.addWidget(lbl, row_counter, 2)
                    row_counter +=1
                    # set the max and min
                    inpt.setMinimum(details['min'])
                    inpt.setMaximum(details['max'])
                # if the label is the same as the the special labels of 
                # time or frequency add to list to be updated with scaling change
                if details['label'] == component._labels[0]:
                    self.tunit_labels.append(lbl)
                    self.tunit_fields.append(inpt)
                elif details['label'] == component._labels[1]:
                    self.funit_labels.append(lbl)
                    self.funit_fields.append(inpt)
                inpt.valueChanged.connect(self.valueChanged.emit)
                self.input_widgets[field] = inpt

        self.setComponent(component)

    def setComponent(self, component):
        self.common.setFields(component)
        common_fields = self.common.fieldNames()
        details = component.auto_details()
        params = component.stateDict()
        for field, val in params.items():
            if field in common_fields or field == 'stim_type':
                pass # already handled
            else:
                self.input_widgets[field].setValue(val/details[field]['multiplier'])
        self._component = component

    def saveToObject(self):
        common_fields = self.common.fieldNames()
        for field in common_fields:
            self._component.set(field, self.common.getValue(field))
            
        details = self._component.auto_details()
        for field, widget in self.input_widgets.items():
            self._component.set(field, widget.value()*details[field]['multiplier'])
        self.attributes_saved.emit(self._component.__class__.__name__, self._component.stateDict())

    def setContentFocus(self):
        """ Builder calls this to get cursor in editor"""
        self.common.dur_spnbx.setFocus()
        self.common.dur_spnbx.selectAll()

    def duration_input_widget(self):
        return self.common.dur_spnbx
