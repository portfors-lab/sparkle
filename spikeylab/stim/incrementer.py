from PyQt4 import QtGui
from numpy import floor

from incrementer_form import Ui_IncrementInput
from spikeylab.resources.icons import arrowup, arrowdown

class IncrementInput(QtGui.QWidget,Ui_IncrementInput):
    numtype = float
    minimum = 0
    maximum = 200000
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.setStyleSheet("IncrementInput { background-color: white; \
                            border-top:1px inset lightgrey; \
                            border-right:1px inset lightgrey}\
                            ")
        self.up10.setIcon(arrowup())
        self.up1.setIcon(arrowup())
        self.down10.setIcon(arrowdown())
        self.down1.setIcon(arrowdown())

    def increment1(self):
        self.incrementn(1)

    def increment10(self):
        self.incrementn(10)

    def decrement1(self):
        self.incrementn(-1)

    def decrement10(self):
        self.incrementn(-10)

    def incrementn(self, n):
        val = self.numtype(self.value_lnedt.text())
        if self.minimum <= (val + n) <= self.maximum:
            val += n
            self.setValue(val)

    def value(self):
        return self.numtype(self.value_lnedt.text())

    def setValue(self, val):
        # type and range checking here!
        if val - floor(val) > 0.0:
            self.value_lnedt.setText(str(val))
        else:
            self.value_lnedt.setText(str(int(val)))

    def paintEvent(self, event):
        o = QtGui.QStyleOption()
        o.initFrom(self)
        p = QtGui.QPainter(self)
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, o, p, self)

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    myapp = IncrementInput()
    myapp.show()
    sys.exit(app.exec_())