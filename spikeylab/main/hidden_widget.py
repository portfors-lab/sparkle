from PyQt4 import QtCore, QtGui
from spikeylab.resources.icons import arrowup, arrowdown

class WidgetHider(QtGui.QWidget):   
    def __init__(self, content, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.title = QtGui.QLabel(content.windowTitle())
        self.hide_icon = arrowdown()
        self.show_icon = arrowup()
        self.hide_btn = QtGui.QPushButton('',self)
        self.hide_btn.setIcon(self.show_icon)
        self.hide_btn.setFlat(True)
        self.hide_btn.clicked.connect(self.hide)
        titlebar_layout = QtGui.QHBoxLayout()
        titlebar_layout.setSpacing(0)
        titlebar_layout.setContentsMargins(0,0,0,0)
        titlebar_layout.addWidget(self.title)
        titlebar_layout.addWidget(self.hide_btn)
        titlebar_layout.addStretch(1)

        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)

        layout.addLayout(titlebar_layout)
        layout.addWidget(content)

        self.content = content
        content.hide()
        self.setFixedHeight(30)

        self.setLayout(layout)

    def hide(self, event):
        if self.content.isHidden():
            self.content.show()
            self.hide_btn.setIcon(self.hide_icon)
            self.setMaximumHeight(16777215)
        else:
            self.content.hide()
            self.hide_btn.setIcon(self.show_icon)
            self.setFixedHeight(30)
