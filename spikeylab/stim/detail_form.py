# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\stim_detail.ui'
#
# Created: Tue Apr 08 12:57:21 2014
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
        self.test_num = QtGui.QLabel(StimDetailWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.test_num.setFont(font)
        self.test_num.setObjectName(_fromUtf8("test_num"))
        self.horizontalLayout.addWidget(self.test_num)
        self.label_2 = QtGui.QLabel(StimDetailWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout.addWidget(self.label_2)
        self.trace_num = QtGui.QLabel(StimDetailWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.trace_num.setFont(font)
        self.trace_num.setObjectName(_fromUtf8("trace_num"))
        self.horizontalLayout.addWidget(self.trace_num)
        self.label_3 = QtGui.QLabel(StimDetailWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_3.setFont(font)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout.addWidget(self.label_3)
        self.rep_num = QtGui.QLabel(StimDetailWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.rep_num.setFont(font)
        self.rep_num.setObjectName(_fromUtf8("rep_num"))
        self.horizontalLayout.addWidget(self.rep_num)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_7 = QtGui.QLabel(StimDetailWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_7.setFont(font)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout.addWidget(self.label_7, 0, 0, 1, 1)
        self.over_atten = QtGui.QLabel(StimDetailWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.over_atten.setFont(font)
        self.over_atten.setObjectName(_fromUtf8("over_atten"))
        self.gridLayout.addWidget(self.over_atten, 0, 1, 1, 1)
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
        self.trace_type = QtGui.QLabel(StimDetailWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.trace_type.setFont(font)
        self.trace_type.setObjectName(_fromUtf8("trace_type"))
        self.gridLayout.addWidget(self.trace_type, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.label_9 = QtGui.QLabel(StimDetailWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_9.setFont(font)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.verticalLayout.addWidget(self.label_9)
        self.component_details = ComponentDetailWidget(StimDetailWidget)
        self.component_details.setObjectName(_fromUtf8("component_details"))
        self.verticalLayout.addWidget(self.component_details)
        self.protocol_progress_bar = QtGui.QProgressBar(StimDetailWidget)
        self.protocol_progress_bar.setProperty("value", 0)
        self.protocol_progress_bar.setObjectName(_fromUtf8("protocol_progress_bar"))
        self.verticalLayout.addWidget(self.protocol_progress_bar)

        self.retranslateUi(StimDetailWidget)
        QtCore.QMetaObject.connectSlotsByName(StimDetailWidget)

    def retranslateUi(self, StimDetailWidget):
        StimDetailWidget.setWindowTitle(_translate("StimDetailWidget", "Form", None))
        self.label.setText(_translate("StimDetailWidget", "Test:", None))
        self.test_num.setText(_translate("StimDetailWidget", "0", None))
        self.label_2.setText(_translate("StimDetailWidget", "Trace:", None))
        self.trace_num.setText(_translate("StimDetailWidget", "0", None))
        self.label_3.setText(_translate("StimDetailWidget", "Rep:", None))
        self.rep_num.setText(_translate("StimDetailWidget", "0", None))
        self.label_7.setText(_translate("StimDetailWidget", "Undesired Attenuation:", None))
        self.over_atten.setText(_translate("StimDetailWidget", "0", None))
        self.label_11.setText(_translate("StimDetailWidget", "dB", None))
        self.label_8.setText(_translate("StimDetailWidget", "Test Type:", None))
        self.trace_type.setText(_translate("StimDetailWidget", "audio", None))
        self.label_9.setText(_translate("StimDetailWidget", "Components:", None))

from spikeylab.stim.component_detail import ComponentDetailWidget
