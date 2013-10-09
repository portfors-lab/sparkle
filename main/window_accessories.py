import os
from PyQt4 import QtGui, QtCore

class MaximizableTitleBar(QtGui.QWidget):
    """ Title bar widget to be used with QDockWidget. Adds maximize
        functionality for floating widget """
    def __init__(self, parent):
        QtGui.QWidget.__init__(self,parent)
        thisfolder = os.path.dirname(os.path.realpath(__file__))
        self.parent = parent
        self.float_icon = QtGui.QIcon.fromTheme('view-fullscreen', QtGui.QIcon(os.path.join(thisfolder,'float_window.png')))
        self.close_icon = QtGui.QIcon.fromTheme('window-close', QtGui.QIcon(os.path.join(thisfolder,'close_window.png')))
        self.restore_icon = QtGui.QIcon(os.path.join(thisfolder,'restore_window.png'))
        self.maximize_icon = QtGui.QIcon(os.path.join(thisfolder,'maximize_window.png'))

        adjust_button = QtGui.QPushButton('',self)
        adjust_button.setIcon(self.float_icon)
        adjust_button.setFlat(True)
        adjust_button.setIconSize(QtCore.QSize(12,12))
        adjust_button.clicked.connect(self.on_adjust)
        close_button = QtGui.QPushButton('',self)
        close_button.setIcon(self.close_icon)
        close_button.setFlat(True)
        close_button.setIconSize(QtCore.QSize(12,12))
        close_button.clicked.connect(self.on_close)

        self.parent.topLevelChanged.connect(self.topLevelChange)

        layout = QtGui.QHBoxLayout()

        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        layout.addStretch(1)
        layout.addWidget(adjust_button)
        layout.addWidget(close_button)
        self.setLayout(layout)
        self.maximized = False
        self.adjust_button = adjust_button


    def on_adjust(self):
        if self.parent.isFloating():
            if self.maximized:
                self.parent.showNormal()
                self.adjust_button.setIcon(self.maximize_icon)
                self.maximized = False
            else:
                self.parent.showMaximized()
                self.adjust_button.setIcon(self.restore_icon)
                self.maximized = True
        else:
            self.parent.setFloating(True)
            # QtGui.QApplication.processEvents()

    def on_close(self):
        self.parent.close()

    def topLevelChange(self, isfloating):
        if isfloating:
            self.adjust_button.setIcon(self.maximize_icon)
        else:
            self.adjust_button.setIcon(self.float_icon)