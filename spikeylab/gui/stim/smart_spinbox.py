from PyQt4 import QtGui, QtCore
from numpy import floor

class SmartSpinBox(QtGui.QDoubleSpinBox):
    """Spin box that shows decimals only if value is not a whole number"""
    def __init__(self, parent=None):
        super(SmartSpinBox, self).__init__(parent)
        # this will cause valueChanged signal to emit only then
        # editing is finished
        self.setKeyboardTracking(False)

    def textFromValue(self, val):
        if val - floor(val) > 0.0:
            return str(val)
        else:
            return str(int(val))