# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\specgram_dlg.ui'
#
# Created: Wed Jan 22 15:37:38 2014
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

class Ui_SpecDialog(object):
    def setupUi(self, SpecDialog):
        SpecDialog.setObjectName(_fromUtf8("SpecDialog"))
        SpecDialog.resize(362, 162)
        self.verticalLayout = QtGui.QVBoxLayout(SpecDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(SpecDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.nfft_spnbx = QtGui.QSpinBox(SpecDialog)
        self.nfft_spnbx.setMinimum(8)
        self.nfft_spnbx.setMaximum(4096)
        self.nfft_spnbx.setProperty("value", 512)
        self.nfft_spnbx.setObjectName(_fromUtf8("nfft_spnbx"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.nfft_spnbx)
        self.label_2 = QtGui.QLabel(SpecDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.window_cmbx = QtGui.QComboBox(SpecDialog)
        self.window_cmbx.setObjectName(_fromUtf8("window_cmbx"))
        self.window_cmbx.addItem(_fromUtf8(""))
        self.window_cmbx.addItem(_fromUtf8(""))
        self.window_cmbx.addItem(_fromUtf8(""))
        self.window_cmbx.addItem(_fromUtf8(""))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.window_cmbx)
        self.label_3 = QtGui.QLabel(SpecDialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_3)
        self.overlap_spnbx = QtGui.QSpinBox(SpecDialog)
        self.overlap_spnbx.setObjectName(_fromUtf8("overlap_spnbx"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.overlap_spnbx)
        self.colormap_cmbx = QtGui.QComboBox(SpecDialog)
        self.colormap_cmbx.setObjectName(_fromUtf8("colormap_cmbx"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.colormap_cmbx)
        self.label_4 = QtGui.QLabel(SpecDialog)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_4)
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
        self.window_cmbx.setItemText(0, _translate("SpecDialog", "Hanning", None))
        self.window_cmbx.setItemText(1, _translate("SpecDialog", "Hamming", None))
        self.window_cmbx.setItemText(2, _translate("SpecDialog", "Blackman", None))
        self.window_cmbx.setItemText(3, _translate("SpecDialog", "Bartlett", None))
        self.label_3.setText(_translate("SpecDialog", "% overlap", None))
        self.label_4.setText(_translate("SpecDialog", "Colormap", None))

