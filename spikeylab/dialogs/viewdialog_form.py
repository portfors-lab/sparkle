# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\view_dlg.ui'
#
# Created: Tue Apr 08 15:58:13 2014
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

class Ui_ViewSettingsDialog(object):
    def setupUi(self, ViewSettingsDialog):
        ViewSettingsDialog.setObjectName(_fromUtf8("ViewSettingsDialog"))
        ViewSettingsDialog.resize(588, 580)
        self.verticalLayout = QtGui.QVBoxLayout(ViewSettingsDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tabWidget = QtGui.QTabWidget(ViewSettingsDialog)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.ui_tab = QtGui.QWidget()
        self.ui_tab.setObjectName(_fromUtf8("ui_tab"))
        self.label = QtGui.QLabel(self.ui_tab)
        self.label.setGeometry(QtCore.QRect(40, 40, 81, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.fontsz_spnbx = QtGui.QDoubleSpinBox(self.ui_tab)
        self.fontsz_spnbx.setGeometry(QtCore.QRect(130, 40, 62, 22))
        self.fontsz_spnbx.setObjectName(_fromUtf8("fontsz_spnbx"))
        self.tabWidget.addTab(self.ui_tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.tab_2)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.label_3 = QtGui.QLabel(self.tab_2)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout_3.addWidget(self.label_3)
        self.scrollArea = QtGui.QScrollArea(self.tab_2)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 544, 468))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.detail_widget = ComponentDetailSelector(self.scrollAreaWidgetContents)
        self.detail_widget.setObjectName(_fromUtf8("detail_widget"))
        self.verticalLayout_2.addWidget(self.detail_widget)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_3.addWidget(self.scrollArea)
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.verticalLayout.addWidget(self.tabWidget)
        self.buttonBox = QtGui.QDialogButtonBox(ViewSettingsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ViewSettingsDialog)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ViewSettingsDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ViewSettingsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ViewSettingsDialog)

    def retranslateUi(self, ViewSettingsDialog):
        ViewSettingsDialog.setWindowTitle(_translate("ViewSettingsDialog", "Dialog", None))
        self.label.setText(_translate("ViewSettingsDialog", "Font Size", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.ui_tab), _translate("ViewSettingsDialog", "Tab 1", None))
        self.label_3.setText(_translate("ViewSettingsDialog", "Attributes to show:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("ViewSettingsDialog", "Tab 2", None))

from spikeylab.stim.component_detail import ComponentDetailSelector
