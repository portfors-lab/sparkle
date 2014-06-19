# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\vocal_parameters.ui'
#
# Created: Wed Jun 18 17:25:42 2014
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
        self.wavrootdirLnedt = QtGui.QLineEdit(VocalParameterWidget)
        self.wavrootdirLnedt.setObjectName(_fromUtf8("wavrootdirLnedt"))
        self.horizontalLayout_6.addWidget(self.wavrootdirLnedt)
        self.wavrootdirBtn = QtGui.QPushButton(VocalParameterWidget)
        self.wavrootdirBtn.setObjectName(_fromUtf8("wavrootdirBtn"))
        self.horizontalLayout_6.addWidget(self.wavrootdirBtn)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.splitter_2 = QtGui.QSplitter(VocalParameterWidget)
        self.splitter_2.setOrientation(QtCore.Qt.Vertical)
        self.splitter_2.setObjectName(_fromUtf8("splitter_2"))
        self.splitter = QtGui.QSplitter(self.splitter_2)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.filetreeView = QtGui.QTreeView(self.splitter)
        self.filetreeView.setObjectName(_fromUtf8("filetreeView"))
        self.filelistView = QtGui.QListView(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.filelistView.sizePolicy().hasHeightForWidth())
        self.filelistView.setSizePolicy(sizePolicy)
        self.filelistView.setObjectName(_fromUtf8("filelistView"))
        self.specPreview = SpecWidget(self.splitter_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.specPreview.sizePolicy().hasHeightForWidth())
        self.specPreview.setSizePolicy(sizePolicy)
        self.specPreview.setMinimumSize(QtCore.QSize(0, 150))
        self.specPreview.setObjectName(_fromUtf8("specPreview"))
        self.verticalLayout.addWidget(self.splitter_2)
        self.common = CommonParameterWidget(VocalParameterWidget)
        self.common.setObjectName(_fromUtf8("common"))
        self.verticalLayout.addWidget(self.common)

        self.retranslateUi(VocalParameterWidget)
        QtCore.QObject.connect(self.filelistView, QtCore.SIGNAL(_fromUtf8("clicked(QModelIndex)")), VocalParameterWidget.wavfileClicked)
        QtCore.QObject.connect(self.filetreeView, QtCore.SIGNAL(_fromUtf8("doubleClicked(QModelIndex)")), VocalParameterWidget.wavdirSelected)
        QtCore.QObject.connect(self.wavrootdirBtn, QtCore.SIGNAL(_fromUtf8("clicked()")), VocalParameterWidget.browseWavdirs)
        QtCore.QMetaObject.connectSlotsByName(VocalParameterWidget)

    def retranslateUi(self, VocalParameterWidget):
        VocalParameterWidget.setWindowTitle(_translate("VocalParameterWidget", "Vocalization", None))
        self.wavrootdirBtn.setText(_translate("VocalParameterWidget", "change", None))

from spikeylab.plotting.pyqtgraph_widgets import SpecWidget
from spikeylab.stim.common_parameters import CommonParameterWidget
