# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\display_dlg.ui'
#
# Created: Tue May 21 11:52:46 2013
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
        DisplayDlg.resize(354, 84)
        self.verticalLayout = QtGui.QVBoxLayout(DisplayDlg)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(DisplayDlg)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.chunksz_lnedt = QtGui.QLineEdit(DisplayDlg)
        self.chunksz_lnedt.setObjectName(_fromUtf8("chunksz_lnedt"))
        self.horizontalLayout.addWidget(self.chunksz_lnedt)
        self.label_2 = QtGui.QLabel(DisplayDlg)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout.addWidget(self.label_2)
        self.verticalLayout.addLayout(self.horizontalLayout)
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
        self.label.setText(_translate("DisplayDlg", "acquisition chunk size", None))
        self.label_2.setText(_translate("DisplayDlg", "samples", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    DisplayDlg = QtGui.QDialog()
    ui = Ui_DisplayDlg()
    ui.setupUi(DisplayDlg)
    DisplayDlg.show()
    sys.exit(app.exec_())

