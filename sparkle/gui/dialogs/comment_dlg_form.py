# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\comment_dlg.ui'
#
# Created: Thu Jun 19 11:21:26 2014
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

class Ui_CellCommentDialog(object):
    def setupUi(self, CellCommentDialog):
        CellCommentDialog.setObjectName(_fromUtf8("CellCommentDialog"))
        CellCommentDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        CellCommentDialog.resize(400, 300)
        self.verticalLayout = QtGui.QVBoxLayout(CellCommentDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(CellCommentDialog)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.cellidLbl = QtGui.QLabel(CellCommentDialog)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.cellidLbl.setFont(font)
        self.cellidLbl.setObjectName(_fromUtf8("cellidLbl"))
        self.horizontalLayout.addWidget(self.cellidLbl)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label_2 = QtGui.QLabel(CellCommentDialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.commentTxtedt = QtGui.QPlainTextEdit(CellCommentDialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.commentTxtedt.setFont(font)
        self.commentTxtedt.setObjectName(_fromUtf8("commentTxtedt"))
        self.verticalLayout.addWidget(self.commentTxtedt)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.okBtn = QtGui.QPushButton(CellCommentDialog)
        self.okBtn.setObjectName(_fromUtf8("okBtn"))
        self.horizontalLayout_2.addWidget(self.okBtn)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(CellCommentDialog)
        QtCore.QObject.connect(self.okBtn, QtCore.SIGNAL(_fromUtf8("clicked()")), CellCommentDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(CellCommentDialog)

    def retranslateUi(self, CellCommentDialog):
        CellCommentDialog.setWindowTitle(_translate("CellCommentDialog", "Form", None))
        self.label.setText(_translate("CellCommentDialog", "Cell ID:", None))
        self.cellidLbl.setText(_translate("CellCommentDialog", "0", None))
        self.label_2.setText(_translate("CellCommentDialog", "Comments:", None))
        self.okBtn.setText(_translate("CellCommentDialog", "OK", None))

