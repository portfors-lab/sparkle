# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\tone_parameters.ui'
#
# Created: Wed Dec 11 12:31:23 2013
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

class Ui_ToneParameterWidget(object):
    def setupUi(self, ToneParameterWidget):
        ToneParameterWidget.setObjectName(_fromUtf8("ToneParameterWidget"))
        ToneParameterWidget.resize(339, 217)
        self.verticalLayout = QtGui.QVBoxLayout(ToneParameterWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_41 = QtGui.QLabel(ToneParameterWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_41.sizePolicy().hasHeightForWidth())
        self.label_41.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_41.setFont(font)
        self.label_41.setObjectName(_fromUtf8("label_41"))
        self.horizontalLayout.addWidget(self.label_41)
        self.freq_spnbx = IncrementInput(ToneParameterWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.freq_spnbx.sizePolicy().hasHeightForWidth())
        self.freq_spnbx.setSizePolicy(sizePolicy)
        self.freq_spnbx.setMinimumSize(QtCore.QSize(0, 25))
        self.freq_spnbx.setObjectName(_fromUtf8("freq_spnbx"))
        self.horizontalLayout.addWidget(self.freq_spnbx)
        self.funit_lbl = QtGui.QLabel(ToneParameterWidget)
        self.funit_lbl.setObjectName(_fromUtf8("funit_lbl"))
        self.horizontalLayout.addWidget(self.funit_lbl)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.common = ParameterWidget(ToneParameterWidget)
        self.common.setObjectName(_fromUtf8("common"))
        self.verticalLayout.addWidget(self.common)

        self.retranslateUi(ToneParameterWidget)
        QtCore.QMetaObject.connectSlotsByName(ToneParameterWidget)

    def retranslateUi(self, ToneParameterWidget):
        ToneParameterWidget.setWindowTitle(_translate("ToneParameterWidget", "Form", None))
        self.label_41.setText(_translate("ToneParameterWidget", "Frequency", None))
        self.funit_lbl.setText(_translate("ToneParameterWidget", "kHz", None))

from incrementer import IncrementInput
from parameterwidget import ParameterWidget
