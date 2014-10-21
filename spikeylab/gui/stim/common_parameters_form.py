# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\common_parameters.ui'
#
# Created: Thu Jun 19 13:26:28 2014
#      by: QtWrapper UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from QtWrapper import QtCore, QtGui

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

class Ui_ParameterWidget(object):
    def setupUi(self, ParameterWidget):
        ParameterWidget.setObjectName(_fromUtf8("ParameterWidget"))
        ParameterWidget.resize(452, 169)
        self.verticalLayout = QtGui.QVBoxLayout(ParameterWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout_5 = QtGui.QGridLayout()
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.label_40 = QtGui.QLabel(ParameterWidget)
        self.label_40.setObjectName(_fromUtf8("label_40"))
        self.gridLayout_5.addWidget(self.label_40, 3, 0, 1, 1)
        self.label_6 = QtGui.QLabel(ParameterWidget)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_5.addWidget(self.label_6, 0, 2, 1, 1)
        self.label_32 = QtGui.QLabel(ParameterWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_32.sizePolicy().hasHeightForWidth())
        self.label_32.setSizePolicy(sizePolicy)
        self.label_32.setObjectName(_fromUtf8("label_32"))
        self.gridLayout_5.addWidget(self.label_32, 1, 0, 1, 1)
        self.tunit_lbl_0 = QtGui.QLabel(ParameterWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tunit_lbl_0.sizePolicy().hasHeightForWidth())
        self.tunit_lbl_0.setSizePolicy(sizePolicy)
        self.tunit_lbl_0.setObjectName(_fromUtf8("tunit_lbl_0"))
        self.gridLayout_5.addWidget(self.tunit_lbl_0, 1, 2, 1, 1)
        self.label_42 = QtGui.QLabel(ParameterWidget)
        self.label_42.setObjectName(_fromUtf8("label_42"))
        self.gridLayout_5.addWidget(self.label_42, 0, 0, 1, 1)
        self.tunit_lbl_1 = QtGui.QLabel(ParameterWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tunit_lbl_1.sizePolicy().hasHeightForWidth())
        self.tunit_lbl_1.setSizePolicy(sizePolicy)
        self.tunit_lbl_1.setObjectName(_fromUtf8("tunit_lbl_1"))
        self.gridLayout_5.addWidget(self.tunit_lbl_1, 3, 2, 1, 1)
        self.dbSpnbx = IncrementInput(ParameterWidget)
        self.dbSpnbx.setObjectName(_fromUtf8("dbSpnbx"))
        self.gridLayout_5.addWidget(self.dbSpnbx, 0, 1, 1, 1)
        self.durSpnbx = SmartSpinBox(ParameterWidget)
        self.durSpnbx.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.durSpnbx.setDecimals(3)
        self.durSpnbx.setMaximum(2000.0)
        self.durSpnbx.setObjectName(_fromUtf8("durSpnbx"))
        self.gridLayout_5.addWidget(self.durSpnbx, 1, 1, 1, 1)
        self.risefallSpnbx = SmartSpinBox(ParameterWidget)
        self.risefallSpnbx.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.risefallSpnbx.setDecimals(3)
        self.risefallSpnbx.setMaximum(500.0)
        self.risefallSpnbx.setObjectName(_fromUtf8("risefallSpnbx"))
        self.gridLayout_5.addWidget(self.risefallSpnbx, 3, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_5)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(ParameterWidget)
        QtCore.QMetaObject.connectSlotsByName(ParameterWidget)

    def retranslateUi(self, ParameterWidget):
        ParameterWidget.setWindowTitle(_translate("ParameterWidget", "Form", None))
        self.label_40.setText(_translate("ParameterWidget", "Rise fall time", None))
        self.label_6.setText(_translate("ParameterWidget", "dB SPL", None))
        self.label_32.setText(_translate("ParameterWidget", "Duration", None))
        self.tunit_lbl_0.setText(_translate("ParameterWidget", "ms", None))
        self.label_42.setText(_translate("ParameterWidget", "Intensity", None))
        self.tunit_lbl_1.setText(_translate("ParameterWidget", "ms", None))

from spikeylab.gui.stim.smart_spinbox import SmartSpinBox
from spikeylab.gui.stim.incrementer import IncrementInput
