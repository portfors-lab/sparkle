# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'function_generator.ui'
#
# Created: Mon Apr 15 22:59:07 2013
#      by: PyQt4 UI code generator 4.10
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

class Ui_fgform(object):
    def setupUi(self, fgform):
        fgform.setObjectName(_fromUtf8("fgform"))
        fgform.resize(661, 606)
        self.widget = QtGui.QWidget(fgform)
        self.widget.setGeometry(QtCore.QRect(10, -9, 647, 608))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.gridLayout_2 = QtGui.QGridLayout(self.widget)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.ttl = QtGui.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.ttl.setFont(font)
        self.ttl.setLineWidth(6)
        self.ttl.setScaledContents(False)
        self.ttl.setObjectName(_fromUtf8("ttl"))
        self.verticalLayout.addWidget(self.ttl)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.widget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)
        self.sr_edit = QtGui.QLineEdit(self.widget)
        self.sr_edit.setObjectName(_fromUtf8("sr_edit"))
        self.gridLayout.addWidget(self.sr_edit, 0, 2, 1, 1)
        self.npts_edit = QtGui.QLineEdit(self.widget)
        self.npts_edit.setObjectName(_fromUtf8("npts_edit"))
        self.gridLayout.addWidget(self.npts_edit, 1, 2, 1, 1)
        self.label_3 = QtGui.QLabel(self.widget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.label_4 = QtGui.QLabel(self.widget)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.label_5 = QtGui.QLabel(self.widget)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.widget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 2)
        self.amp_edit = QtGui.QLineEdit(self.widget)
        self.amp_edit.setObjectName(_fromUtf8("amp_edit"))
        self.gridLayout.addWidget(self.amp_edit, 3, 2, 1, 1)
        self.freq_edit = QtGui.QLineEdit(self.widget)
        self.freq_edit.setObjectName(_fromUtf8("freq_edit"))
        self.gridLayout.addWidget(self.freq_edit, 4, 2, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_6 = QtGui.QLabel(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.horizontalLayout.addWidget(self.label_6)
        self.aochan_box = QtGui.QComboBox(self.widget)
        self.aochan_box.setObjectName(_fromUtf8("aochan_box"))
        self.horizontalLayout.addWidget(self.aochan_box)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label_7 = QtGui.QLabel(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.horizontalLayout_3.addWidget(self.label_7)
        self.aichan_box = QtGui.QComboBox(self.widget)
        self.aichan_box.setObjectName(_fromUtf8("aichan_box"))
        self.horizontalLayout_3.addWidget(self.aichan_box)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.start_button = QtGui.QPushButton(self.widget)
        self.start_button.setObjectName(_fromUtf8("start_button"))
        self.horizontalLayout_2.addWidget(self.start_button)
        self.stop_button = QtGui.QPushButton(self.widget)
        self.stop_button.setObjectName(_fromUtf8("stop_button"))
        self.horizontalLayout_2.addWidget(self.stop_button)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.gridLayout_2.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.outplot = MatplotlibWidget(self.widget)
        self.outplot.setObjectName(_fromUtf8("outplot"))
        self.gridLayout_2.addWidget(self.outplot, 0, 1, 1, 1)
        self.inplot = MatplotlibWidget(self.widget)
        self.inplot.setObjectName(_fromUtf8("inplot"))
        self.gridLayout_2.addWidget(self.inplot, 1, 1, 1, 1)

        self.retranslateUi(fgform)
        QtCore.QMetaObject.connectSlotsByName(fgform)

    def retranslateUi(self, fgform):
        fgform.setWindowTitle(_translate("fgform", "Form", None))
        self.ttl.setText(_translate("fgform", "Function Generator", None))
        self.label.setText(_translate("fgform", "sample rate (s/sec):", None))
        self.sr_edit.setText(_translate("fgform", "1000", None))
        self.npts_edit.setText(_translate("fgform", "1000", None))
        self.label_3.setText(_translate("fgform", "Function", None))
        self.label_4.setText(_translate("fgform", "amplitude :", None))
        self.label_5.setText(_translate("fgform", "frequency :", None))
        self.label_2.setText(_translate("fgform", "no. of  points:", None))
        self.amp_edit.setText(_translate("fgform", "1", None))
        self.freq_edit.setText(_translate("fgform", "1", None))
        self.label_6.setText(_translate("fgform", "AO channel :", None))
        self.label_7.setText(_translate("fgform", "AI Channel :", None))
        self.start_button.setText(_translate("fgform", "Start", None))
        self.stop_button.setText(_translate("fgform", "Stop", None))

from matplotlibwidget import MatplotlibWidget
