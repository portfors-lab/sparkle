import os

from PyQt4 import QtGui

thisfolder = os.path.dirname(os.path.realpath(__file__))

def arrowup():
    return QtGui.QIcon(os.path.join(thisfolder,'arrowup.png'))

def arrowdown():
    return QtGui.QIcon(os.path.join(thisfolder,'arrowdown.png'))