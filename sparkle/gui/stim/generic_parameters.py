from sparkle.QtWrapper import QtGui
from sparkle.gui.stim.abstract_component_editor import AbstractComponentWidget
from sparkle.gui.stim.incrementer import IncrementInput
from sparkle.gui.stim.smart_spinbox import SmartSpinBox


class GenericParameterWidget(AbstractComponentWidget):
    """Editor widget intended to work with (almost) any possible 
    stimulus component (well, or create a custom one if it doesn't)"""
    def __init__(self, component, parent=None):
        super(GenericParameterWidget, self).__init__(parent)

        layout = QtGui.QGridLayout(self)

        self.setWindowTitle(component.name)

        row_counter = 0
        self.inputWidgets = {}
        for field, details in component.auto_details().items():

            if field in ['frequency', 'intensity']:
                # special case field should get incrementer
                inpt = IncrementInput()
                layout.addWidget(QtGui.QLabel(field), row_counter, 0)
            else:
                inpt = SmartSpinBox()
                layout.addWidget(QtGui.QLabel(details.get('text', field)), row_counter, 0)
            layout.addWidget(inpt, row_counter, 1)
            row_counter +=1
            # set the max and min
            inpt.setMinimum(details['min'])
            inpt.setMaximum(details['max'])  
             
            # if the label is the same as the the special labels of 
            # time or frequency add to list to be updated with scaling change
            if details['unit'] == 's':
                self.tunit_fields.append(inpt)
                inpt.setScale(self._scales[0])
            elif details['unit'] == 'Hz':
                self.funit_fields.append(inpt)
                inpt.setScale(self._scales[1])
            else:
                inpt.setScale(details['unit'])

            inpt.valueChanged.connect(self.valueChanged.emit)
            self.inputWidgets[field] = inpt
        layout.setRowStretch(row_counter, 1)

        self.setComponent(component)

    def setComponent(self, component):
        """Re-implemented from :meth:`AbstractComponentWidget<sparkle.gui.stim.abstract_component_editor.AbstractComponentWidget.setComponent>`"""
        details = component.auto_details()
        state = component.stateDict()
        for field, detail in details.items():
            val = state[field]
            self.inputWidgets[field].setValue(val)
        self._component = component

    def saveToObject(self):
        """Re-implemented from :meth:`AbstractComponentWidget<sparkle.gui.stim.abstract_component_editor.AbstractComponentWidget.saveToObject>`"""
        details = self._component.auto_details()
        for field, widget in self.inputWidgets.items():
            self._component.set(field, widget.value())
        self.attributesSaved.emit(self._component.__class__.__name__, self._component.stateDict())

    def setContentFocus(self):
        """Builder calls this to get cursor in editor"""
        self.inputWidgets['duration'].setFocus()
        self.inputWidgets['duration'].selectAll()

    def durationInputWidget(self):
        """Gets the widget responsible for duration input"""
        if 'duration' in self.inputWidgets:
            return self.inputWidgets['duration']
