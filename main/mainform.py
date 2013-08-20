# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\main_choices.ui'
#
# Created: Mon Aug 19 17:15:27 2013
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

class Ui_ChoicesWindow(object):
    def setupUi(self, ChoicesWindow):
        ChoicesWindow.setObjectName(_fromUtf8("ChoicesWindow"))
        ChoicesWindow.resize(307, 240)
        self.centralwidget = QtGui.QWidget(ChoicesWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.explore_btn = QtGui.QPushButton(self.centralwidget)
        self.explore_btn.setObjectName(_fromUtf8("explore_btn"))
        self.verticalLayout.addWidget(self.explore_btn)
        self.curve_btn = QtGui.QPushButton(self.centralwidget)
        self.curve_btn.setObjectName(_fromUtf8("curve_btn"))
        self.verticalLayout.addWidget(self.curve_btn)
        self.chart_btn = QtGui.QPushButton(self.centralwidget)
        self.chart_btn.setObjectName(_fromUtf8("chart_btn"))
        self.verticalLayout.addWidget(self.chart_btn)
        self.experiment_btn = QtGui.QPushButton(self.centralwidget)
        self.experiment_btn.setObjectName(_fromUtf8("experiment_btn"))
        self.verticalLayout.addWidget(self.experiment_btn)
        self.gridLayout_4 = QtGui.QGridLayout()
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.label_29 = QtGui.QLabel(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_29.sizePolicy().hasHeightForWidth())
        self.label_29.setSizePolicy(sizePolicy)
        self.label_29.setObjectName(_fromUtf8("label_29"))
        self.gridLayout_4.addWidget(self.label_29, 0, 0, 1, 1)
        self.aochan_box = QtGui.QComboBox(self.centralwidget)
        self.aochan_box.setObjectName(_fromUtf8("aochan_box"))
        self.gridLayout_4.addWidget(self.aochan_box, 0, 1, 1, 1)
        self.label_30 = QtGui.QLabel(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_30.sizePolicy().hasHeightForWidth())
        self.label_30.setSizePolicy(sizePolicy)
        self.label_30.setObjectName(_fromUtf8("label_30"))
        self.gridLayout_4.addWidget(self.label_30, 1, 0, 1, 1)
        self.aichan_box = QtGui.QComboBox(self.centralwidget)
        self.aichan_box.setObjectName(_fromUtf8("aichan_box"))
        self.gridLayout_4.addWidget(self.aichan_box, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_4)
        self.info_label = QtGui.QLabel(self.centralwidget)
        self.info_label.setObjectName(_fromUtf8("info_label"))
        self.verticalLayout.addWidget(self.info_label)
        ChoicesWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(ChoicesWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 307, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuOptions = QtGui.QMenu(self.menubar)
        self.menuOptions.setObjectName(_fromUtf8("menuOptions"))
        ChoicesWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(ChoicesWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        ChoicesWindow.setStatusBar(self.statusbar)
        self.actionSet_Calibration = QtGui.QAction(ChoicesWindow)
        self.actionSet_Calibration.setObjectName(_fromUtf8("actionSet_Calibration"))
        self.menuOptions.addAction(self.actionSet_Calibration)
        self.menubar.addAction(self.menuOptions.menuAction())

        self.retranslateUi(ChoicesWindow)
        QtCore.QObject.connect(self.actionSet_Calibration, QtCore.SIGNAL(_fromUtf8("triggered()")), ChoicesWindow.launch_calibration_dlg)
        QtCore.QMetaObject.connectSlotsByName(ChoicesWindow)

    def retranslateUi(self, ChoicesWindow):
        ChoicesWindow.setWindowTitle(_translate("ChoicesWindow", "MainWindow", None))
        self.explore_btn.setText(_translate("ChoicesWindow", "Explore", None))
        self.curve_btn.setText(_translate("ChoicesWindow", "Tuning Curve", None))
        self.chart_btn.setText(_translate("ChoicesWindow", "Chart", None))
        self.experiment_btn.setText(_translate("ChoicesWindow", "Experimental", None))
        self.label_29.setText(_translate("ChoicesWindow", "Stim channel", None))
        self.label_30.setText(_translate("ChoicesWindow", "AI channel", None))
        self.info_label.setText(_translate("ChoicesWindow", "Now Playing:", None))
        self.menuOptions.setTitle(_translate("ChoicesWindow", "Options", None))
        self.actionSet_Calibration.setText(_translate("ChoicesWindow", "Set Calibration...", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ChoicesWindow = QtGui.QMainWindow()
    ui = Ui_ChoicesWindow()
    ui.setupUi(ChoicesWindow)
    ChoicesWindow.show()
    sys.exit(app.exec_())

