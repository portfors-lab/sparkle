# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'explore_stim_editor.ui'
#
# Created: Thu Nov 20 18:08:31 2014
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
        self._2 = QtGui.QHBoxLayout()
        self._2.setObjectName(_fromUtf8("_2"))
        self.trackBtnLayout = QtGui.QHBoxLayout()
        self.trackBtnLayout.setObjectName(_fromUtf8("trackBtnLayout"))
        self._2.addLayout(self.trackBtnLayout)
        self.addBtn = QtGui.QPushButton(ExploreStimEditor)
        self.addBtn.setObjectName(_fromUtf8("addBtn"))
        self._2.addWidget(self.addBtn)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self._2.addItem(spacerItem)
        self.verticalLayout.addLayout(self._2)
        self.trackStack = QtGui.QStackedWidget(ExploreStimEditor)
        self.trackStack.setObjectName(_fromUtf8("trackStack"))
        self.verticalLayout.addWidget(self.trackStack)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.exNrepsSpnbx = QtGui.QSpinBox(ExploreStimEditor)
        self.exNrepsSpnbx.setMinimum(1)
        self.exNrepsSpnbx.setMaximum(100)
        self.exNrepsSpnbx.setProperty("value", 5)
        self.exNrepsSpnbx.setObjectName(_fromUtf8("exNrepsSpnbx"))
        self.gridLayout.addWidget(self.exNrepsSpnbx, 0, 1, 1, 1)
        self.label_39 = QtGui.QLabel(ExploreStimEditor)
        self.label_39.setObjectName(_fromUtf8("label_39"))
        self.gridLayout.addWidget(self.label_39, 0, 0, 1, 1)
        self.label_6 = QtGui.QLabel(ExploreStimEditor)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 1, 0, 1, 1)
        self.aosrSpnbx = SmartSpinBox(ExploreStimEditor)
        self.aosrSpnbx.setEnabled(False)
        self.aosrSpnbx.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.aosrSpnbx.setMaximum(500000.0)
        self.aosrSpnbx.setObjectName(_fromUtf8("aosrSpnbx"))
        self.gridLayout.addWidget(self.aosrSpnbx, 1, 1, 1, 1)
        self.funit_lbl = QtGui.QLabel(ExploreStimEditor)
        self.funit_lbl.setObjectName(_fromUtf8("funit_lbl"))
        self.gridLayout.addWidget(self.funit_lbl, 1, 2, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)

        self.retranslateUi(ExploreStimEditor)
        QtCore.QMetaObject.connectSlotsByName(ExploreStimEditor)

    def retranslateUi(self, ExploreStimEditor):
        ExploreStimEditor.setWindowTitle(_translate("ExploreStimEditor", "Form", None))
        self.addBtn.setText(_translate("ExploreStimEditor", "+", None))
        self.exNrepsSpnbx.setToolTip(_translate("ExploreStimEditor", "Number of presentations before plots reset", None))
        self.label_39.setText(_translate("ExploreStimEditor", "Reps", None))
        self.label_6.setText(_translate("ExploreStimEditor", "Gen. Sample rate", None))
        self.aosrSpnbx.setToolTip(_translate("ExploreStimEditor", "Stimulus output sampling rate", None))
        self.funit_lbl.setText(_translate("ExploreStimEditor", "kHz", None))

from spikeylab.gui.stim.smart_spinbox import SmartSpinBox
