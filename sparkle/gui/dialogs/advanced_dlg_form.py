# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'advanced_dlg.ui'
#
# Created: Fri May  1 23:18:07 2015
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

class Ui_AdvancedOptionsDialog(object):
    def setupUi(self, AdvancedOptionsDialog):
        AdvancedOptionsDialog.setObjectName(_fromUtf8("AdvancedOptionsDialog"))
        AdvancedOptionsDialog.resize(400, 286)
        self.verticalLayout = QtGui.QVBoxLayout(AdvancedOptionsDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(AdvancedOptionsDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.deviceCmbx = QtGui.QComboBox(AdvancedOptionsDialog)
        self.deviceCmbx.setObjectName(_fromUtf8("deviceCmbx"))
        self.gridLayout.addWidget(self.deviceCmbx, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(AdvancedOptionsDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.speakerMaxVSpnbx = SmartSpinBox(AdvancedOptionsDialog)
        self.speakerMaxVSpnbx.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.speakerMaxVSpnbx.setObjectName(_fromUtf8("speakerMaxVSpnbx"))
        self.gridLayout.addWidget(self.speakerMaxVSpnbx, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(AdvancedOptionsDialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.squareMaxVSpnbx = SmartSpinBox(AdvancedOptionsDialog)
        self.squareMaxVSpnbx.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.squareMaxVSpnbx.setObjectName(_fromUtf8("squareMaxVSpnbx"))
        self.gridLayout.addWidget(self.squareMaxVSpnbx, 2, 1, 1, 1)
        self.label_4 = QtGui.QLabel(AdvancedOptionsDialog)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.V2ASpnbx = SmartSpinBox(AdvancedOptionsDialog)
        self.V2ASpnbx.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.V2ASpnbx.setObjectName(_fromUtf8("V2ASpnbx"))
        self.gridLayout.addWidget(self.V2ASpnbx, 3, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.groupBox = QtGui.QGroupBox(AdvancedOptionsDialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.attenOnRadio = QtGui.QRadioButton(self.groupBox)
        self.attenOnRadio.setGeometry(QtCore.QRect(10, 30, 109, 26))
        self.attenOnRadio.setChecked(False)
        self.attenOnRadio.setObjectName(_fromUtf8("attenOnRadio"))
        self.buttonGroup = QtGui.QButtonGroup(AdvancedOptionsDialog)
        self.buttonGroup.setObjectName(_fromUtf8("buttonGroup"))
        self.buttonGroup.addButton(self.attenOnRadio)
        self.radioButton_2 = QtGui.QRadioButton(self.groupBox)
        self.radioButton_2.setGeometry(QtCore.QRect(130, 30, 109, 26))
        self.radioButton_2.setChecked(True)
        self.radioButton_2.setObjectName(_fromUtf8("radioButton_2"))
        self.buttonGroup.addButton(self.radioButton_2)
        self.verticalLayout.addWidget(self.groupBox)
        self.buttonBox = QtGui.QDialogButtonBox(AdvancedOptionsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(AdvancedOptionsDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), AdvancedOptionsDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), AdvancedOptionsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AdvancedOptionsDialog)

    def retranslateUi(self, AdvancedOptionsDialog):
        AdvancedOptionsDialog.setWindowTitle(_translate("AdvancedOptionsDialog", "Advanced Options", None))
        self.label.setText(_translate("AdvancedOptionsDialog", "DAQ Device", None))
        self.label_2.setText(_translate("AdvancedOptionsDialog", "Max voltage (speaker)", None))
        self.label_3.setText(_translate("AdvancedOptionsDialog", "Max voltage (square)", None))
        self.label_4.setText(_translate("AdvancedOptionsDialog", "Volt to Amp conversion", None))
        self.groupBox.setTitle(_translate("AdvancedOptionsDialog", "Attenuator", None))
        self.attenOnRadio.setText(_translate("AdvancedOptionsDialog", "On", None))
        self.radioButton_2.setText(_translate("AdvancedOptionsDialog", "Off", None))

from sparkle.gui.stim.smart_spinbox import SmartSpinBox
