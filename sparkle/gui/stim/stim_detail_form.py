# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\stim_detail.ui'
#
# Created: Wed Jun 18 17:00:54 2014
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

class Ui_StimDetailWidget(object):
    def setupUi(self, StimDetailWidget):
        StimDetailWidget.setObjectName(_fromUtf8("StimDetailWidget"))
        StimDetailWidget.resize(489, 403)
        self.verticalLayout = QtGui.QVBoxLayout(StimDetailWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(StimDetailWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.testNum = QtGui.QLabel(StimDetailWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.testNum.setFont(font)
        self.testNum.setObjectName(_fromUtf8("testNum"))
        self.horizontalLayout.addWidget(self.testNum)
        self.label_2 = QtGui.QLabel(StimDetailWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout.addWidget(self.label_2)
        self.traceNum = QtGui.QLabel(StimDetailWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.traceNum.setFont(font)
        self.traceNum.setObjectName(_fromUtf8("traceNum"))
        self.horizontalLayout.addWidget(self.traceNum)
        self.label_3 = QtGui.QLabel(StimDetailWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_3.setFont(font)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout.addWidget(self.label_3)
        self.repNum = QtGui.QLabel(StimDetailWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.repNum.setFont(font)
        self.repNum.setObjectName(_fromUtf8("repNum"))
        self.horizontalLayout.addWidget(self.repNum)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_7 = QtGui.QLabel(StimDetailWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_7.setFont(font)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout.addWidget(self.label_7, 0, 0, 1, 1)
        self.overAtten = QtGui.QLabel(StimDetailWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.overAtten.setFont(font)
        self.overAtten.setObjectName(_fromUtf8("overAtten"))
        self.gridLayout.addWidget(self.overAtten, 0, 1, 1, 1)
        self.label_11 = QtGui.QLabel(StimDetailWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_11.setFont(font)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.gridLayout.addWidget(self.label_11, 0, 2, 1, 1)
        self.label_8 = QtGui.QLabel(StimDetailWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_8.setFont(font)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout.addWidget(self.label_8, 1, 0, 1, 1)
        self.traceType = QtGui.QLabel(StimDetailWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.traceType.setFont(font)
        self.traceType.setObjectName(_fromUtf8("traceType"))
        self.gridLayout.addWidget(self.traceType, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.label_9 = QtGui.QLabel(StimDetailWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_9.setFont(font)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.verticalLayout.addWidget(self.label_9)
        self.scrollArea = QtGui.QScrollArea(StimDetailWidget)
        self.scrollArea.setFrameShape(QtGui.QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 471, 280))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.componentDetails = ComponentsDetailWidget(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.componentDetails.sizePolicy().hasHeightForWidth())
        self.componentDetails.setSizePolicy(sizePolicy)
        self.componentDetails.setObjectName(_fromUtf8("componentDetails"))
        self.verticalLayout_2.addWidget(self.componentDetails)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)

        self.retranslateUi(StimDetailWidget)
        QtCore.QMetaObject.connectSlotsByName(StimDetailWidget)

    def retranslateUi(self, StimDetailWidget):
        StimDetailWidget.setWindowTitle(_translate("StimDetailWidget", "Form", None))
        self.label.setText(_translate("StimDetailWidget", "Test:", None))
        self.testNum.setText(_translate("StimDetailWidget", "0", None))
        self.label_2.setText(_translate("StimDetailWidget", "Trace:", None))
        self.traceNum.setText(_translate("StimDetailWidget", "0", None))
        self.label_3.setText(_translate("StimDetailWidget", "Rep:", None))
        self.repNum.setText(_translate("StimDetailWidget", "0", None))
        self.label_7.setText(_translate("StimDetailWidget", "Undesired Attenuation:", None))
        self.overAtten.setText(_translate("StimDetailWidget", "0", None))
        self.label_11.setText(_translate("StimDetailWidget", "dB", None))
        self.label_8.setText(_translate("StimDetailWidget", "Test Type:", None))
        self.traceType.setText(_translate("StimDetailWidget", "audio", None))
        self.label_9.setText(_translate("StimDetailWidget", "Components:", None))

from sparkle.gui.stim.component_detail import ComponentsDetailWidget
