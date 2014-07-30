from PyQt4 import QtGui, QtDesigner

from spikeylab.gui.stim.incrementer import IncrementInput

class IncrementInputPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin):
    def __init__(self, parent=None):
        QtDesigner.QPyDesignerCustomWidgetPlugin.__init__(self)
 
    def name(self):
        return 'IncrementInput'
 
    def group(self):
        return 'bass-assery'
 
    def icon(self):
        return QtGui.QIcon()
 
    def isContainer(self):
        return False
 
    def includeFile(self):
        return 'incrementer'
 
    def toolTip(self):
        return 'Arnold Facepalmer'
 
    def whatsThis(self):
        return 'Facepalm all day'
 
    def createWidget(self, parent):
        return IncrementInput(parent)


if __name__ == '__main__':
    """Run this to check for syntax and other silly mistakes that will
    stop the plugin from loading"""
    import sys
    app = QtGui.QApplication(sys.argv)
    widget = IncrementInput()
    widget.show()
    sys.exit(app.exec_())