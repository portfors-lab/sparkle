from PyQt4 import QtGui, QtCore

from common_parametersform import Ui_ParameterWidget
from spikeylab.gui.stim.abstract_component_editor import AbstractComponentWidget

class CommonParameterWidget(AbstractComponentWidget,Ui_ParameterWidget):
    """Widget that accepts input for parameters that all stimuli
     types have in common"""
    valueChanged = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.dbSpnbx.numtype = int

        self.tunit_labels.append(self.tunit_lbl_0)
        self.tunit_labels.append(self.tunit_lbl_1)
        self.tunit_fields.append(self.durSpnbx)
        self.tunit_fields.append(self.risefallSpnbx)
        # self.setTScale(self.scales[0], setup=True)
        # need to initialize units to current scale
        # relay editing signals
        self.dbSpnbx.valueChanged.connect(self.valueChanged.emit)
        self.durSpnbx.valueChanged.connect(self.valueChanged.emit)
        self.risefallSpnbx.valueChanged.connect(self.valueChanged.emit)

        self.durSpnbx.setKeyboardTracking(False)
        self.risefallSpnbx.setKeyboardTracking(False)

    def intensityValue(self):
        return self.dbSpnbx.value()

    def durationValue(self):
        return self.durSpnbx.value()*self.scales[0]

    def risefallValue(self):
        return self.risefallSpnbx.value()*self.scales[0]

    def setField(self, **field):
        if 'intensity' in field:
            self.dbSpnbx.setValue(field['intensity'])
        if 'duration' in field:
            self.durSpnbx.setValue(field['duration']/self.scales[0])
        if 'risefall' in field:
            self.risefallSpnbx.setValue(field['risefall']/self.scales[0])

    def setFields(self, component):
        """Set all the input fields to the values in the provided component"""
        self.dbSpnbx.setValue(component.intensity())
        self.durSpnbx.setValue(component.duration()/self.scales[0])
        self.risefallSpnbx.setValue(component.risefall()/self.scales[0])

        self.tunit_lbl_0.setText(component._labels[0])
        self.tunit_lbl_1.setText(component._labels[0])

    def getValue(self, field):
        if field == 'intensity':
            return self.dbSpnbx.value()
        if field == 'duration':
            return self.durSpnbx.value()*self.scales[0]
        if field == 'risefall':
            return self.risefallSpnbx.value()*self.scales[0]

    def setDuration(self, duration):
        self.durSpnbx.setValue(duration/self.scales[0])

    def fieldNames(self):
        """ Return the names of the fields this widget handles """
        return ['intensity', 'duration', 'risefall']
