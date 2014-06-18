from PyQt4 import QtGui, QtCore
from numpy import floor

from incrementer_form import Ui_IncrementInput
from spikeylab.resources.icons import arrowup, arrowdown

class IncrementInput(QtGui.QWidget,Ui_IncrementInput):
    numtype = float
    minimum = 0
    maximum = 200000
    valueChanged = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)

        self.up10.setIcon(arrowup())
        self.up5.setIcon(arrowup())
        self.up1.setIcon(arrowup())
        self.down10.setIcon(arrowdown())
        self.down5.setIcon(arrowdown())
        self.down1.setIcon(arrowdown())
        # this will emit on partial values -- not what I want ideally
        self.value_lnedt.editingFinished.connect(self.checkInput)
        self.value_lnedt.editingFinished.connect(self.valueChanged.emit)

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
        val = self.numtype(self.value_lnedt.text())
        if self.minimum <= (val + n) <= self.maximum:
            val += n
            self.setValue(val)
        self.valueChanged.emit()

    def value(self):
        return self.numtype(self.value_lnedt.text())

    def setValue(self, val):
        # type and range checking here!
        if val - floor(val) > 0.0:
            self.value_lnedt.setText(str(val))
        else:
            self.value_lnedt.setText(str(int(val)))

    def checkInput(self):
        if self.value_lnedt.text() == '':
            self.setValue(0)

    def setDecimals(self, val):
        pass

    def setMaximum(self, val):
        self.maximum = val

    def setMinimum(self, val):
        self.minimum = val

    def sizeHint(self):
        return QtCore.QSize(450,45)

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    myapp = IncrementInput()
    myapp.show()
    sys.exit(app.exec_())