# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'vocal_path_dlg.ui'
#
# Created: Fri Mar 27 11:24:32 2015
#      by: PyQt4 UI code generator 4.11.1
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

class Ui_VocalPathDialog(object):
    def setupUi(self, VocalPathDialog):
        VocalPathDialog.setObjectName(_fromUtf8("VocalPathDialog"))
        VocalPathDialog.resize(610, 370)
        self.verticalLayout = QtGui.QVBoxLayout(VocalPathDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.addBtn = QtGui.QPushButton(VocalPathDialog)
        self.addBtn.setObjectName(_fromUtf8("addBtn"))
        self.gridLayout.addWidget(self.addBtn, 2, 0, 1, 1)
        self.filetreeView = QtGui.QTreeView(VocalPathDialog)
        self.filetreeView.setAllColumnsShowFocus(False)
        self.filetreeView.setObjectName(_fromUtf8("filetreeView"))
        self.filetreeView.header().setStretchLastSection(False)
        self.gridLayout.addWidget(self.filetreeView, 1, 0, 1, 1)
        self.removeBtn = QtGui.QPushButton(VocalPathDialog)
        self.removeBtn.setObjectName(_fromUtf8("removeBtn"))
        self.gridLayout.addWidget(self.removeBtn, 2, 1, 1, 1)
        self.label = QtGui.QLabel(VocalPathDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(VocalPathDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.filelist = QtGui.QListWidget(VocalPathDialog)
        self.filelist.setObjectName(_fromUtf8("filelist"))
        self.gridLayout.addWidget(self.filelist, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttonBox = QtGui.QDialogButtonBox(VocalPathDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(VocalPathDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), VocalPathDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), VocalPathDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(VocalPathDialog)

    def retranslateUi(self, VocalPathDialog):
        VocalPathDialog.setWindowTitle(_translate("VocalPathDialog", "Dialog", None))
        self.addBtn.setText(_translate("VocalPathDialog", "add >>", None))
        self.removeBtn.setText(_translate("VocalPathDialog", "<< remove", None))
        self.label.setText(_translate("VocalPathDialog", "Folders to search for vocal files:", None))
        self.label_2.setText(_translate("VocalPathDialog", "Select folders to add to vocal search path", None))

