# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'explore_stim_editor.ui'
#
# Created: Wed Nov 19 18:04:03 2014
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
        self.scrollArea = QtGui.QScrollArea(ExploreStimEditor)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents_3 = QtGui.QWidget()
        self.scrollAreaWidgetContents_3.setGeometry(QtCore.QRect(0, 0, 493, 254))
        self.scrollAreaWidgetContents_3.setObjectName(_fromUtf8("scrollAreaWidgetContents_3"))
        self.layout = QtGui.QVBoxLayout(self.scrollAreaWidgetContents_3)
        self.layout.setObjectName(_fromUtf8("layout"))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents_3)
        self.verticalLayout.addWidget(self.scrollArea)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.addBtn = QtGui.QPushButton(ExploreStimEditor)
        self.addBtn.setObjectName(_fromUtf8("addBtn"))
        self.horizontalLayout.addWidget(self.addBtn)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
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
