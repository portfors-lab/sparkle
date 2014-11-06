# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\raster_bounds_dlg.ui'
#
# Created: Wed Nov 05 16:22:36 2014
#      by: PyQt4 UI code generator 4.11.1
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
        RasterBoundsDialog.resize(257, 127)
        self.verticalLayout = QtGui.QVBoxLayout(RasterBoundsDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_3 = QtGui.QLabel(RasterBoundsDialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        self.label_4 = QtGui.QLabel(RasterBoundsDialog)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout.addWidget(self.label_4)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(RasterBoundsDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(RasterBoundsDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.upperSpnbx = QtGui.QDoubleSpinBox(RasterBoundsDialog)
        self.upperSpnbx.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.upperSpnbx.setMaximum(1.0)
        self.upperSpnbx.setSingleStep(0.01)
        self.upperSpnbx.setObjectName(_fromUtf8("upperSpnbx"))
        self.gridLayout.addWidget(self.upperSpnbx, 0, 1, 1, 1)
        self.lowerSpnbx = QtGui.QDoubleSpinBox(RasterBoundsDialog)
        self.lowerSpnbx.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.lowerSpnbx.setMaximum(1.0)
        self.lowerSpnbx.setSingleStep(0.01)
        self.lowerSpnbx.setObjectName(_fromUtf8("lowerSpnbx"))
        self.gridLayout.addWidget(self.lowerSpnbx, 1, 1, 1, 1)
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
        self.label_3.setText(_translate("RasterBoundsDialog", "Portion of plot to display raster points in", None))
        self.label_4.setText(_translate("RasterBoundsDialog", "(values between 0.0 - 1.0)", None))
        self.label.setText(_translate("RasterBoundsDialog", "Upper bound", None))
        self.label_2.setText(_translate("RasterBoundsDialog", "Lower bound", None))

