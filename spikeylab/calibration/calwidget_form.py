# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\calibration_widget.ui'
#
# Created: Wed Apr 09 12:51:46 2014
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

class Ui_CalibrationWidget(object):
    def setupUi(self, CalibrationWidget):
        CalibrationWidget.setObjectName(_fromUtf8("CalibrationWidget"))
        CalibrationWidget.resize(750, 380)
        self.verticalLayout = QtGui.QVBoxLayout(CalibrationWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.calgroup = QtGui.QGroupBox(CalibrationWidget)
        self.calgroup.setMaximumSize(QtCore.QSize(16777215, 50))
        font = QtGui.QFont()
        font.setKerning(True)
        self.calgroup.setFont(font)
        self.calgroup.setTitle(_fromUtf8(""))
        self.calgroup.setFlat(False)
        self.calgroup.setCheckable(False)
        self.calgroup.setObjectName(_fromUtf8("calgroup"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.calgroup)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.savecal_ckbx = QtGui.QRadioButton(self.calgroup)
        self.savecal_ckbx.setChecked(True)
        self.savecal_ckbx.setObjectName(_fromUtf8("savecal_ckbx"))
        self.horizontalLayout_4.addWidget(self.savecal_ckbx)
        self.applycal_ckbx = QtGui.QRadioButton(self.calgroup)
        self.applycal_ckbx.setObjectName(_fromUtf8("applycal_ckbx"))
        self.horizontalLayout_4.addWidget(self.applycal_ckbx)
        self.label_2 = QtGui.QLabel(self.calgroup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_4.addWidget(self.label_2)
        self.nreps_spnbx = QtGui.QSpinBox(self.calgroup)
        self.nreps_spnbx.setMaximumSize(QtCore.QSize(100, 16777215))
        self.nreps_spnbx.setProperty("value", 1)
        self.nreps_spnbx.setObjectName(_fromUtf8("nreps_spnbx"))
        self.horizontalLayout_4.addWidget(self.nreps_spnbx)
        self.verticalLayout.addWidget(self.calgroup)
        self.frame = QtGui.QFrame(CalibrationWidget)
        self.frame.setEnabled(False)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.test_type_grp = QtGui.QGroupBox(self.frame)
        self.test_type_grp.setEnabled(False)
        self.test_type_grp.setObjectName(_fromUtf8("test_type_grp"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.test_type_grp)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.cal_type_cmbbx = QtGui.QComboBox(self.test_type_grp)
        self.cal_type_cmbbx.setObjectName(_fromUtf8("cal_type_cmbbx"))
        self.cal_type_cmbbx.addItem(_fromUtf8(""))
        self.horizontalLayout.addWidget(self.cal_type_cmbbx)
        self.verticalLayout_2.addWidget(self.test_type_grp)
        self.caleditor_stack = QtGui.QStackedWidget(self.frame)
        self.caleditor_stack.setObjectName(_fromUtf8("caleditor_stack"))
        self.page = QtGui.QWidget()
        self.page.setObjectName(_fromUtf8("page"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.page)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.curve_widget = TuningCurveEditor(self.page)
        self.curve_widget.setObjectName(_fromUtf8("curve_widget"))
        self.verticalLayout_3.addWidget(self.curve_widget)
        self.caleditor_stack.addWidget(self.page)
        self.verticalLayout_2.addWidget(self.caleditor_stack)
        self.verticalLayout.addWidget(self.frame)

        self.retranslateUi(CalibrationWidget)
        self.caleditor_stack.setCurrentIndex(0)
        QtCore.QObject.connect(self.cal_type_cmbbx, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.caleditor_stack.setCurrentIndex)
        QtCore.QObject.connect(self.applycal_ckbx, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.frame.setEnabled)
        QtCore.QObject.connect(self.applycal_ckbx, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.test_type_grp.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(CalibrationWidget)

    def retranslateUi(self, CalibrationWidget):
        CalibrationWidget.setWindowTitle(_translate("CalibrationWidget", "Form", None))
        self.savecal_ckbx.setText(_translate("CalibrationWidget", "Save calibration", None))
        self.applycal_ckbx.setText(_translate("CalibrationWidget", "Test calibration", None))
        self.label_2.setText(_translate("CalibrationWidget", "Reps", None))
        self.test_type_grp.setTitle(_translate("CalibrationWidget", "Test type", None))
        self.cal_type_cmbbx.setItemText(0, _translate("CalibrationWidget", "Tone Curve", None))

from spikeylab.stim.tceditor import TuningCurveEditor
