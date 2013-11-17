# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\incrementer.ui'
#
# Created: Tue Oct 22 13:46:02 2013
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_IncrementInput(object):
    def setupUi(self, IncrementInput):
        IncrementInput.setObjectName(_fromUtf8("IncrementInput"))
        IncrementInput.resize(410, 48)
        self.horizontalLayout = QtGui.QHBoxLayout(IncrementInput)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.value_lnedt = QtGui.QLineEdit(IncrementInput)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.value_lnedt.sizePolicy().hasHeightForWidth())
        self.value_lnedt.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.value_lnedt.setFont(font)
        self.value_lnedt.setObjectName(_fromUtf8("value_lnedt"))
        self.horizontalLayout.addWidget(self.value_lnedt)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.pushButton = QtGui.QPushButton(IncrementInput)
        self.pushButton.setMinimumSize(QtCore.QSize(20, 0))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.gridLayout.addWidget(self.pushButton, 0, 0, 1, 1)
        self.pushButton_3 = QtGui.QPushButton(IncrementInput)
        self.pushButton_3.setMinimumSize(QtCore.QSize(20, 0))
        self.pushButton_3.setObjectName(_fromUtf8("pushButton_3"))
        self.gridLayout.addWidget(self.pushButton_3, 0, 1, 1, 1)
        self.pushButton_2 = QtGui.QPushButton(IncrementInput)
        self.pushButton_2.setMinimumSize(QtCore.QSize(20, 0))
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.gridLayout.addWidget(self.pushButton_2, 1, 0, 1, 1)
        self.pushButton_4 = QtGui.QPushButton(IncrementInput)
        self.pushButton_4.setMinimumSize(QtCore.QSize(20, 0))
        self.pushButton_4.setObjectName(_fromUtf8("pushButton_4"))
        self.gridLayout.addWidget(self.pushButton_4, 1, 1, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout)

        self.retranslateUi(IncrementInput)
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), IncrementInput.increment10)
        QtCore.QObject.connect(self.pushButton_2, QtCore.SIGNAL(_fromUtf8("clicked()")), IncrementInput.decrement10)
        QtCore.QObject.connect(self.pushButton_3, QtCore.SIGNAL(_fromUtf8("clicked()")), IncrementInput.increment1)
        QtCore.QObject.connect(self.pushButton_4, QtCore.SIGNAL(_fromUtf8("clicked()")), IncrementInput.decrement1)
        QtCore.QMetaObject.connectSlotsByName(IncrementInput)

    def retranslateUi(self, IncrementInput):
        IncrementInput.setWindowTitle(_translate("IncrementInput", "Form", None))
        self.value_lnedt.setText(_translate("IncrementInput", "0", None))
        self.pushButton.setText(_translate("IncrementInput", "^10", None))
        self.pushButton_3.setText(_translate("IncrementInput", "^1", None))
        self.pushButton_2.setText(_translate("IncrementInput", "v", None))
        self.pushButton_4.setText(_translate("IncrementInput", "v", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    IncrementInput = QtGui.QWidget()
    ui = Ui_IncrementInput()
    ui.setupUi(IncrementInput)
    IncrementInput.show()
    sys.exit(app.exec_())

