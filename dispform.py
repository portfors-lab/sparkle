# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\display_dlg.ui'
#
# Created: Tue May 28 23:46:44 2013
#      by: PyQt4 UI code generator 4.10.1
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

class Ui_DisplayDlg(object):
    def setupUi(self, DisplayDlg):
        DisplayDlg.setObjectName(_fromUtf8("DisplayDlg"))
        DisplayDlg.resize(280, 154)
        self.verticalLayout = QtGui.QVBoxLayout(DisplayDlg)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.caldb_lnedt = QtGui.QLineEdit(DisplayDlg)
        self.caldb_lnedt.setObjectName(_fromUtf8("caldb_lnedt"))
        self.gridLayout.addWidget(self.caldb_lnedt, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(DisplayDlg)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.label = QtGui.QLabel(DisplayDlg)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.chunksz_lnedt = QtGui.QLineEdit(DisplayDlg)
        self.chunksz_lnedt.setObjectName(_fromUtf8("chunksz_lnedt"))
        self.gridLayout.addWidget(self.chunksz_lnedt, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(DisplayDlg)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 2, 1, 1)
        self.calV_lnedt = QtGui.QLineEdit(DisplayDlg)
        self.calV_lnedt.setObjectName(_fromUtf8("calV_lnedt"))
        self.gridLayout.addWidget(self.calV_lnedt, 2, 1, 1, 1)
        self.label_4 = QtGui.QLabel(DisplayDlg)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)
        self.label_6 = QtGui.QLabel(DisplayDlg)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 1, 2, 1, 1)
        self.label_5 = QtGui.QLabel(DisplayDlg)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 2, 2, 1, 1)
        self.calkhz_lnedt = QtGui.QLineEdit(DisplayDlg)
        self.calkhz_lnedt.setObjectName(_fromUtf8("calkhz_lnedt"))
        self.gridLayout.addWidget(self.calkhz_lnedt, 3, 1, 1, 1)
        self.label_7 = QtGui.QLabel(DisplayDlg)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout.addWidget(self.label_7, 3, 0, 1, 1)
        self.label_8 = QtGui.QLabel(DisplayDlg)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout.addWidget(self.label_8, 3, 2, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttonBox = QtGui.QDialogButtonBox(DisplayDlg)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(DisplayDlg)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DisplayDlg.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DisplayDlg.reject)
        QtCore.QMetaObject.connectSlotsByName(DisplayDlg)

    def retranslateUi(self, DisplayDlg):
        DisplayDlg.setWindowTitle(_translate("DisplayDlg", "Display Options", None))
        self.label_3.setText(_translate("DisplayDlg", "Calibration intensity", None))
        self.label.setText(_translate("DisplayDlg", "acquisition chunk size", None))
        self.label_2.setText(_translate("DisplayDlg", "samples", None))
        self.label_4.setText(_translate("DisplayDlg", "Voltage at  cal dB", None))
        self.label_6.setText(_translate("DisplayDlg", "dB", None))
        self.label_5.setText(_translate("DisplayDlg", "V", None))
        self.label_7.setText(_translate("DisplayDlg", "Calibration frequency", None))
        self.label_8.setText(_translate("DisplayDlg", "kHz", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    DisplayDlg = QtGui.QDialog()
    ui = Ui_DisplayDlg()
    ui.setupUi(DisplayDlg)
    DisplayDlg.show()
    sys.exit(app.exec_())

