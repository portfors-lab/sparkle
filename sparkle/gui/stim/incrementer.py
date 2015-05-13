from numpy import floor

from incrementer_form import Ui_IncrementInput
from sparkle.QtWrapper import QtCore, QtGui
from sparkle.resources.icons import arrowdown, arrowup


class IncrementInput(QtGui.QWidget,Ui_IncrementInput):
    """Input widget with buttons to increment the value in the 
    field by 1,5, or 10"""
    numtype = float
    valueChanged = QtCore.Signal()
    def __init__(self, parent=None):
        super(IncrementInput, self).__init__(parent)
        self.setupUi(self)

        self.up10.setIcon(arrowup())
        self.up5.setIcon(arrowup())
        self.up1.setIcon(arrowup())
        self.down10.setIcon(arrowdown())
        self.down5.setIcon(arrowdown())
        self.down1.setIcon(arrowdown())

        self.valueSpnbx.valueChanged.connect(self.valueChanged.emit)

        # shortcut to propagate methods for spinbox
        for m in ['setValue', 'setMaximum', 'maximum', 'setMinimum', 'minimum', 'value', 'setDecimals', 'decimals', 'setScale']:
            setattr(self, m, getattr(self.valueSpnbx, m))

    def increment1(self):
        self.incrementn(1)

    def increment5(self):
        self.incrementn(5)

    def increment10(self):
        self.incrementn(10)

    def decrement1(self):
        self.incrementn(-1)

    def decrement5(self):
        self.incrementn(-5)

    def decrement10(self):
        self.incrementn(-10)

    def incrementn(self, n):
        self.valueSpnbx.setValue(self.valueSpnbx.value() + (n*self.valueSpnbx.currentScale()))

    def sizeHint(self):
        return QtCore.QSize(450,45)


if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    myapp = IncrementInput()
    myapp.show()
    sys.exit(app.exec_())
