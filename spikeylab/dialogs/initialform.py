# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\inital_dlg.ui'
#
# Created: Thu May 08 17:58:31 2014
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

class Ui_InitialDlg(object):
    def setupUi(self, InitialDlg):
        InitialDlg.setObjectName(_fromUtf8("InitialDlg"))
        InitialDlg.resize(410, 129)
        self.verticalLayout = QtGui.QVBoxLayout(InitialDlg)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(InitialDlg)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.new_radio = QtGui.QRadioButton(self.groupBox)
        self.new_radio.setChecked(True)
        self.new_radio.setObjectName(_fromUtf8("new_radio"))
        self.horizontalLayout.addWidget(self.new_radio)
        self.prev_radio = QtGui.QRadioButton(self.groupBox)
        self.prev_radio.setObjectName(_fromUtf8("prev_radio"))
        self.horizontalLayout.addWidget(self.prev_radio)
        self.verticalLayout.addWidget(self.groupBox)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.filename_lnedt = QtGui.QLineEdit(InitialDlg)
        self.filename_lnedt.setObjectName(_fromUtf8("filename_lnedt"))
        self.horizontalLayout_2.addWidget(self.filename_lnedt)
        self.browse_button = QtGui.QPushButton(InitialDlg)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.browse_button.sizePolicy().hasHeightForWidth())
        self.browse_button.setSizePolicy(sizePolicy)
        self.browse_button.setMinimumSize(QtCore.QSize(30, 0))
        self.browse_button.setBaseSize(QtCore.QSize(0, 0))
        self.browse_button.setObjectName(_fromUtf8("browse_button"))
        self.horizontalLayout_2.addWidget(self.browse_button)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.buttonBox = QtGui.QDialogButtonBox(InitialDlg)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(InitialDlg)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), InitialDlg.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), InitialDlg.reject)
        QtCore.QObject.connect(self.browse_button, QtCore.SIGNAL(_fromUtf8("clicked()")), InitialDlg.browse)
        QtCore.QMetaObject.connectSlotsByName(InitialDlg)

    def retranslateUi(self, InitialDlg):
        InitialDlg.setWindowTitle(_translate("InitialDlg", "Dialog", None))
        self.groupBox.setTitle(_translate("InitialDlg", "Data File", None))
        self.new_radio.setText(_translate("InitialDlg", "Create New", None))
        self.prev_radio.setText(_translate("InitialDlg", "Load Previous", None))
        self.browse_button.setText(_translate("InitialDlg", "...", None))

