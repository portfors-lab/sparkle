from PyQt4 import QtGui
from incrementer_form import Ui_IncrementInput

class IncrementInput(QtGui.QWidget,Ui_IncrementInput):
    numtype = int
    minimum = 0
    maximum = 100
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)

    def increment1(self):
        val = self.numtype(self.value_lnedt.text())
        if (val + 1) <= self.maximum:
            val += 1
            self.value_lnedt.setText(str(val))

    def increment10(self):
        val = self.numtype(self.value_lnedt.text())
        if (val + 10) <= self.maximum:
            val += 10
            self.value_lnedt.setText(str(val))

    def decrement1(self):
        val = self.numtype(self.value_lnedt.text())
        if val - 1 >= self.minimum:
            val -= 1
            self.value_lnedt.setText(str(val))

    def decrement10(self):
        val = self.numtype(self.value_lnedt.text())
        if val - 10 >= self.minimum:
            val -= 10
            self.value_lnedt.setText(str(val))

    def incrementn(self, n):
        val = self.numtype(self.value_lnedt.text())
        if (val + n) <= self.maximum:
            val += n

    def value(self):
        return self.numtype(self.value_lnedt.text())

    def setValue(self, val):
        self.value_lnedt.setText(str(val))


if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    myapp = IncrementInput()
    myapp.show()
    sys.exit(app.exec_())