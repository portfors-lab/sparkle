# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\scale_dlg.ui'
#
# Created: Fri May 31 10:31:08 2013
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
        ScaleDlg.resize(258, 112)
        self.verticalLayout = QtGui.QVBoxLayout(ScaleDlg)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(ScaleDlg)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.tscale_spnbx = QtGui.QDoubleSpinBox(ScaleDlg)
        self.tscale_spnbx.setDecimals(6)
        self.tscale_spnbx.setMaximum(60.0)
        self.tscale_spnbx.setSingleStep(0.0)
        self.tscale_spnbx.setProperty("value", 0.001)
        self.tscale_spnbx.setObjectName(_fromUtf8("tscale_spnbx"))
        self.gridLayout.addWidget(self.tscale_spnbx, 0, 1, 1, 1)
        self.label = QtGui.QLabel(ScaleDlg)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.fscale_spnbx = QtGui.QSpinBox(ScaleDlg)
        self.fscale_spnbx.setMinimum(1)
        self.fscale_spnbx.setMaximum(100000)
        self.fscale_spnbx.setProperty("value", 1000)
        self.fscale_spnbx.setObjectName(_fromUtf8("fscale_spnbx"))
        self.gridLayout.addWidget(self.fscale_spnbx, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
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
        self.label_2.setText(_translate("ScaleDlg", "time factor", None))
        self.label.setText(_translate("ScaleDlg", "frequency factor", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ScaleDlg = QtGui.QDialog()
    ui = Ui_ScaleDlg()
    ui.setupUi(ScaleDlg)
    ScaleDlg.show()
    sys.exit(app.exec_())

