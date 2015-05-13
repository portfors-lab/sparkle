# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\specgram_dlg.ui'
#
# Created: Thu Jun 19 11:21:55 2014
#      by: sparkle.QtWrapper UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from sparkle.QtWrapper import QtCore, QtGui

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

class Ui_SpecDialog(object):
    def setupUi(self, SpecDialog):
        SpecDialog.setObjectName(_fromUtf8("SpecDialog"))
        SpecDialog.resize(362, 121)
        self.verticalLayout = QtGui.QVBoxLayout(SpecDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(SpecDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.nfftSpnbx = QtGui.QSpinBox(SpecDialog)
        self.nfftSpnbx.setMinimum(8)
        self.nfftSpnbx.setMaximum(4096)
        self.nfftSpnbx.setProperty("value", 512)
        self.nfftSpnbx.setObjectName(_fromUtf8("nfftSpnbx"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.nfftSpnbx)
        self.label_2 = QtGui.QLabel(SpecDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.windowCmbx = QtGui.QComboBox(SpecDialog)
        self.windowCmbx.setObjectName(_fromUtf8("windowCmbx"))
        self.windowCmbx.addItem(_fromUtf8(""))
        self.windowCmbx.addItem(_fromUtf8(""))
        self.windowCmbx.addItem(_fromUtf8(""))
        self.windowCmbx.addItem(_fromUtf8(""))
        self.windowCmbx.addItem(_fromUtf8(""))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.windowCmbx)
        self.label_3 = QtGui.QLabel(SpecDialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_3)
        self.overlapSpnbx = QtGui.QSpinBox(SpecDialog)
        self.overlapSpnbx.setObjectName(_fromUtf8("overlapSpnbx"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.overlapSpnbx)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtGui.QDialogButtonBox(SpecDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(SpecDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SpecDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SpecDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SpecDialog)

    def retranslateUi(self, SpecDialog):
        SpecDialog.setWindowTitle(_translate("SpecDialog", "Dialog", None))
        self.label.setText(_translate("SpecDialog", "NFFT", None))
        self.label_2.setText(_translate("SpecDialog", "Window function", None))
        self.windowCmbx.setItemText(0, _translate("SpecDialog", "Hanning", None))
        self.windowCmbx.setItemText(1, _translate("SpecDialog", "Hamming", None))
        self.windowCmbx.setItemText(2, _translate("SpecDialog", "Blackman", None))
        self.windowCmbx.setItemText(3, _translate("SpecDialog", "Bartlett", None))
        self.windowCmbx.setItemText(4, _translate("SpecDialog", "none", None))
        self.label_3.setText(_translate("SpecDialog", "% overlap", None))

