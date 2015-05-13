import os

from sparkle.QtWrapper import QtGui

thisfolder = os.path.dirname(os.path.realpath(__file__))

def handEdit():
    icon = QtGui.QIcon(os.path.join(thisfolder,'hand_ibeam.png'))
    cursor = QtGui.QCursor(icon.pixmap(20,20))
    return cursor

def openHand():
    icon = QtGui.QIcon(os.path.join(thisfolder,'openhand.png'))
    cursor = QtGui.QCursor(icon.pixmap(16,16))
    return cursor

def pointyHand():
    icon = QtGui.QIcon(os.path.join(thisfolder,'pointyhand.png'))
    cursor = QtGui.QCursor(icon.pixmap(18,18))
    return cursor
