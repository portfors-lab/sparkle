# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'calibration_widget.ui'
#
# Created: Fri Dec  5 14:44:26 2014
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

from sparkle.gui.stim.tuning_curve import TuningCurveEditor

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
        self.savecalCkbx = QtGui.QRadioButton(self.calgroup)
        self.savecalCkbx.setChecked(True)
        self.savecalCkbx.setObjectName(_fromUtf8("savecalCkbx"))
        self.horizontalLayout_4.addWidget(self.savecalCkbx)
        self.applycalCkbx = QtGui.QRadioButton(self.calgroup)
        self.applycalCkbx.setObjectName(_fromUtf8("applycalCkbx"))
        self.horizontalLayout_4.addWidget(self.applycalCkbx)
        self.label_2 = QtGui.QLabel(self.calgroup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_4.addWidget(self.label_2)
        self.nrepsSpnbx = QtGui.QSpinBox(self.calgroup)
        self.nrepsSpnbx.setMaximumSize(QtCore.QSize(100, 16777215))
        self.nrepsSpnbx.setMaximum(1000)
        self.nrepsSpnbx.setProperty("value", 1)
        self.nrepsSpnbx.setObjectName(_fromUtf8("nrepsSpnbx"))
        self.horizontalLayout_4.addWidget(self.nrepsSpnbx)
        self.verticalLayout.addWidget(self.calgroup)
        self.frame = QtGui.QFrame(CalibrationWidget)
        self.frame.setEnabled(False)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.testTypeGrp = QtGui.QGroupBox(self.frame)
        self.testTypeGrp.setEnabled(False)
        self.testTypeGrp.setObjectName(_fromUtf8("testTypeGrp"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.testTypeGrp)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.calTypeCmbbx = QtGui.QComboBox(self.testTypeGrp)
        self.calTypeCmbbx.setObjectName(_fromUtf8("calTypeCmbbx"))
        self.calTypeCmbbx.addItem(_fromUtf8(""))
        self.horizontalLayout.addWidget(self.calTypeCmbbx)
        self.verticalLayout_2.addWidget(self.testTypeGrp)
        self.caleditorStack = QtGui.QStackedWidget(self.frame)
        self.caleditorStack.setObjectName(_fromUtf8("caleditorStack"))
        self.page = QtGui.QWidget()
        self.page.setObjectName(_fromUtf8("page"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.page)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.curveWidget = TuningCurveEditor(self.page)
        self.curveWidget.setObjectName(_fromUtf8("curveWidget"))
        self.verticalLayout_3.addWidget(self.curveWidget)
        self.caleditorStack.addWidget(self.page)
        self.verticalLayout_2.addWidget(self.caleditorStack)
        self.verticalLayout.addWidget(self.frame)

        self.retranslateUi(CalibrationWidget)
        self.caleditorStack.setCurrentIndex(0)
        QtCore.QObject.connect(self.calTypeCmbbx, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.caleditorStack.setCurrentIndex)
        QtCore.QObject.connect(self.applycalCkbx, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.frame.setEnabled)
        QtCore.QObject.connect(self.applycalCkbx, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.testTypeGrp.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(CalibrationWidget)

    def retranslateUi(self, CalibrationWidget):
        CalibrationWidget.setWindowTitle(_translate("CalibrationWidget", "Form", None))
        self.savecalCkbx.setToolTip(_translate("CalibrationWidget", "Saves calibration data to file and sets as current calibration", None))
        self.savecalCkbx.setText(_translate("CalibrationWidget", "Save calibration", None))
        self.applycalCkbx.setToolTip(_translate("CalibrationWidget", "Play stimulus with calibration applied; does not save to file", None))
        self.applycalCkbx.setText(_translate("CalibrationWidget", "Test calibration", None))
        self.label_2.setText(_translate("CalibrationWidget", "Reps", None))
        self.nrepsSpnbx.setToolTip(_translate("CalibrationWidget", "Number of repeats for the stimulus", None))
        self.testTypeGrp.setTitle(_translate("CalibrationWidget", "Test type", None))
        self.calTypeCmbbx.setToolTip(_translate("CalibrationWidget", "Stimulus type", None))
        self.calTypeCmbbx.setItemText(0, _translate("CalibrationWidget", "Tone Curve", None))
