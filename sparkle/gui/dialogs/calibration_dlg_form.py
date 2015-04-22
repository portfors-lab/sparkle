# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\calibration_dlg.ui'
#
# Created: Wed Apr 22 11:00:25 2015
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

class Ui_CalibrationDialog(object):
    def setupUi(self, CalibrationDialog):
        CalibrationDialog.setObjectName(_fromUtf8("CalibrationDialog"))
        CalibrationDialog.setEnabled(True)
        CalibrationDialog.resize(359, 303)
        self.verticalLayout_2 = QtGui.QVBoxLayout(CalibrationDialog)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.groupBox = QtGui.QGroupBox(CalibrationDialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.noneRadio = QtGui.QRadioButton(self.groupBox)
        self.noneRadio.setChecked(True)
        self.noneRadio.setObjectName(_fromUtf8("noneRadio"))
        self.verticalLayout.addWidget(self.noneRadio)
        self.calfileRadio = QtGui.QRadioButton(self.groupBox)
        self.calfileRadio.setObjectName(_fromUtf8("calfileRadio"))
        self.verticalLayout.addWidget(self.calfileRadio)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.calChoiceCmbbx = QtGui.QComboBox(self.groupBox)
        self.calChoiceCmbbx.setEnabled(False)
        self.calChoiceCmbbx.setObjectName(_fromUtf8("calChoiceCmbbx"))
        self.horizontalLayout.addWidget(self.calChoiceCmbbx)
        self.plotBtn = QtGui.QPushButton(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plotBtn.sizePolicy().hasHeightForWidth())
        self.plotBtn.setSizePolicy(sizePolicy)
        self.plotBtn.setMaximumSize(QtCore.QSize(25, 16777215))
        self.plotBtn.setObjectName(_fromUtf8("plotBtn"))
        self.horizontalLayout.addWidget(self.plotBtn)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_8 = QtGui.QLabel(self.groupBox)
        self.label_8.setEnabled(False)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.horizontalLayout_2.addWidget(self.label_8)
        self.frangeLowSpnbx = SmartSpinBox(self.groupBox)
        self.frangeLowSpnbx.setEnabled(False)
        self.frangeLowSpnbx.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.frangeLowSpnbx.setMinimum(1.0)
        self.frangeLowSpnbx.setMaximum(100000.0)
        self.frangeLowSpnbx.setObjectName(_fromUtf8("frangeLowSpnbx"))
        self.horizontalLayout_2.addWidget(self.frangeLowSpnbx)
        self.frangeHighSpnbx = SmartSpinBox(self.groupBox)
        self.frangeHighSpnbx.setEnabled(False)
        self.frangeHighSpnbx.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.frangeHighSpnbx.setMaximum(120000.0)
        self.frangeHighSpnbx.setObjectName(_fromUtf8("frangeHighSpnbx"))
        self.horizontalLayout_2.addWidget(self.frangeHighSpnbx)
        self.funit_lbl_2 = QtGui.QLabel(self.groupBox)
        self.funit_lbl_2.setEnabled(False)
        self.funit_lbl_2.setObjectName(_fromUtf8("funit_lbl_2"))
        self.horizontalLayout_2.addWidget(self.funit_lbl_2)
        self.rangeBtn = QtGui.QPushButton(self.groupBox)
        self.rangeBtn.setEnabled(False)
        self.rangeBtn.setMinimumSize(QtCore.QSize(20, 0))
        self.rangeBtn.setObjectName(_fromUtf8("rangeBtn"))
        self.horizontalLayout_2.addWidget(self.rangeBtn)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.buttonBox = QtGui.QDialogButtonBox(CalibrationDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(CalibrationDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), CalibrationDialog.conditional_accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), CalibrationDialog.reject)
        QtCore.QObject.connect(self.noneRadio, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.label_8.setDisabled)
        QtCore.QObject.connect(self.noneRadio, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.frangeLowSpnbx.setDisabled)
        QtCore.QObject.connect(self.noneRadio, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.frangeHighSpnbx.setDisabled)
        QtCore.QObject.connect(self.noneRadio, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.funit_lbl_2.setDisabled)
        QtCore.QObject.connect(self.noneRadio, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.rangeBtn.setDisabled)
        QtCore.QObject.connect(self.rangeBtn, QtCore.SIGNAL(_fromUtf8("clicked()")), CalibrationDialog.maxRange)
        QtCore.QObject.connect(self.plotBtn, QtCore.SIGNAL(_fromUtf8("clicked()")), CalibrationDialog.plotCurve)
        QtCore.QObject.connect(self.noneRadio, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.calChoiceCmbbx.setDisabled)
        QtCore.QMetaObject.connectSlotsByName(CalibrationDialog)

    def retranslateUi(self, CalibrationDialog):
        CalibrationDialog.setWindowTitle(_translate("CalibrationDialog", "Dialog", None))
        self.groupBox.setTitle(_translate("CalibrationDialog", "Calibration file", None))
        self.noneRadio.setText(_translate("CalibrationDialog", "None", None))
        self.calfileRadio.setText(_translate("CalibrationDialog", "Use saved calibration", None))
        self.plotBtn.setText(_translate("CalibrationDialog", "P", None))
        self.label_8.setText(_translate("CalibrationDialog", "Calibration frequency range", None))
        self.funit_lbl_2.setText(_translate("CalibrationDialog", "kHz", None))
        self.rangeBtn.setToolTip(_translate("CalibrationDialog", "file max range", None))
        self.rangeBtn.setText(_translate("CalibrationDialog", "<>", None))

from sparkle.gui.stim.smart_spinbox import SmartSpinBox
