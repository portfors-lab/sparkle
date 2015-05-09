import os

from sparkle.QtWrapper import QtGui

thisfolder = os.path.dirname(os.path.realpath(__file__))

def noise():
    return QtGui.QImage(os.path.join(thisfolder,'noise.png'))

def default():
    return QtGui.QImage(os.path.join(thisfolder,'default.jpg'))
