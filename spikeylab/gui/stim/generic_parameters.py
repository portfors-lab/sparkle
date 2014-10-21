from QtWrapper import QtGui

from spikeylab.gui.stim.abstract_component_editor import AbstractComponentWidget
from spikeylab.gui.stim.smart_spinbox import SmartSpinBox
from spikeylab.gui.stim.incrementer import IncrementInput

class GenericParameterWidget(AbstractComponentWidget):
    """Editor widget intended to work with (almost) any possible 
    stimulus component (well, or create a custom one if it doesn't)"""
    def __init__(self, component, parent=None):
        super(GenericParameterWidget, self).__init__(parent)

        layout = QtGui.QGridLayout(self)

        self.setWindowTitle(component.name)

        row_counter = 0
        details = component.auto_details()
        self.inputWidgets = {}
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
            self.inputWidgets[field] = inpt
        layout.setRowStretch(row_counter, 1)

        self.setComponent(component)

    def setComponent(self, component):
        """Re-implemented from :meth:`AbstractComponentWidget<spikeylab.gui.stim.abstract_component_editor.AbstractComponentWidget.setComponent>`"""
        details = component.auto_details()
        state = component.stateDict()
        for field, detail in details.items():
            val = state[field]
            self.inputWidgets[field].setValue(val/detail['multiplier'])
        self._component = component

    def saveToObject(self):
        """Re-implemented from :meth:`AbstractComponentWidget<spikeylab.gui.stim.abstract_component_editor.AbstractComponentWidget.saveToObject>`"""
        details = self._component.auto_details()
        for field, widget in self.inputWidgets.items():
            self._component.set(field, widget.value()*details[field]['multiplier'])
        self.attributesSaved.emit(self._component.__class__.__name__, self._component.stateDict())

    def setContentFocus(self):
        """ Builder calls this to get cursor in editor"""
        self.inputWidgets['duration'].setFocus()
        self.inputWidgets['duration'].selectAll()

    def durationInputWidget(self):
        """Gets the widget responsible for duration input"""
        return self.inputWidgets['duration']

