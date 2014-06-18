from PyQt4 import QtGui, QtCore

from spikeylab.stim.abstract_parameters import AbstractParameterWidget
from spikeylab.stim.smart_spinbox import SmartSpinBox
from spikeylab.stim.incrementer import IncrementInput

class GenericParameterWidget(AbstractParameterWidget):
    
    def __init__(self, component, parent=None):
        super(GenericParameterWidget, self).__init__(parent)

        layout = QtGui.QGridLayout(self)

        self.setWindowTitle(component.name)

        row_counter = 0
        details = component.auto_details()
        self.input_widgets = {}
        for field, details in component.auto_details().items():

            if field in ['frequency', 'intensity']:
                # special case field should get incrementer
                inpt = IncrementInput()
                layout.addWidget(QtGui.QLabel(field), row_counter, 0)
                layout.addWidget(inpt, row_counter, 1)
                lbl = QtGui.QLabel(details['label'])
                layout.addWidget(lbl, row_counter, 2)
            else:
                inpt = SmartSpinBox()
                layout.addWidget(QtGui.QLabel(details.get('text', field)), row_counter, 0)
                layout.addWidget(inpt, row_counter, 1)
                lbl = QtGui.QLabel(details['label'])
                layout.addWidget(lbl, row_counter, 2)
                # set the max and min
                inpt.setMinimum(details['min']/details['multiplier'])
                inpt.setMaximum(details['max']/details['multiplier'])
            row_counter +=1
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
        layout.setRowStretch(row_counter, 1)

        self.setComponent(component)

    def setComponent(self, component):
        details = component.auto_details()
        state = component.stateDict()
        for field, detail in details.items():
            val = state[field]
            self.input_widgets[field].setValue(val/detail['multiplier'])
        self._component = component

    def saveToObject(self):
        details = self._component.auto_details()
        for field, widget in self.input_widgets.items():
            self._component.set(field, widget.value()*details[field]['multiplier'])
        self.attributes_saved.emit(self._component.__class__.__name__, self._component.stateDict())

    def setContentFocus(self):
        """ Builder calls this to get cursor in editor"""
        self.input_widgets['duration'].setFocus()
        self.input_widgets['duration'].selectAll()

    def duration_input_widget(self):
        return self.input_widgets['duration']

