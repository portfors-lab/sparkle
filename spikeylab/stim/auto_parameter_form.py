# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\auto_parameter.ui'
#
# Created: Thu Nov 21 18:15:50 2013
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

class Ui_AutoParamWidget(object):
    def setupUi(self, AutoParamWidget):
        AutoParamWidget.setObjectName(_fromUtf8("AutoParamWidget"))
        AutoParamWidget.resize(357, 192)
        self.verticalLayout = QtGui.QVBoxLayout(AutoParamWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.nsteps_lbl = QtGui.QLabel(AutoParamWidget)
        self.nsteps_lbl.setObjectName(_fromUtf8("nsteps_lbl"))
        self.gridLayout.addWidget(self.nsteps_lbl, 4, 1, 1, 1)
        self.label_4 = QtGui.QLabel(AutoParamWidget)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.stop_lnedt = QtGui.QLineEdit(AutoParamWidget)
        self.stop_lnedt.setObjectName(_fromUtf8("stop_lnedt"))
        self.gridLayout.addWidget(self.stop_lnedt, 3, 1, 1, 2)
        self.step_lnedt = QtGui.QLineEdit(AutoParamWidget)
        self.step_lnedt.setObjectName(_fromUtf8("step_lnedt"))
        self.gridLayout.addWidget(self.step_lnedt, 2, 1, 1, 2)
        self.label_3 = QtGui.QLabel(AutoParamWidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.label = QtGui.QLabel(AutoParamWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 4, 0, 1, 1)
        self.label_2 = QtGui.QLabel(AutoParamWidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.type_cmbx = QtGui.QComboBox(AutoParamWidget)
        self.type_cmbx.setObjectName(_fromUtf8("type_cmbx"))
        self.gridLayout.addWidget(self.type_cmbx, 0, 1, 1, 2)
        self.label_6 = QtGui.QLabel(AutoParamWidget)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 1, 0, 1, 1)
        self.start_lnedt = QtGui.QLineEdit(AutoParamWidget)
        self.start_lnedt.setObjectName(_fromUtf8("start_lnedt"))
        self.gridLayout.addWidget(self.start_lnedt, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)

        self.retranslateUi(AutoParamWidget)
        QtCore.QMetaObject.connectSlotsByName(AutoParamWidget)

    def retranslateUi(self, AutoParamWidget):
        AutoParamWidget.setWindowTitle(_translate("AutoParamWidget", "Form", None))
        self.nsteps_lbl.setText(_translate("AutoParamWidget", "0", None))
        self.label_4.setText(_translate("AutoParamWidget", "Stop", None))
        self.label_3.setText(_translate("AutoParamWidget", "Parameter", None))
        self.label.setText(_translate("AutoParamWidget", "Number of steps:", None))
        self.label_2.setText(_translate("AutoParamWidget", "Step", None))
        self.label_6.setText(_translate("AutoParamWidget", "Start", None))

