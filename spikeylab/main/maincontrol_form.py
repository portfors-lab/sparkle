# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\main_control.ui'
#
# Created: Tue Apr 01 16:36:03 2014
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

class Ui_ControlWindow(object):
    def setupUi(self, ControlWindow):
        ControlWindow.setObjectName(_fromUtf8("ControlWindow"))
        ControlWindow.resize(1230, 743)
        self.centralwidget = QtGui.QWidget(ControlWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label_3 = QtGui.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_3.setFont(font)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_4.addWidget(self.label_3)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.running_label = QtGui.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.running_label.setFont(font)
        self.running_label.setObjectName(_fromUtf8("running_label"))
        self.horizontalLayout.addWidget(self.running_label)
        self.horizontalLayout_4.addLayout(self.horizontalLayout)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.tab_group = QtGui.QTabWidget(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.tab_group.setFont(font)
        self.tab_group.setObjectName(_fromUtf8("tab_group"))
        self.tab_explore = QtGui.QWidget()
        self.tab_explore.setObjectName(_fromUtf8("tab_explore"))
        self.horizontalLayout_7 = QtGui.QHBoxLayout(self.tab_explore)
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        self.verticalLayout_8 = QtGui.QVBoxLayout()
        self.verticalLayout_8.setObjectName(_fromUtf8("verticalLayout_8"))
        self.label_4 = QtGui.QLabel(self.tab_explore)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout_8.addWidget(self.label_4)
        self.listWidget_2 = QtGui.QListWidget(self.tab_explore)
        self.listWidget_2.setObjectName(_fromUtf8("listWidget_2"))
        item = QtGui.QListWidgetItem()
        self.listWidget_2.addItem(item)
        self.verticalLayout_8.addWidget(self.listWidget_2)
        self.gridLayout_6 = QtGui.QGridLayout()
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.label_20 = QtGui.QLabel(self.tab_explore)
        self.label_20.setObjectName(_fromUtf8("label_20"))
        self.gridLayout_6.addWidget(self.label_20, 0, 0, 1, 1)
        self.over_atten_lbl = QtGui.QLabel(self.tab_explore)
        self.over_atten_lbl.setObjectName(_fromUtf8("over_atten_lbl"))
        self.gridLayout_6.addWidget(self.over_atten_lbl, 0, 1, 1, 1)
        self.label_23 = QtGui.QLabel(self.tab_explore)
        self.label_23.setObjectName(_fromUtf8("label_23"))
        self.gridLayout_6.addWidget(self.label_23, 0, 2, 1, 1)
        self.verticalLayout_8.addLayout(self.gridLayout_6)
        self.horizontalLayout_7.addLayout(self.verticalLayout_8)
        self.verticalLayout_9 = QtGui.QVBoxLayout()
        self.verticalLayout_9.setObjectName(_fromUtf8("verticalLayout_9"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.explore_stim_type_cmbbx = QtGui.QComboBox(self.tab_explore)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.explore_stim_type_cmbbx.sizePolicy().hasHeightForWidth())
        self.explore_stim_type_cmbbx.setSizePolicy(sizePolicy)
        self.explore_stim_type_cmbbx.setObjectName(_fromUtf8("explore_stim_type_cmbbx"))
        self.horizontalLayout_3.addWidget(self.explore_stim_type_cmbbx)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.verticalLayout_9.addLayout(self.horizontalLayout_3)
        self.parameter_stack = DynamicStackedWidget(self.tab_explore)
        self.parameter_stack.setObjectName(_fromUtf8("parameter_stack"))
        self.verticalLayout_9.addWidget(self.parameter_stack)
        self.gridLayout_7 = QtGui.QGridLayout()
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.label_39 = QtGui.QLabel(self.tab_explore)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_39.setFont(font)
        self.label_39.setObjectName(_fromUtf8("label_39"))
        self.gridLayout_7.addWidget(self.label_39, 1, 0, 1, 1)
        self.ex_nreps_spnbx = QtGui.QSpinBox(self.tab_explore)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.ex_nreps_spnbx.setFont(font)
        self.ex_nreps_spnbx.setMinimum(1)
        self.ex_nreps_spnbx.setMaximum(100)
        self.ex_nreps_spnbx.setProperty("value", 5)
        self.ex_nreps_spnbx.setObjectName(_fromUtf8("ex_nreps_spnbx"))
        self.gridLayout_7.addWidget(self.ex_nreps_spnbx, 1, 1, 1, 1)
        self.funit_lbl = QtGui.QLabel(self.tab_explore)
        self.funit_lbl.setObjectName(_fromUtf8("funit_lbl"))
        self.gridLayout_7.addWidget(self.funit_lbl, 0, 2, 1, 1)
        self.save_explore_ckbx = QtGui.QCheckBox(self.tab_explore)
        self.save_explore_ckbx.setEnabled(False)
        self.save_explore_ckbx.setObjectName(_fromUtf8("save_explore_ckbx"))
        self.gridLayout_7.addWidget(self.save_explore_ckbx, 2, 0, 1, 2)
        self.label_6 = QtGui.QLabel(self.tab_explore)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_6.setFont(font)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_7.addWidget(self.label_6, 0, 0, 1, 1)
        self.aosr_spnbx = SmartSpinBox(self.tab_explore)
        self.aosr_spnbx.setEnabled(False)
        self.aosr_spnbx.setToolTip(_fromUtf8(""))
        self.aosr_spnbx.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.aosr_spnbx.setObjectName(_fromUtf8("aosr_spnbx"))
        self.gridLayout_7.addWidget(self.aosr_spnbx, 0, 1, 1, 1)
        self.verticalLayout_9.addLayout(self.gridLayout_7)
        self.horizontalLayout_7.addLayout(self.verticalLayout_9)
        self.tab_group.addTab(self.tab_explore, _fromUtf8(""))
        self.tab_protocol = QtGui.QWidget()
        self.tab_protocol.setObjectName(_fromUtf8("tab_protocol"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.tab_protocol)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_14 = QtGui.QLabel(self.tab_protocol)
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.gridLayout_2.addWidget(self.label_14, 0, 2, 1, 1)
        self.label_8 = QtGui.QLabel(self.tab_protocol)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout_2.addWidget(self.label_8, 0, 0, 1, 1)
        self.label_9 = QtGui.QLabel(self.tab_protocol)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridLayout_2.addWidget(self.label_9, 0, 1, 1, 1)
        self.trace_num = QtGui.QLabel(self.tab_protocol)
        self.trace_num.setObjectName(_fromUtf8("trace_num"))
        self.gridLayout_2.addWidget(self.trace_num, 1, 1, 1, 1)
        self.trace_type = QtGui.QLabel(self.tab_protocol)
        self.trace_type.setObjectName(_fromUtf8("trace_type"))
        self.gridLayout_2.addWidget(self.trace_type, 1, 3, 1, 1)
        self.label_15 = QtGui.QLabel(self.tab_protocol)
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.gridLayout_2.addWidget(self.label_15, 0, 3, 1, 1)
        self.test_num = QtGui.QLabel(self.tab_protocol)
        self.test_num.setObjectName(_fromUtf8("test_num"))
        self.gridLayout_2.addWidget(self.test_num, 1, 0, 1, 1)
        self.label_21 = QtGui.QLabel(self.tab_protocol)
        self.label_21.setObjectName(_fromUtf8("label_21"))
        self.gridLayout_2.addWidget(self.label_21, 2, 0, 1, 1)
        self.rep_num = QtGui.QLabel(self.tab_protocol)
        self.rep_num.setObjectName(_fromUtf8("rep_num"))
        self.gridLayout_2.addWidget(self.rep_num, 1, 2, 1, 1)
        self.trace_info = QtGui.QLabel(self.tab_protocol)
        self.trace_info.setObjectName(_fromUtf8("trace_info"))
        self.gridLayout_2.addWidget(self.trace_info, 3, 0, 1, 4)
        self.verticalLayout_5.addLayout(self.gridLayout_2)
        self.label_2 = QtGui.QLabel(self.tab_protocol)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_5.addWidget(self.label_2)
        self.protocolView = ProtocolView(self.tab_protocol)
        self.protocolView.setObjectName(_fromUtf8("protocolView"))
        self.verticalLayout_5.addWidget(self.protocolView)
        self.horizontalLayout_9 = QtGui.QHBoxLayout()
        self.horizontalLayout_9.setObjectName(_fromUtf8("horizontalLayout_9"))
        self.stimulus_choices = StimulusLabelTable(self.tab_protocol)
        self.stimulus_choices.setObjectName(_fromUtf8("stimulus_choices"))
        self.horizontalLayout_9.addWidget(self.stimulus_choices)
        self.pushButton = QtGui.QPushButton(self.tab_protocol)
        self.pushButton.setMaximumSize(QtCore.QSize(100, 16777215))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.horizontalLayout_9.addWidget(self.pushButton)
        self.verticalLayout_5.addLayout(self.horizontalLayout_9)
        self.tab_group.addTab(self.tab_protocol, _fromUtf8(""))
        self.tab_calibrate = QtGui.QWidget()
        self.tab_calibrate.setObjectName(_fromUtf8("tab_calibrate"))
        self.verticalLayout = QtGui.QVBoxLayout(self.tab_calibrate)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.calibration_widget = CalibrationWidget(self.tab_calibrate)
        self.calibration_widget.setObjectName(_fromUtf8("calibration_widget"))
        self.verticalLayout.addWidget(self.calibration_widget)
        self.tab_group.addTab(self.tab_calibrate, _fromUtf8(""))
        self.horizontalLayout_5.addWidget(self.tab_group)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.gridLayout_4 = QtGui.QGridLayout()
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
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
        self.label_29 = QtGui.QLabel(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_29.sizePolicy().hasHeightForWidth())
        self.label_29.setSizePolicy(sizePolicy)
        self.label_29.setObjectName(_fromUtf8("label_29"))
        self.gridLayout_4.addWidget(self.label_29, 0, 0, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_4)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.funit_lbl_2 = QtGui.QLabel(self.centralwidget)
        self.funit_lbl_2.setObjectName(_fromUtf8("funit_lbl_2"))
        self.gridLayout.addWidget(self.funit_lbl_2, 0, 2, 1, 1)
        self.label_10 = QtGui.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_10.setFont(font)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.gridLayout.addWidget(self.label_10, 2, 0, 1, 1)
        self.tunit_lbl = QtGui.QLabel(self.centralwidget)
        self.tunit_lbl.setObjectName(_fromUtf8("tunit_lbl"))
        self.gridLayout.addWidget(self.tunit_lbl, 2, 2, 1, 1)
        self.label_12 = QtGui.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_12.setFont(font)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.gridLayout.addWidget(self.label_12, 3, 0, 1, 1)
        self.label_13 = QtGui.QLabel(self.centralwidget)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.gridLayout.addWidget(self.label_13, 3, 2, 1, 1)
        self.label_43 = QtGui.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_43.setFont(font)
        self.label_43.setObjectName(_fromUtf8("label_43"))
        self.gridLayout.addWidget(self.label_43, 4, 0, 1, 1)
        self.tunit_lbl_2 = QtGui.QLabel(self.centralwidget)
        self.tunit_lbl_2.setObjectName(_fromUtf8("tunit_lbl_2"))
        self.gridLayout.addWidget(self.tunit_lbl_2, 4, 2, 1, 1)
        self.aisr_spnbx = SmartSpinBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.aisr_spnbx.setFont(font)
        self.aisr_spnbx.setDecimals(3)
        self.aisr_spnbx.setMaximum(500000.0)
        self.aisr_spnbx.setObjectName(_fromUtf8("aisr_spnbx"))
        self.gridLayout.addWidget(self.aisr_spnbx, 0, 1, 1, 1)
        self.binsz_spnbx = SmartSpinBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.binsz_spnbx.setFont(font)
        self.binsz_spnbx.setDecimals(3)
        self.binsz_spnbx.setMaximum(3000.0)
        self.binsz_spnbx.setObjectName(_fromUtf8("binsz_spnbx"))
        self.gridLayout.addWidget(self.binsz_spnbx, 4, 1, 1, 1)
        self.windowsz_spnbx = SmartSpinBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.windowsz_spnbx.setFont(font)
        self.windowsz_spnbx.setDecimals(3)
        self.windowsz_spnbx.setMaximum(3000.0)
        self.windowsz_spnbx.setObjectName(_fromUtf8("windowsz_spnbx"))
        self.gridLayout.addWidget(self.windowsz_spnbx, 2, 1, 1, 1)
        self.reprate_spnbx = QtGui.QDoubleSpinBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.reprate_spnbx.setFont(font)
        self.reprate_spnbx.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.reprate_spnbx.setPrefix(_fromUtf8(""))
        self.reprate_spnbx.setMinimum(0.1)
        self.reprate_spnbx.setMaximum(10.0)
        self.reprate_spnbx.setProperty("value", 0.5)
        self.reprate_spnbx.setObjectName(_fromUtf8("reprate_spnbx"))
        self.gridLayout.addWidget(self.reprate_spnbx, 5, 1, 1, 1)
        self.label_35 = QtGui.QLabel(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_35.sizePolicy().hasHeightForWidth())
        self.label_35.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_35.setFont(font)
        self.label_35.setObjectName(_fromUtf8("label_35"))
        self.gridLayout.addWidget(self.label_35, 5, 0, 1, 1)
        self.label_36 = QtGui.QLabel(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_36.sizePolicy().hasHeightForWidth())
        self.label_36.setSizePolicy(sizePolicy)
        self.label_36.setObjectName(_fromUtf8("label_36"))
        self.gridLayout.addWidget(self.label_36, 5, 2, 1, 1)
        self.thresh_spnbx = QtGui.QDoubleSpinBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.thresh_spnbx.setFont(font)
        self.thresh_spnbx.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.thresh_spnbx.setDecimals(3)
        self.thresh_spnbx.setMaximum(500.0)
        self.thresh_spnbx.setObjectName(_fromUtf8("thresh_spnbx"))
        self.gridLayout.addWidget(self.thresh_spnbx, 3, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.label_17 = QtGui.QLabel(self.centralwidget)
        self.label_17.setObjectName(_fromUtf8("label_17"))
        self.horizontalLayout_6.addWidget(self.label_17)
        self.mode_cmbx = QtGui.QComboBox(self.centralwidget)
        self.mode_cmbx.setObjectName(_fromUtf8("mode_cmbx"))
        self.mode_cmbx.addItem(_fromUtf8(""))
        self.mode_cmbx.addItem(_fromUtf8(""))
        self.horizontalLayout_6.addWidget(self.mode_cmbx)
        self.verticalLayout_2.addLayout(self.horizontalLayout_6)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem2)
        self.horizontalLayout_8 = QtGui.QHBoxLayout()
        self.horizontalLayout_8.setObjectName(_fromUtf8("horizontalLayout_8"))
        self.start_chart_btn = QtGui.QPushButton(self.centralwidget)
        self.start_chart_btn.setObjectName(_fromUtf8("start_chart_btn"))
        self.horizontalLayout_8.addWidget(self.start_chart_btn)
        self.stop_chart_btn = QtGui.QPushButton(self.centralwidget)
        self.stop_chart_btn.setObjectName(_fromUtf8("stop_chart_btn"))
        self.horizontalLayout_8.addWidget(self.stop_chart_btn)
        self.verticalLayout_2.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.start_btn = QtGui.QPushButton(self.centralwidget)
        self.start_btn.setObjectName(_fromUtf8("start_btn"))
        self.horizontalLayout_2.addWidget(self.start_btn)
        self.stop_btn = QtGui.QPushButton(self.centralwidget)
        self.stop_btn.setObjectName(_fromUtf8("stop_btn"))
        self.horizontalLayout_2.addWidget(self.stop_btn)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_5.addLayout(self.verticalLayout_2)
        self.verticalLayout_3.addLayout(self.horizontalLayout_5)
        ControlWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(ControlWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1230, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuOptions = QtGui.QMenu(self.menubar)
        self.menuOptions.setObjectName(_fromUtf8("menuOptions"))
        self.menuView = QtGui.QMenu(self.menubar)
        self.menuView.setObjectName(_fromUtf8("menuView"))
        ControlWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(ControlWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        ControlWindow.setStatusBar(self.statusbar)
        self.plot_dock = PlotDockWidget(ControlWindow)
        self.plot_dock.setObjectName(_fromUtf8("plot_dock"))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_4.setMargin(0)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.plot_dock.setWidget(self.dockWidgetContents)
        ControlWindow.addDockWidget(QtCore.Qt.DockWidgetArea(8), self.plot_dock)
        self.psth_dock = QtGui.QDockWidget(ControlWindow)
        self.psth_dock.setObjectName(_fromUtf8("psth_dock"))
        self.dockWidgetContents_2 = QtGui.QWidget()
        self.dockWidgetContents_2.setObjectName(_fromUtf8("dockWidgetContents_2"))
        self.verticalLayout_10 = QtGui.QVBoxLayout(self.dockWidgetContents_2)
        self.verticalLayout_10.setObjectName(_fromUtf8("verticalLayout_10"))
        self.psth_container = QtGui.QWidget(self.dockWidgetContents_2)
        self.psth_container.setObjectName(_fromUtf8("psth_container"))
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.psth_container)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setMargin(0)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.psth = PSTHWidget(self.psth_container)
        self.psth.setObjectName(_fromUtf8("psth"))
        self.verticalLayout_6.addWidget(self.psth)
        self.gridLayout_9 = QtGui.QGridLayout()
        self.gridLayout_9.setObjectName(_fromUtf8("gridLayout_9"))
        self.label_11 = QtGui.QLabel(self.psth_container)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_11.sizePolicy().hasHeightForWidth())
        self.label_11.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_11.setFont(font)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.gridLayout_9.addWidget(self.label_11, 0, 0, 1, 1)
        self.label_16 = QtGui.QLabel(self.psth_container)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_16.setFont(font)
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.gridLayout_9.addWidget(self.label_16, 0, 3, 1, 1)
        self.label_5 = QtGui.QLabel(self.psth_container)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_5.setFont(font)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_9.addWidget(self.label_5, 1, 0, 1, 1)
        self.spike_latency_lbl = QtGui.QLabel(self.psth_container)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.spike_latency_lbl.setFont(font)
        self.spike_latency_lbl.setObjectName(_fromUtf8("spike_latency_lbl"))
        self.gridLayout_9.addWidget(self.spike_latency_lbl, 1, 1, 1, 1)
        self.label_7 = QtGui.QLabel(self.psth_container)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_7.setFont(font)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout_9.addWidget(self.label_7, 1, 3, 1, 1)
        self.spike_rate_lbl = QtGui.QLabel(self.psth_container)
        self.spike_rate_lbl.setObjectName(_fromUtf8("spike_rate_lbl"))
        self.gridLayout_9.addWidget(self.spike_rate_lbl, 1, 4, 1, 1)
        self.spike_avg_lbl = QtGui.QLabel(self.psth_container)
        self.spike_avg_lbl.setObjectName(_fromUtf8("spike_avg_lbl"))
        self.gridLayout_9.addWidget(self.spike_avg_lbl, 0, 4, 1, 1)
        self.spike_total_lbl = QtGui.QLabel(self.psth_container)
        self.spike_total_lbl.setObjectName(_fromUtf8("spike_total_lbl"))
        self.gridLayout_9.addWidget(self.spike_total_lbl, 0, 1, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_9.addItem(spacerItem3, 0, 2, 1, 1)
        self.verticalLayout_6.addLayout(self.gridLayout_9)
        self.verticalLayout_10.addWidget(self.psth_container)
        self.psth_dock.setWidget(self.dockWidgetContents_2)
        ControlWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.psth_dock)
        self.progress_dock = QtGui.QDockWidget(ControlWindow)
        self.progress_dock.setObjectName(_fromUtf8("progress_dock"))
        self.dockWidgetContents_3 = QtGui.QWidget()
        self.dockWidgetContents_3.setObjectName(_fromUtf8("dockWidgetContents_3"))
        self.progress_dock.setWidget(self.dockWidgetContents_3)
        ControlWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.progress_dock)
        self.log_dock = QtGui.QDockWidget(ControlWindow)
        self.log_dock.setObjectName(_fromUtf8("log_dock"))
        self.dockWidgetContents_4 = QtGui.QWidget()
        self.dockWidgetContents_4.setObjectName(_fromUtf8("dockWidgetContents_4"))
        self.verticalLayout_7 = QtGui.QVBoxLayout(self.dockWidgetContents_4)
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.log_txedt = QtGui.QPlainTextEdit(self.dockWidgetContents_4)
        self.log_txedt.setReadOnly(True)
        self.log_txedt.setObjectName(_fromUtf8("log_txedt"))
        self.verticalLayout_7.addWidget(self.log_txedt)
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.dblevel_lbl = QtGui.QLabel(self.dockWidgetContents_4)
        self.dblevel_lbl.setObjectName(_fromUtf8("dblevel_lbl"))
        self.gridLayout_3.addWidget(self.dblevel_lbl, 0, 1, 1, 1)
        self.label_18 = QtGui.QLabel(self.dockWidgetContents_4)
        self.label_18.setObjectName(_fromUtf8("label_18"))
        self.gridLayout_3.addWidget(self.label_18, 0, 0, 1, 1)
        self.dblevel_lbl2 = QtGui.QLabel(self.dockWidgetContents_4)
        self.dblevel_lbl2.setObjectName(_fromUtf8("dblevel_lbl2"))
        self.gridLayout_3.addWidget(self.dblevel_lbl2, 1, 1, 1, 1)
        self.dblevel_lbl3 = QtGui.QLabel(self.dockWidgetContents_4)
        self.dblevel_lbl3.setObjectName(_fromUtf8("dblevel_lbl3"))
        self.gridLayout_3.addWidget(self.dblevel_lbl3, 2, 1, 1, 1)
        self.label_19 = QtGui.QLabel(self.dockWidgetContents_4)
        self.label_19.setObjectName(_fromUtf8("label_19"))
        self.gridLayout_3.addWidget(self.label_19, 2, 0, 1, 1)
        self.verticalLayout_7.addLayout(self.gridLayout_3)
        self.log_dock.setWidget(self.dockWidgetContents_4)
        ControlWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.log_dock)
        self.actionSave_Options = QtGui.QAction(ControlWindow)
        self.actionSave_Options.setObjectName(_fromUtf8("actionSave_Options"))
        self.actionSet_Calibration = QtGui.QAction(ControlWindow)
        self.actionSet_Calibration.setObjectName(_fromUtf8("actionSet_Calibration"))
        self.actionSet_Scale = QtGui.QAction(ControlWindow)
        self.actionSet_Scale.setObjectName(_fromUtf8("actionSet_Scale"))
        self.actionShow_Data_display = QtGui.QAction(ControlWindow)
        self.actionShow_Data_display.setObjectName(_fromUtf8("actionShow_Data_display"))
        self.actionShow_PSTH = QtGui.QAction(ControlWindow)
        self.actionShow_PSTH.setObjectName(_fromUtf8("actionShow_PSTH"))
        self.actionSpectrogram_Parameters = QtGui.QAction(ControlWindow)
        self.actionSpectrogram_Parameters.setObjectName(_fromUtf8("actionSpectrogram_Parameters"))
        self.actionShow_Progress = QtGui.QAction(ControlWindow)
        self.actionShow_Progress.setObjectName(_fromUtf8("actionShow_Progress"))
        self.actionShow_Log = QtGui.QAction(ControlWindow)
        self.actionShow_Log.setObjectName(_fromUtf8("actionShow_Log"))
        self.menuOptions.addAction(self.actionSave_Options)
        self.menuOptions.addAction(self.actionSet_Calibration)
        self.menuOptions.addAction(self.actionSet_Scale)
        self.menuOptions.addAction(self.actionSpectrogram_Parameters)
        self.menuView.addAction(self.actionShow_Data_display)
        self.menuView.addAction(self.actionShow_PSTH)
        self.menuView.addAction(self.actionShow_Progress)
        self.menuView.addAction(self.actionShow_Log)
        self.menubar.addAction(self.menuOptions.menuAction())
        self.menubar.addAction(self.menuView.menuAction())

        self.retranslateUi(ControlWindow)
        self.tab_group.setCurrentIndex(1)
        self.parameter_stack.setCurrentIndex(-1)
        QtCore.QObject.connect(self.actionSave_Options, QtCore.SIGNAL(_fromUtf8("triggered()")), ControlWindow.launch_save_dlg)
        QtCore.QObject.connect(self.actionSet_Calibration, QtCore.SIGNAL(_fromUtf8("triggered()")), ControlWindow.launch_calibration_dlg)
        QtCore.QObject.connect(self.actionSet_Scale, QtCore.SIGNAL(_fromUtf8("triggered()")), ControlWindow.launch_scale_dlg)
        QtCore.QObject.connect(self.actionShow_Data_display, QtCore.SIGNAL(_fromUtf8("triggered()")), ControlWindow.show_display)
        QtCore.QObject.connect(self.actionShow_PSTH, QtCore.SIGNAL(_fromUtf8("triggered()")), ControlWindow.show_psth)
        QtCore.QObject.connect(self.explore_stim_type_cmbbx, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.parameter_stack.setCurrentIndex)
        QtCore.QObject.connect(self.actionSpectrogram_Parameters, QtCore.SIGNAL(_fromUtf8("triggered()")), ControlWindow.launch_specgram_dlg)
        QtCore.QObject.connect(self.mode_cmbx, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(QString)")), ControlWindow.mode_toggled)
        QtCore.QObject.connect(self.actionShow_Progress, QtCore.SIGNAL(_fromUtf8("triggered()")), ControlWindow.show_progress)
        QtCore.QObject.connect(self.tab_group, QtCore.SIGNAL(_fromUtf8("currentChanged(int)")), ControlWindow.tab_changed)
        QtCore.QObject.connect(self.actionShow_Log, QtCore.SIGNAL(_fromUtf8("triggered()")), ControlWindow.show_log)
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), ControlWindow.clear_protocol)
        QtCore.QMetaObject.connectSlotsByName(ControlWindow)

    def retranslateUi(self, ControlWindow):
        ControlWindow.setWindowTitle(_translate("ControlWindow", "MainWindow", None))
        self.label_3.setText(_translate("ControlWindow", "SSHF", None))
        self.running_label.setText(_translate("ControlWindow", "OFF", None))
        self.label_4.setText(_translate("ControlWindow", "History:", None))
        __sortingEnabled = self.listWidget_2.isSortingEnabled()
        self.listWidget_2.setSortingEnabled(False)
        item = self.listWidget_2.item(0)
        item.setText(_translate("ControlWindow", "Coming soon", None))
        self.listWidget_2.setSortingEnabled(__sortingEnabled)
        self.label_20.setText(_translate("ControlWindow", "Undesired Attenuation:", None))
        self.over_atten_lbl.setText(_translate("ControlWindow", "0", None))
        self.label_23.setText(_translate("ControlWindow", "dB", None))
        self.label_39.setText(_translate("ControlWindow", "Reps", None))
        self.funit_lbl.setText(_translate("ControlWindow", "kHz", None))
        self.save_explore_ckbx.setText(_translate("ControlWindow", "Save Explore Recording", None))
        self.label_6.setText(_translate("ControlWindow", "Gen. Sample rate", None))
        self.tab_group.setTabText(self.tab_group.indexOf(self.tab_explore), _translate("ControlWindow", "Explore", None))
        self.label_14.setText(_translate("ControlWindow", "Rep:", None))
        self.label_8.setText(_translate("ControlWindow", "Test:", None))
        self.label_9.setText(_translate("ControlWindow", "Trace:", None))
        self.trace_num.setText(_translate("ControlWindow", "0", None))
        self.trace_type.setText(_translate("ControlWindow", "None", None))
        self.label_15.setText(_translate("ControlWindow", "Type:", None))
        self.test_num.setText(_translate("ControlWindow", "0", None))
        self.label_21.setText(_translate("ControlWindow", "Details:", None))
        self.rep_num.setText(_translate("ControlWindow", "0", None))
        self.trace_info.setText(_translate("ControlWindow", "Super cool info", None))
        self.label_2.setText(_translate("ControlWindow", "Experiment Protocol:", None))
        self.pushButton.setText(_translate("ControlWindow", "clear protocol", None))
        self.tab_group.setTabText(self.tab_group.indexOf(self.tab_protocol), _translate("ControlWindow", "Experiment", None))
        self.tab_group.setTabText(self.tab_group.indexOf(self.tab_calibrate), _translate("ControlWindow", "Calibration", None))
        self.label_30.setText(_translate("ControlWindow", "AI channel", None))
        self.label_29.setText(_translate("ControlWindow", "Stim channel", None))
        self.label.setText(_translate("ControlWindow", "Acq. Sample rate", None))
        self.funit_lbl_2.setText(_translate("ControlWindow", "kHz", None))
        self.label_10.setText(_translate("ControlWindow", "Window size", None))
        self.tunit_lbl.setText(_translate("ControlWindow", "ms", None))
        self.label_12.setText(_translate("ControlWindow", "Threshold", None))
        self.label_13.setText(_translate("ControlWindow", "mV", None))
        self.label_43.setText(_translate("ControlWindow", "Spike bin size", None))
        self.tunit_lbl_2.setText(_translate("ControlWindow", "ms", None))
        self.label_35.setText(_translate("ControlWindow", "Rep rate", None))
        self.label_36.setText(_translate("ControlWindow", "reps/s", None))
        self.label_17.setText(_translate("ControlWindow", "Mode", None))
        self.mode_cmbx.setItemText(0, _translate("ControlWindow", "Windowed", None))
        self.mode_cmbx.setItemText(1, _translate("ControlWindow", "Chart", None))
        self.start_chart_btn.setText(_translate("ControlWindow", "Start Chart", None))
        self.stop_chart_btn.setText(_translate("ControlWindow", "Stop Chart", None))
        self.start_btn.setText(_translate("ControlWindow", "Start", None))
        self.stop_btn.setText(_translate("ControlWindow", "Abort", None))
        self.menuOptions.setTitle(_translate("ControlWindow", "Options", None))
        self.menuView.setTitle(_translate("ControlWindow", "View", None))
        self.plot_dock.setWindowTitle(_translate("ControlWindow", "Data Display", None))
        self.psth_dock.setWindowTitle(_translate("ControlWindow", "PSTH", None))
        self.label_11.setToolTip(_translate("ControlWindow", "Total no. of spikes over repetitions", None))
        self.label_11.setText(_translate("ControlWindow", "Total :", None))
        self.label_16.setToolTip(_translate("ControlWindow", "Mean no. of spikes per unique stimulus", None))
        self.label_16.setText(_translate("ControlWindow", "Average :", None))
        self.label_5.setToolTip(_translate("ControlWindow", "Mean time of first spike", None))
        self.label_5.setText(_translate("ControlWindow", "Latency (ms) :", None))
        self.spike_latency_lbl.setText(_translate("ControlWindow", "0", None))
        self.label_7.setToolTip(_translate("ControlWindow", "Mean no. spikes per window", None))
        self.label_7.setText(_translate("ControlWindow", "Rate :", None))
        self.spike_rate_lbl.setText(_translate("ControlWindow", "0", None))
        self.spike_avg_lbl.setText(_translate("ControlWindow", "0", None))
        self.spike_total_lbl.setText(_translate("ControlWindow", "0", None))
        self.progress_dock.setWindowTitle(_translate("ControlWindow", "Progress", None))
        self.log_dock.setWindowTitle(_translate("ControlWindow", "Log", None))
        self.dblevel_lbl.setText(_translate("ControlWindow", "0", None))
        self.label_18.setText(_translate("ControlWindow", "dB SPL level:", None))
        self.dblevel_lbl2.setText(_translate("ControlWindow", "0", None))
        self.dblevel_lbl3.setText(_translate("ControlWindow", "0", None))
        self.label_19.setText(_translate("ControlWindow", "FFT peak", None))
        self.actionSave_Options.setText(_translate("ControlWindow", "Save Options...", None))
        self.actionSet_Calibration.setText(_translate("ControlWindow", "Set Calibration...", None))
        self.actionSet_Scale.setText(_translate("ControlWindow", "Set Scale...", None))
        self.actionShow_Data_display.setText(_translate("ControlWindow", "Show Data Display", None))
        self.actionShow_PSTH.setText(_translate("ControlWindow", "Show PSTH", None))
        self.actionSpectrogram_Parameters.setText(_translate("ControlWindow", "Spectrogram Parameters...", None))
        self.actionShow_Progress.setText(_translate("ControlWindow", "Show Progress", None))
        self.actionShow_Log.setText(_translate("ControlWindow", "Show Log", None))

from spikeylab.stim.dynamic_stacker import DynamicStackedWidget
from spikeylab.stim.smart_spinbox import SmartSpinBox
from spikeylab.calibration.calibration_widget import CalibrationWidget
from spikeylab.plotting.pyqtgraph_widgets import PSTHWidget
from spikeylab.main.protocol_model import ProtocolView
from spikeylab.main.plotdock import PlotDockWidget
from spikeylab.stim.stimulus_label import StimulusLabelTable
