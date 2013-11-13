# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\common_parameters.ui'
#
# Created: Wed Nov 13 14:25:43 2013
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

class Ui_ParameterWidget(object):
    def setupUi(self, ParameterWidget):
        ParameterWidget.setObjectName(_fromUtf8("ParameterWidget"))
        ParameterWidget.resize(452, 174)
        self.verticalLayout = QtGui.QVBoxLayout(ParameterWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout_5 = QtGui.QGridLayout()
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.db_spnbx = QtGui.QSpinBox(ParameterWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.db_spnbx.setFont(font)
        self.db_spnbx.setObjectName(_fromUtf8("db_spnbx"))
        self.gridLayout_5.addWidget(self.db_spnbx, 0, 1, 1, 1)
        self.tunit_lbl2 = QtGui.QLabel(ParameterWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tunit_lbl2.sizePolicy().hasHeightForWidth())
        self.tunit_lbl2.setSizePolicy(sizePolicy)
        self.tunit_lbl2.setObjectName(_fromUtf8("tunit_lbl2"))
        self.gridLayout_5.addWidget(self.tunit_lbl2, 1, 2, 1, 1)
        self.label_42 = QtGui.QLabel(ParameterWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_42.setFont(font)
        self.label_42.setObjectName(_fromUtf8("label_42"))
        self.gridLayout_5.addWidget(self.label_42, 0, 0, 1, 1)
        self.label_6 = QtGui.QLabel(ParameterWidget)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_5.addWidget(self.label_6, 0, 2, 1, 1)
        self.label_40 = QtGui.QLabel(ParameterWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_40.setFont(font)
        self.label_40.setObjectName(_fromUtf8("label_40"))
        self.gridLayout_5.addWidget(self.label_40, 3, 0, 1, 1)
        self.funit_lbl2 = QtGui.QLabel(ParameterWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.funit_lbl2.sizePolicy().hasHeightForWidth())
        self.funit_lbl2.setSizePolicy(sizePolicy)
        self.funit_lbl2.setObjectName(_fromUtf8("funit_lbl2"))
        self.gridLayout_5.addWidget(self.funit_lbl2, 4, 2, 1, 1)
        self.label_37 = QtGui.QLabel(ParameterWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_37.sizePolicy().hasHeightForWidth())
        self.label_37.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_37.setFont(font)
        self.label_37.setObjectName(_fromUtf8("label_37"))
        self.gridLayout_5.addWidget(self.label_37, 4, 0, 1, 1)
        self.risefall_spnbx = QtGui.QSpinBox(ParameterWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.risefall_spnbx.setFont(font)
        self.risefall_spnbx.setMaximum(100)
        self.risefall_spnbx.setObjectName(_fromUtf8("risefall_spnbx"))
        self.gridLayout_5.addWidget(self.risefall_spnbx, 3, 1, 1, 1)
        self.aosr_spnbx = QtGui.QSpinBox(ParameterWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.aosr_spnbx.setFont(font)
        self.aosr_spnbx.setMinimum(10)
        self.aosr_spnbx.setMaximum(1000)
        self.aosr_spnbx.setSingleStep(10)
        self.aosr_spnbx.setProperty("value", 100)
        self.aosr_spnbx.setObjectName(_fromUtf8("aosr_spnbx"))
        self.gridLayout_5.addWidget(self.aosr_spnbx, 4, 1, 1, 1)
        self.dur_spnbx = QtGui.QSpinBox(ParameterWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.dur_spnbx.setFont(font)
        self.dur_spnbx.setMinimum(5)
        self.dur_spnbx.setMaximum(50000)
        self.dur_spnbx.setSingleStep(100)
        self.dur_spnbx.setProperty("value", 1000)
        self.dur_spnbx.setObjectName(_fromUtf8("dur_spnbx"))
        self.gridLayout_5.addWidget(self.dur_spnbx, 1, 1, 1, 1)
        self.tunit_lbl3 = QtGui.QLabel(ParameterWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tunit_lbl3.sizePolicy().hasHeightForWidth())
        self.tunit_lbl3.setSizePolicy(sizePolicy)
        self.tunit_lbl3.setObjectName(_fromUtf8("tunit_lbl3"))
        self.gridLayout_5.addWidget(self.tunit_lbl3, 3, 2, 1, 1)
        self.label_32 = QtGui.QLabel(ParameterWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_32.sizePolicy().hasHeightForWidth())
        self.label_32.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_32.setFont(font)
        self.label_32.setObjectName(_fromUtf8("label_32"))
        self.gridLayout_5.addWidget(self.label_32, 1, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_5)

        self.retranslateUi(ParameterWidget)
        QtCore.QMetaObject.connectSlotsByName(ParameterWidget)

    def retranslateUi(self, ParameterWidget):
        ParameterWidget.setWindowTitle(_translate("ParameterWidget", "Form", None))
        self.tunit_lbl2.setText(_translate("ParameterWidget", "ms", None))
        self.label_42.setText(_translate("ParameterWidget", "Intensity", None))
        self.label_6.setText(_translate("ParameterWidget", "dB SPL", None))
        self.label_40.setText(_translate("ParameterWidget", "Rise fall time", None))
        self.funit_lbl2.setText(_translate("ParameterWidget", "kHz", None))
        self.label_37.setText(_translate("ParameterWidget", "Gen. Sample rate", None))
        self.tunit_lbl3.setText(_translate("ParameterWidget", "ms", None))
        self.label_32.setText(_translate("ParameterWidget", "Duration", None))

