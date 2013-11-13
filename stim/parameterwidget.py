from PyQt4 import QtGui

from common_parametersform import Ui_ParameterWidget

class ParameterWidget(QtGui.QWidget):
    """ Widget that accepts input for parameters that all stimuli
     types have in common"""
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_ParameterWidget()
        self.ui.setupUi(self)

    def testMethod(self):
        print 'Just adding a method to our QLabel'
