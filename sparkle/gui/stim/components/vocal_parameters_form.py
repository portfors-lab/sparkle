# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'vocal_parameters.ui'
#
# Created: Fri Feb 27 16:36:56 2015
#      by: PyQt4 UI code generator 4.11.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

from sparkle.gui.plotting.pyqtgraph_widgets import SpecWidget
from sparkle.gui.stim.incrementer import IncrementInput
from sparkle.gui.stim.smart_spinbox import SmartSpinBox

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
        VocalParameterWidget.resize(535, 620)
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
        self.filelistView.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.filelistView.setObjectName(_fromUtf8("filelistView"))
        self.specPreview = SpecWidget(self.splitter_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.specPreview.sizePolicy().hasHeightForWidth())
        self.specPreview.setSizePolicy(sizePolicy)
        self.specPreview.setMinimumSize(QtCore.QSize(0, 0))
        self.specPreview.setObjectName(_fromUtf8("specPreview"))
        self.verticalLayout.addWidget(self.splitter_2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label = QtGui.QLabel(VocalParameterWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.nfiles = QtGui.QLabel(VocalParameterWidget)
        self.nfiles.setObjectName(_fromUtf8("nfiles"))
        self.horizontalLayout.addWidget(self.nfiles)
        self.orderBtn = QtGui.QPushButton(VocalParameterWidget)
        self.orderBtn.setObjectName(_fromUtf8("orderBtn"))
        self.horizontalLayout.addWidget(self.orderBtn)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout_5 = QtGui.QGridLayout()
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.risefallSpnbx = SmartSpinBox(VocalParameterWidget)
        self.risefallSpnbx.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.risefallSpnbx.setDecimals(3)
        self.risefallSpnbx.setMaximum(500.0)
        self.risefallSpnbx.setObjectName(_fromUtf8("risefallSpnbx"))
        self.gridLayout_5.addWidget(self.risefallSpnbx, 3, 1, 1, 1)
        self.dbSpnbx = IncrementInput(VocalParameterWidget)
        self.dbSpnbx.setObjectName(_fromUtf8("dbSpnbx"))
        self.gridLayout_5.addWidget(self.dbSpnbx, 0, 1, 1, 1)
        self.label_32 = QtGui.QLabel(VocalParameterWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_32.sizePolicy().hasHeightForWidth())
        self.label_32.setSizePolicy(sizePolicy)
        self.label_32.setObjectName(_fromUtf8("label_32"))
        self.gridLayout_5.addWidget(self.label_32, 1, 0, 1, 1)
        self.label_42 = QtGui.QLabel(VocalParameterWidget)
        self.label_42.setObjectName(_fromUtf8("label_42"))
        self.gridLayout_5.addWidget(self.label_42, 0, 0, 1, 1)
        self.label_40 = QtGui.QLabel(VocalParameterWidget)
        self.label_40.setObjectName(_fromUtf8("label_40"))
        self.gridLayout_5.addWidget(self.label_40, 3, 0, 1, 1)
        self.durSpnbx = SmartSpinBox(VocalParameterWidget)
        self.durSpnbx.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.durSpnbx.setDecimals(3)
        self.durSpnbx.setMaximum(2000.0)
        self.durSpnbx.setObjectName(_fromUtf8("durSpnbx"))
        self.gridLayout_5.addWidget(self.durSpnbx, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_5)

        self.retranslateUi(VocalParameterWidget)
        QtCore.QObject.connect(self.filetreeView, QtCore.SIGNAL(_fromUtf8("doubleClicked(QModelIndex)")), VocalParameterWidget.wavdirSelected)
        QtCore.QObject.connect(self.wavrootdirBtn, QtCore.SIGNAL(_fromUtf8("clicked()")), VocalParameterWidget.browseWavdirs)
        QtCore.QObject.connect(self.orderBtn, QtCore.SIGNAL(_fromUtf8("clicked()")), VocalParameterWidget.setOrder)
        QtCore.QMetaObject.connectSlotsByName(VocalParameterWidget)

    def retranslateUi(self, VocalParameterWidget):
        VocalParameterWidget.setWindowTitle(_translate("VocalParameterWidget", "Vocalization", None))
        self.wavrootdirBtn.setText(_translate("VocalParameterWidget", "change", None))
        self.label.setText(_translate("VocalParameterWidget", "Files selected:", None))
        self.nfiles.setText(_translate("VocalParameterWidget", "0", None))
        self.orderBtn.setText(_translate("VocalParameterWidget", "Order...", None))
        self.label_32.setText(_translate("VocalParameterWidget", "Duration", None))
        self.label_42.setText(_translate("VocalParameterWidget", "Intensity", None))
        self.label_40.setText(_translate("VocalParameterWidget", "Rise fall time", None))
