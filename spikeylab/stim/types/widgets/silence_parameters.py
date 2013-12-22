from PyQt4 import QtGui
            
class SilenceParameterWidget(QtGui.QWidget):
    include_in_stack = False
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.tscale = 0.001 # display in ms

        self.dur_spnbx = QtGui.QSpinBox()
        self.dur_spnbx.setRange(1,5000)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.dur_spnbx)

        self.setLayout(layout)

    def setComponent(self, component):
        self.dur_spnbx.setValue(component.duration()/self.tscale)
        self._component = component

    def saveToObject(self):
        self._component.setDuration(self.dur_spnbx.value()*self.tscale)

    def component(self):
        return self._component

    def setContentFocus(self):
        self.dur_spnbx.setFocus()
        self.dur_spnbx.selectAll()
