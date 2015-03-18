# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'explore_stim_editor.ui'
#
# Created: Fri Dec  5 14:45:05 2014
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_ExploreStimEditor(object):
    def setupUi(self, ExploreStimEditor):
        ExploreStimEditor.setObjectName(_fromUtf8("ExploreStimEditor"))
        ExploreStimEditor.resize(513, 393)
        self.verticalLayout = QtGui.QVBoxLayout(ExploreStimEditor)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self._ = QtGui.QHBoxLayout()
        self._.setObjectName(_fromUtf8("_"))
        self.trackBtnLayout = QtGui.QHBoxLayout()
        self.trackBtnLayout.setObjectName(_fromUtf8("trackBtnLayout"))
        self._.addLayout(self.trackBtnLayout)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self._.addItem(spacerItem)
        self.addBtn = QtGui.QPushButton(ExploreStimEditor)
        self.addBtn.setObjectName(_fromUtf8("addBtn"))
        self._.addWidget(self.addBtn)
        self.verticalLayout.addLayout(self._)
        self.trackStack = QtGui.QStackedWidget(ExploreStimEditor)
        self.trackStack.setObjectName(_fromUtf8("trackStack"))
        self.verticalLayout.addWidget(self.trackStack)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.exNrepsSpnbx = QtGui.QSpinBox(ExploreStimEditor)
        self.exNrepsSpnbx.setMinimum(1)
        self.exNrepsSpnbx.setMaximum(1000)
        self.exNrepsSpnbx.setProperty("value", 5)
        self.exNrepsSpnbx.setObjectName(_fromUtf8("exNrepsSpnbx"))
        self.gridLayout.addWidget(self.exNrepsSpnbx, 0, 1, 1, 1)
        self.label_6 = QtGui.QLabel(ExploreStimEditor)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 1, 0, 1, 1)
        self.aofsSpnbx = SmartSpinBox(ExploreStimEditor)
        self.aofsSpnbx.setEnabled(False)
        self.aofsSpnbx.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.aofsSpnbx.setMaximum(500000.0)
        self.aofsSpnbx.setObjectName(_fromUtf8("aofsSpnbx"))
        self.gridLayout.addWidget(self.aofsSpnbx, 1, 1, 1, 1)
        self.label_39 = QtGui.QLabel(ExploreStimEditor)
        self.label_39.setObjectName(_fromUtf8("label_39"))
        self.gridLayout.addWidget(self.label_39, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)

        self.retranslateUi(ExploreStimEditor)
        QtCore.QMetaObject.connectSlotsByName(ExploreStimEditor)

    def retranslateUi(self, ExploreStimEditor):
        ExploreStimEditor.setWindowTitle(_translate("ExploreStimEditor", "Form", None))
        self.addBtn.setText(_translate("ExploreStimEditor", "+", None))
        self.exNrepsSpnbx.setToolTip(_translate("ExploreStimEditor", "Number of presentations before plots reset", None))
        self.label_6.setText(_translate("ExploreStimEditor", "Gen. Sample rate", None))
        self.aofsSpnbx.setToolTip(_translate("ExploreStimEditor", "Stimulus output sampling rate", None))
        self.label_39.setText(_translate("ExploreStimEditor", "Reps", None))

from sparkle.gui.stim.smart_spinbox import SmartSpinBox
