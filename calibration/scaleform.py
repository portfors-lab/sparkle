# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\scale_dlg.ui'
#
# Created: Tue Jun  4 13:54:51 2013
#      by: PyQt4 UI code generator 4.10
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

class Ui_ScaleDlg(object):
    def setupUi(self, ScaleDlg):
        ScaleDlg.setObjectName(_fromUtf8("ScaleDlg"))
        ScaleDlg.resize(218, 133)
        self.verticalLayout = QtGui.QVBoxLayout(ScaleDlg)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(ScaleDlg)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.sec_btn = QtGui.QRadioButton(self.groupBox)
        self.sec_btn.setGeometry(QtCore.QRect(10, 20, 82, 17))
        self.sec_btn.setObjectName(_fromUtf8("sec_btn"))
        self.ms_btn = QtGui.QRadioButton(self.groupBox)
        self.ms_btn.setGeometry(QtCore.QRect(110, 20, 82, 17))
        self.ms_btn.setChecked(True)
        self.ms_btn.setObjectName(_fromUtf8("ms_btn"))
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(ScaleDlg)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.hz_btn = QtGui.QRadioButton(self.groupBox_2)
        self.hz_btn.setGeometry(QtCore.QRect(10, 20, 82, 17))
        self.hz_btn.setObjectName(_fromUtf8("hz_btn"))
        self.khz_btn = QtGui.QRadioButton(self.groupBox_2)
        self.khz_btn.setGeometry(QtCore.QRect(110, 20, 82, 17))
        self.khz_btn.setChecked(True)
        self.khz_btn.setObjectName(_fromUtf8("khz_btn"))
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
        self.sec_btn.setText(_translate("ScaleDlg", "seconds", None))
        self.ms_btn.setText(_translate("ScaleDlg", "ms", None))
        self.groupBox_2.setTitle(_translate("ScaleDlg", "Frequency scale", None))
        self.hz_btn.setText(_translate("ScaleDlg", "Hz", None))
        self.khz_btn.setText(_translate("ScaleDlg", "kHz", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ScaleDlg = QtGui.QDialog()
    ui = Ui_ScaleDlg()
    ui.setupUi(ScaleDlg)
    ScaleDlg.show()
    sys.exit(app.exec_())

