# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\tone_parameters.ui'
#
# Created: Sun Jan 26 21:18:51 2014
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
        ToneParameterWidget.resize(351, 311)
        self.verticalLayout = QtGui.QVBoxLayout(ToneParameterWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.freq_spnbx = IncrementInput(ToneParameterWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.freq_spnbx.sizePolicy().hasHeightForWidth())
        self.freq_spnbx.setSizePolicy(sizePolicy)
        self.freq_spnbx.setMinimumSize(QtCore.QSize(0, 25))
        self.freq_spnbx.setObjectName(_fromUtf8("freq_spnbx"))
        self.gridLayout.addWidget(self.freq_spnbx, 0, 1, 1, 1)
        self.funit_lbl = QtGui.QLabel(ToneParameterWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.funit_lbl.sizePolicy().hasHeightForWidth())
        self.funit_lbl.setSizePolicy(sizePolicy)
        self.funit_lbl.setMinimumSize(QtCore.QSize(32, 0))
        self.funit_lbl.setObjectName(_fromUtf8("funit_lbl"))
        self.gridLayout.addWidget(self.funit_lbl, 0, 2, 1, 1)
        self.label_41 = QtGui.QLabel(ToneParameterWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_41.sizePolicy().hasHeightForWidth())
        self.label_41.setSizePolicy(sizePolicy)
        self.label_41.setMinimumSize(QtCore.QSize(75, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_41.setFont(font)
        self.label_41.setObjectName(_fromUtf8("label_41"))
        self.gridLayout.addWidget(self.label_41, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.common = CommonParameterWidget(ToneParameterWidget)
        self.common.setObjectName(_fromUtf8("common"))
        self.verticalLayout.addWidget(self.common)

        self.retranslateUi(ToneParameterWidget)
        QtCore.QMetaObject.connectSlotsByName(ToneParameterWidget)

    def retranslateUi(self, ToneParameterWidget):
        ToneParameterWidget.setWindowTitle(_translate("ToneParameterWidget", "Pure Tone", None))
        self.funit_lbl.setText(_translate("ToneParameterWidget", "kHz", None))
        self.label_41.setText(_translate("ToneParameterWidget", "Frequency", None))

from spikeylab.stim.common_parameters import CommonParameterWidget
from spikeylab.stim.incrementer import IncrementInput
