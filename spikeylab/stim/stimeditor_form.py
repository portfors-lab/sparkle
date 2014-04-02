# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\stimulus_editor.ui'
#
# Created: Tue Apr 01 17:23:18 2014
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

class Ui_StimulusEditor(object):
    def setupUi(self, StimulusEditor):
        StimulusEditor.setObjectName(_fromUtf8("StimulusEditor"))
        StimulusEditor.resize(942, 634)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(StimulusEditor.sizePolicy().hasHeightForWidth())
        StimulusEditor.setSizePolicy(sizePolicy)
        self.verticalLayout_2 = QtGui.QVBoxLayout(StimulusEditor)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.splitter = QtGui.QSplitter(StimulusEditor)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.scrollArea = QtGui.QScrollArea(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setMinimumSize(QtCore.QSize(500, 0))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 643, 314))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_4.setMargin(0)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.trackview = StimulusView(self.scrollAreaWidgetContents)
        self.trackview.setObjectName(_fromUtf8("trackview"))
        self.verticalLayout_4.addWidget(self.trackview)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.frame = QtGui.QFrame(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.frame.setBaseSize(QtCore.QSize(200, 0))
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_5 = QtGui.QLabel(self.frame)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.verticalLayout.addWidget(self.label_5)
        self.template_box = ComponentTemplateTable(self.frame)
        self.template_box.setObjectName(_fromUtf8("template_box"))
        self.verticalLayout.addWidget(self.template_box)
        self.hint_txedt = QtGui.QTextEdit(self.frame)
        self.hint_txedt.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.hint_txedt.sizePolicy().hasHeightForWidth())
        self.hint_txedt.setSizePolicy(sizePolicy)
        self.hint_txedt.setMinimumSize(QtCore.QSize(0, 60))
        self.hint_txedt.setMaximumSize(QtCore.QSize(16777215, 100))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.hint_txedt.setFont(font)
        self.hint_txedt.setFrameShape(QtGui.QFrame.Panel)
        self.hint_txedt.setObjectName(_fromUtf8("hint_txedt"))
        self.verticalLayout.addWidget(self.hint_txedt)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.nreps_spnbx = QtGui.QSpinBox(self.frame)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.nreps_spnbx.setFont(font)
        self.nreps_spnbx.setObjectName(_fromUtf8("nreps_spnbx"))
        self.gridLayout_3.addWidget(self.nreps_spnbx, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setFrameShape(QtGui.QFrame.NoFrame)
        self.label_2.setFrameShadow(QtGui.QFrame.Plain)
        self.label_2.setWordWrap(False)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_3.addWidget(self.label_2, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_3)
        self.preview_btn = QtGui.QPushButton(self.frame)
        self.preview_btn.setObjectName(_fromUtf8("preview_btn"))
        self.verticalLayout.addWidget(self.preview_btn)
        self.save_btn = QtGui.QPushButton(self.frame)
        self.save_btn.setObjectName(_fromUtf8("save_btn"))
        self.verticalLayout.addWidget(self.save_btn)
        self.ok_btn = QtGui.QPushButton(self.frame)
        self.ok_btn.setObjectName(_fromUtf8("ok_btn"))
        self.verticalLayout.addWidget(self.ok_btn)
        self.verticalLayout_2.addWidget(self.splitter)
        self.parametizer = HidableParameterEditor(StimulusEditor)
        self.parametizer.setObjectName(_fromUtf8("parametizer"))
        self.verticalLayout_2.addWidget(self.parametizer)

        self.retranslateUi(StimulusEditor)
        QtCore.QObject.connect(self.nreps_spnbx, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), StimulusEditor.setRepCount)
        QtCore.QObject.connect(self.ok_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), StimulusEditor.close)
        QtCore.QObject.connect(self.preview_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), StimulusEditor.preview)
        QtCore.QObject.connect(self.save_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), StimulusEditor.saveStimulus)
        QtCore.QMetaObject.connectSlotsByName(StimulusEditor)

    def retranslateUi(self, StimulusEditor):
        StimulusEditor.setWindowTitle(_translate("StimulusEditor", "Form", None))
        self.trackview.setToolTip(_translate("StimulusEditor", "Stimulus View", None))
        self.label_5.setText(_translate("StimulusEditor", "Components:", None))
        self.hint_txedt.setHtml(_translate("StimulusEditor", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Drag Components onto view to Add. Double click to edit; right drag to move.</p></body></html>", None))
        self.label_2.setText(_translate("StimulusEditor", "Reps", None))
        self.preview_btn.setText(_translate("StimulusEditor", "Preview Spectrogram", None))
        self.save_btn.setText(_translate("StimulusEditor", "Save As...", None))
        self.ok_btn.setText(_translate("StimulusEditor", "Ok", None))

from spikeylab.stim.auto_parameters_editor import HidableParameterEditor
from spikeylab.stim.stimulusview import StimulusView
from spikeylab.stim.component_label import ComponentTemplateTable
