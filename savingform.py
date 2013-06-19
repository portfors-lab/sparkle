# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\saving_dlg.ui'
#
# Created: Mon Jun 17 15:11:58 2013
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

class Ui_SaveOptDlg(object):
    def setupUi(self, SaveOptDlg):
        SaveOptDlg.setObjectName(_fromUtf8("SaveOptDlg"))
        SaveOptDlg.resize(361, 172)
        self.verticalLayout = QtGui.QVBoxLayout(SaveOptDlg)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(SaveOptDlg)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.saveformat_cmbx = QtGui.QComboBox(SaveOptDlg)
        self.saveformat_cmbx.setObjectName(_fromUtf8("saveformat_cmbx"))
        self.saveformat_cmbx.addItem(_fromUtf8(""))
        self.saveformat_cmbx.addItem(_fromUtf8(""))
        self.saveformat_cmbx.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.saveformat_cmbx, 0, 1, 1, 1)
        self.label_3 = QtGui.QLabel(SaveOptDlg)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.savefolder_lnedt = QtGui.QLineEdit(SaveOptDlg)
        self.savefolder_lnedt.setObjectName(_fromUtf8("savefolder_lnedt"))
        self.gridLayout.addWidget(self.savefolder_lnedt, 1, 1, 1, 1)
        self.browse_button = QtGui.QPushButton(SaveOptDlg)
        self.browse_button.setObjectName(_fromUtf8("browse_button"))
        self.gridLayout.addWidget(self.browse_button, 1, 2, 1, 1)
        self.label_2 = QtGui.QLabel(SaveOptDlg)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.savename_lnedt = QtGui.QLineEdit(SaveOptDlg)
        self.savename_lnedt.setObjectName(_fromUtf8("savename_lnedt"))
        self.gridLayout.addWidget(self.savename_lnedt, 2, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttonBox = QtGui.QDialogButtonBox(SaveOptDlg)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(SaveOptDlg)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SaveOptDlg.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SaveOptDlg.reject)
        QtCore.QObject.connect(self.browse_button, QtCore.SIGNAL(_fromUtf8("clicked()")), SaveOptDlg.browse_folders)
        QtCore.QMetaObject.connectSlotsByName(SaveOptDlg)

    def retranslateUi(self, SaveOptDlg):
        SaveOptDlg.setWindowTitle(_translate("SaveOptDlg", "Dialog", None))
        self.label.setText(_translate("SaveOptDlg", "Save file format", None))
        self.saveformat_cmbx.setItemText(0, _translate("SaveOptDlg", "npy", None))
        self.saveformat_cmbx.setItemText(1, _translate("SaveOptDlg", "mat", None))
        self.saveformat_cmbx.setItemText(2, _translate("SaveOptDlg", "txt", None))
        self.label_3.setText(_translate("SaveOptDlg", "Save file location", None))
        self.browse_button.setText(_translate("SaveOptDlg", "browse...", None))
        self.label_2.setText(_translate("SaveOptDlg", "Save name template", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    SaveOptDlg = QtGui.QDialog()
    ui = Ui_SaveOptDlg()
    ui.setupUi(SaveOptDlg)
    SaveOptDlg.show()
    sys.exit(app.exec_())

