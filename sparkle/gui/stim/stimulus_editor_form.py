# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'stimulus_editor.ui'
#
# Created: Fri Dec  5 14:44:51 2014
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

class Ui_StimulusEditor(object):
    def setupUi(self, StimulusEditor):
        StimulusEditor.setObjectName(_fromUtf8("StimulusEditor"))
        StimulusEditor.resize(941, 737)
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
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 641, 442))
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
        self.templateBox = ComponentTemplateTable(self.frame)
        self.templateBox.setObjectName(_fromUtf8("templateBox"))
        self.verticalLayout.addWidget(self.templateBox)
        self.modeLbl = QtGui.QLabel(self.frame)
        self.modeLbl.setEnabled(True)
        self.modeLbl.setFrameShape(QtGui.QFrame.Panel)
        self.modeLbl.setFrameShadow(QtGui.QFrame.Sunken)
        self.modeLbl.setAlignment(QtCore.Qt.AlignCenter)
        self.modeLbl.setObjectName(_fromUtf8("modeLbl"))
        self.verticalLayout.addWidget(self.modeLbl)
        self.hintTxedt = QtGui.QTextEdit(self.frame)
        self.hintTxedt.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.hintTxedt.sizePolicy().hasHeightForWidth())
        self.hintTxedt.setSizePolicy(sizePolicy)
        self.hintTxedt.setMinimumSize(QtCore.QSize(0, 60))
        self.hintTxedt.setMaximumSize(QtCore.QSize(16777215, 100))
        self.hintTxedt.setFrameShape(QtGui.QFrame.Panel)
        self.hintTxedt.setObjectName(_fromUtf8("hintTxedt"))
        self.verticalLayout.addWidget(self.hintTxedt)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.frame)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.horizontalSlider = QtGui.QSlider(self.frame)
        self.horizontalSlider.setMinimum(1)
        self.horizontalSlider.setMaximum(12)
        self.horizontalSlider.setProperty("value", 10)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName(_fromUtf8("horizontalSlider"))
        self.gridLayout.addWidget(self.horizontalSlider, 0, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.nrepsSpnbx = QtGui.QSpinBox(self.frame)
        self.nrepsSpnbx.setMaximum(1000)
        self.nrepsSpnbx.setObjectName(_fromUtf8("nrepsSpnbx"))
        self.gridLayout_3.addWidget(self.nrepsSpnbx, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setFrameShape(QtGui.QFrame.NoFrame)
        self.label_2.setFrameShadow(QtGui.QFrame.Plain)
        self.label_2.setWordWrap(False)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_3.addWidget(self.label_2, 0, 0, 1, 1)
        self.label_3 = QtGui.QLabel(self.frame)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_3.addWidget(self.label_3, 1, 0, 1, 1)
        self.ntracesLbl = QtGui.QLabel(self.frame)
        self.ntracesLbl.setObjectName(_fromUtf8("ntracesLbl"))
        self.gridLayout_3.addWidget(self.ntracesLbl, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_3)
        self.previewBtn = QtGui.QPushButton(self.frame)
        self.previewBtn.setObjectName(_fromUtf8("previewBtn"))
        self.verticalLayout.addWidget(self.previewBtn)
        self.saveBtn = QtGui.QPushButton(self.frame)
        self.saveBtn.setObjectName(_fromUtf8("saveBtn"))
        self.verticalLayout.addWidget(self.saveBtn)
        self.okBtn = QtGui.QPushButton(self.frame)
        self.okBtn.setObjectName(_fromUtf8("okBtn"))
        self.verticalLayout.addWidget(self.okBtn)
        self.verticalLayout_2.addWidget(self.splitter)
        self.parametizer = HidableParameterEditor(StimulusEditor)
        self.parametizer.setMinimumSize(QtCore.QSize(0, 50))
        self.parametizer.setObjectName(_fromUtf8("parametizer"))
        self.verticalLayout_2.addWidget(self.parametizer)

        self.retranslateUi(StimulusEditor)
        QtCore.QObject.connect(self.nrepsSpnbx, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), StimulusEditor.setRepCount)
        QtCore.QObject.connect(self.okBtn, QtCore.SIGNAL(_fromUtf8("clicked()")), StimulusEditor.close)
        QtCore.QObject.connect(self.previewBtn, QtCore.SIGNAL(_fromUtf8("clicked()")), StimulusEditor.preview)
        QtCore.QObject.connect(self.saveBtn, QtCore.SIGNAL(_fromUtf8("clicked()")), StimulusEditor.saveStimulus)
        QtCore.QObject.connect(self.horizontalSlider, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.trackview.setPixelScale)
        QtCore.QMetaObject.connectSlotsByName(StimulusEditor)

    def retranslateUi(self, StimulusEditor):
        StimulusEditor.setWindowTitle(_translate("StimulusEditor", "Form", None))
        self.trackview.setToolTip(_translate("StimulusEditor", "Stimulus View", None))
        self.label_5.setText(_translate("StimulusEditor", "Components:", None))
        self.modeLbl.setText(_translate("StimulusEditor", "BUILDING MODE", None))
        self.hintTxedt.setToolTip(_translate("StimulusEditor", "Hint", None))
        self.hintTxedt.setHtml(_translate("StimulusEditor", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Cantarell\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-size:10pt;\">Drag Components onto view to Add. </span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'MS Shell Dlg 2\'; font-size:10pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-size:10pt;\">Double click to edit. </span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'MS Shell Dlg 2\'; font-size:10pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-size:10pt;\">Drag to move.</span></p></body></html>", None))
        self.label.setText(_translate("StimulusEditor", "Grid scale(ms):", None))
        self.horizontalSlider.setToolTip(_translate("StimulusEditor", "Zoom", None))
        self.nrepsSpnbx.setToolTip(_translate("StimulusEditor", "Number of times to repeat (also applies to each expanded stimulus if auto-parameters are used)", None))
        self.label_2.setText(_translate("StimulusEditor", "Reps", None))
        self.label_3.setText(_translate("StimulusEditor", "Traces", None))
        self.ntracesLbl.setToolTip(_translate("StimulusEditor", "Number of unique stimuli (including expanded auto-parameters) in this test", None))
        self.ntracesLbl.setText(_translate("StimulusEditor", "1", None))
        self.previewBtn.setToolTip(_translate("StimulusEditor", "Generate preview spectrogram", None))
        self.previewBtn.setText(_translate("StimulusEditor", "Preview Spectrogram", None))
        self.saveBtn.setToolTip(_translate("StimulusEditor", "Save stimulus template to file", None))
        self.saveBtn.setText(_translate("StimulusEditor", "Save As...", None))
        self.okBtn.setText(_translate("StimulusEditor", "Ok", None))

from sparkle.gui.stim.stimulusview import StimulusView
from sparkle.gui.stim.component_label import ComponentTemplateTable
from sparkle.gui.stim.auto_parameters_editor import HidableParameterEditor
