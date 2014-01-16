import os

from PyQt4 import QtGui, QtCore

class TrashWidget(QtGui.QPushButton):
    def __init__(self,parent=None):
        QtGui.QPushButton.__init__(self, parent)

        thisfolder = os.path.dirname(os.path.realpath(__file__))
        self.trash_icon = QtGui.QIcon(os.path.join(thisfolder,'trash.png'))
        self.setFlat(True)
        self.setIcon(self.trash_icon)
        self.setIconSize(QtCore.QSize(25,25))
        self.setAcceptDrops(True)

        self.under_mouse = False

    def dragEnterEvent(self, event):
        self.setFlat(False)
        event.accept()

    def dragLeaveEvent(self, event):
        self.setFlat(True)
        event.accept()

    def dragMoveEvent(self, event):
        event.accept()

    def leaveEvent(self, event):
        self.setFlat(True)
        event.accept()
