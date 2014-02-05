# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\vocal_parameters.ui'
#
# Created: Wed Feb 05 09:47:40 2014
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

class Ui_VocalParameterWidget(object):
    def setupUi(self, VocalParameterWidget):
        VocalParameterWidget.setObjectName(_fromUtf8("VocalParameterWidget"))
        VocalParameterWidget.resize(545, 427)
        self.verticalLayout = QtGui.QVBoxLayout(VocalParameterWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.wavrootdir_lnedt = QtGui.QLineEdit(VocalParameterWidget)
        self.wavrootdir_lnedt.setObjectName(_fromUtf8("wavrootdir_lnedt"))
        self.horizontalLayout_6.addWidget(self.wavrootdir_lnedt)
        self.wavrootdir_btn = QtGui.QPushButton(VocalParameterWidget)
        self.wavrootdir_btn.setObjectName(_fromUtf8("wavrootdir_btn"))
        self.horizontalLayout_6.addWidget(self.wavrootdir_btn)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.splitter_2 = QtGui.QSplitter(VocalParameterWidget)
        self.splitter_2.setOrientation(QtCore.Qt.Vertical)
        self.splitter_2.setObjectName(_fromUtf8("splitter_2"))
        self.splitter = QtGui.QSplitter(self.splitter_2)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.filetree_view = QtGui.QTreeView(self.splitter)
        self.filetree_view.setObjectName(_fromUtf8("filetree_view"))
        self.filelist_view = QtGui.QListView(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.filelist_view.sizePolicy().hasHeightForWidth())
        self.filelist_view.setSizePolicy(sizePolicy)
        self.filelist_view.setObjectName(_fromUtf8("filelist_view"))
        self.spec_preview = SpecWidget(self.splitter_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spec_preview.sizePolicy().hasHeightForWidth())
        self.spec_preview.setSizePolicy(sizePolicy)
        self.spec_preview.setMinimumSize(QtCore.QSize(0, 150))
        self.spec_preview.setObjectName(_fromUtf8("spec_preview"))
        self.verticalLayout.addWidget(self.splitter_2)
        self.common = CommonParameterWidget(VocalParameterWidget)
        self.common.setObjectName(_fromUtf8("common"))
        self.verticalLayout.addWidget(self.common)

        self.retranslateUi(VocalParameterWidget)
        QtCore.QObject.connect(self.filelist_view, QtCore.SIGNAL(_fromUtf8("clicked(QModelIndex)")), VocalParameterWidget.wavfile_clicked)
        QtCore.QObject.connect(self.filetree_view, QtCore.SIGNAL(_fromUtf8("doubleClicked(QModelIndex)")), VocalParameterWidget.wavdir_selected)
        QtCore.QObject.connect(self.wavrootdir_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), VocalParameterWidget.browse_wavdirs)
        QtCore.QMetaObject.connectSlotsByName(VocalParameterWidget)

    def retranslateUi(self, VocalParameterWidget):
        VocalParameterWidget.setWindowTitle(_translate("VocalParameterWidget", "Vocalization", None))
        self.wavrootdir_btn.setText(_translate("VocalParameterWidget", "change", None))

from spikeylab.plotting.custom_plots import SpecWidget
from spikeylab.stim.common_parameters import CommonParameterWidget
