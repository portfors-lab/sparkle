# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\raster_bounds_dlg.ui'
#
# Created: Thu Jun 19 13:01:50 2014
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

class Ui_RasterBoundsDialog(object):
    def setupUi(self, RasterBoundsDialog):
        RasterBoundsDialog.setObjectName(_fromUtf8("RasterBoundsDialog"))
        RasterBoundsDialog.resize(229, 99)
        self.verticalLayout = QtGui.QVBoxLayout(RasterBoundsDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(RasterBoundsDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.upperLnedt = QtGui.QLineEdit(RasterBoundsDialog)
        self.upperLnedt.setObjectName(_fromUtf8("upperLnedt"))
        self.gridLayout.addWidget(self.upperLnedt, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(RasterBoundsDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.lowerLnedt = QtGui.QLineEdit(RasterBoundsDialog)
        self.lowerLnedt.setObjectName(_fromUtf8("lowerLnedt"))
        self.gridLayout.addWidget(self.lowerLnedt, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttonBox = QtGui.QDialogButtonBox(RasterBoundsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(RasterBoundsDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), RasterBoundsDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), RasterBoundsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(RasterBoundsDialog)

    def retranslateUi(self, RasterBoundsDialog):
        RasterBoundsDialog.setWindowTitle(_translate("RasterBoundsDialog", "Raster y-axis bounds", None))
        self.label.setText(_translate("RasterBoundsDialog", "Upper bound", None))
        self.label_2.setText(_translate("RasterBoundsDialog", "Lower bound", None))

