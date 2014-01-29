# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\incrementer.ui'
#
# Created: Tue Jan 28 19:28:49 2014
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
        IncrementInput.resize(371, 51)
        IncrementInput.setAutoFillBackground(True)
        IncrementInput.setStyleSheet(_fromUtf8(""))
        self.horizontalLayout = QtGui.QHBoxLayout(IncrementInput)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(0, 1, 1, 0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.value_lnedt = QtGui.QLineEdit(IncrementInput)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.value_lnedt.sizePolicy().hasHeightForWidth())
        self.value_lnedt.setSizePolicy(sizePolicy)
        self.value_lnedt.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.value_lnedt.setFont(font)
        self.value_lnedt.setStyleSheet(_fromUtf8("border: none"))
        self.value_lnedt.setObjectName(_fromUtf8("value_lnedt"))
        self.horizontalLayout.addWidget(self.value_lnedt)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setSpacing(0)
        self.gridLayout.setContentsMargins(-1, 1, 1, 1)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.down10 = QtGui.QPushButton(IncrementInput)
        self.down10.setMinimumSize(QtCore.QSize(20, 0))
        self.down10.setMaximumSize(QtCore.QSize(50, 16777215))
        self.down10.setStyleSheet(_fromUtf8("QWidget { background-color:rgb(234, 234, 234); }"))
        self.down10.setObjectName(_fromUtf8("down10"))
        self.gridLayout.addWidget(self.down10, 2, 0, 1, 1)
        self.up10 = QtGui.QPushButton(IncrementInput)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.up10.sizePolicy().hasHeightForWidth())
        self.up10.setSizePolicy(sizePolicy)
        self.up10.setMinimumSize(QtCore.QSize(30, 0))
        self.up10.setMaximumSize(QtCore.QSize(50, 16777215))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.up10.setFont(font)
        self.up10.setStyleSheet(_fromUtf8("QWidget { background-color:rgb(234, 234, 234); }"))
        self.up10.setObjectName(_fromUtf8("up10"))
        self.gridLayout.addWidget(self.up10, 1, 0, 1, 1)
        self.up1 = QtGui.QPushButton(IncrementInput)
        self.up1.setMinimumSize(QtCore.QSize(30, 0))
        self.up1.setMaximumSize(QtCore.QSize(50, 16777215))
        self.up1.setStyleSheet(_fromUtf8("QWidget { background-color:rgb(234, 234, 234); }"))
        self.up1.setObjectName(_fromUtf8("up1"))
        self.gridLayout.addWidget(self.up1, 1, 2, 1, 1)
        self.down1 = QtGui.QPushButton(IncrementInput)
        self.down1.setMinimumSize(QtCore.QSize(20, 0))
        self.down1.setMaximumSize(QtCore.QSize(50, 16777215))
        self.down1.setStyleSheet(_fromUtf8("QWidget { background-color:rgb(234, 234, 234); }"))
        self.down1.setObjectName(_fromUtf8("down1"))
        self.gridLayout.addWidget(self.down1, 2, 2, 1, 1)
        self.up5 = QtGui.QPushButton(IncrementInput)
        self.up5.setMinimumSize(QtCore.QSize(20, 0))
        self.up5.setMaximumSize(QtCore.QSize(50, 16777215))
        self.up5.setStyleSheet(_fromUtf8("QWidget { background-color:rgb(234, 234, 234); }"))
        self.up5.setObjectName(_fromUtf8("up5"))
        self.gridLayout.addWidget(self.up5, 1, 1, 1, 1)
        self.down5 = QtGui.QPushButton(IncrementInput)
        self.down5.setMinimumSize(QtCore.QSize(20, 0))
        self.down5.setMaximumSize(QtCore.QSize(50, 16777215))
        self.down5.setStyleSheet(_fromUtf8("QWidget { background-color:rgb(234, 234, 234); }"))
        self.down5.setObjectName(_fromUtf8("down5"))
        self.gridLayout.addWidget(self.down5, 2, 1, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout)

        self.retranslateUi(IncrementInput)
        QtCore.QObject.connect(self.up10, QtCore.SIGNAL(_fromUtf8("clicked()")), IncrementInput.increment10)
        QtCore.QObject.connect(self.down10, QtCore.SIGNAL(_fromUtf8("clicked()")), IncrementInput.decrement10)
        QtCore.QObject.connect(self.up1, QtCore.SIGNAL(_fromUtf8("clicked()")), IncrementInput.increment1)
        QtCore.QObject.connect(self.down1, QtCore.SIGNAL(_fromUtf8("clicked()")), IncrementInput.decrement1)
        QtCore.QObject.connect(self.down5, QtCore.SIGNAL(_fromUtf8("clicked()")), IncrementInput.decrement5)
        QtCore.QObject.connect(self.up5, QtCore.SIGNAL(_fromUtf8("clicked()")), IncrementInput.increment5)
        QtCore.QMetaObject.connectSlotsByName(IncrementInput)

    def retranslateUi(self, IncrementInput):
        IncrementInput.setWindowTitle(_translate("IncrementInput", "Form", None))
        self.value_lnedt.setText(_translate("IncrementInput", "0", None))
        self.down10.setText(_translate("IncrementInput", "   ", None))
        self.up10.setText(_translate("IncrementInput", "10", None))
        self.up1.setText(_translate("IncrementInput", "1", None))
        self.down1.setText(_translate("IncrementInput", "   ", None))
        self.up5.setText(_translate("IncrementInput", "5", None))
        self.down5.setText(_translate("IncrementInput", "   ", None))

