# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\scale_dlg.ui'
#
# Created: Thu Jun 19 11:21:41 2014
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

class Ui_ScaleDlg(object):
    def setupUi(self, ScaleDlg):
        ScaleDlg.setObjectName(_fromUtf8("ScaleDlg"))
        ScaleDlg.resize(218, 133)
        self.verticalLayout = QtGui.QVBoxLayout(ScaleDlg)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(ScaleDlg)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.secBtn = QtGui.QRadioButton(self.groupBox)
        self.secBtn.setGeometry(QtCore.QRect(10, 20, 82, 17))
        self.secBtn.setObjectName(_fromUtf8("secBtn"))
        self.msBtn = QtGui.QRadioButton(self.groupBox)
        self.msBtn.setGeometry(QtCore.QRect(110, 20, 82, 17))
        self.msBtn.setChecked(True)
        self.msBtn.setObjectName(_fromUtf8("msBtn"))
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(ScaleDlg)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.hzBtn = QtGui.QRadioButton(self.groupBox_2)
        self.hzBtn.setGeometry(QtCore.QRect(10, 20, 82, 17))
        self.hzBtn.setObjectName(_fromUtf8("hzBtn"))
        self.khzBtn = QtGui.QRadioButton(self.groupBox_2)
        self.khzBtn.setGeometry(QtCore.QRect(110, 20, 82, 17))
        self.khzBtn.setChecked(True)
        self.khzBtn.setObjectName(_fromUtf8("khzBtn"))
        self.verticalLayout.addWidget(self.groupBox_2)
        self.buttonBox = QtGui.QDialogButtonBox(ScaleDlg)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ScaleDlg)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ScaleDlg.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ScaleDlg.reject)
        QtCore.QMetaObject.connectSlotsByName(ScaleDlg)

    def retranslateUi(self, ScaleDlg):
        ScaleDlg.setWindowTitle(_translate("ScaleDlg", "Dialog", None))
        self.groupBox.setTitle(_translate("ScaleDlg", "Time scale", None))
        self.secBtn.setText(_translate("ScaleDlg", "seconds", None))
        self.msBtn.setText(_translate("ScaleDlg", "ms", None))
        self.groupBox_2.setTitle(_translate("ScaleDlg", "Frequency scale", None))
        self.hzBtn.setText(_translate("ScaleDlg", "Hz", None))
        self.khzBtn.setText(_translate("ScaleDlg", "kHz", None))

