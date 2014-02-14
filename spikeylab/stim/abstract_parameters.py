from PyQt4 import QtGui, QtCore

from spikeylab.stim.abstract_editor import AbstractEditorWidget

class AbstractParameterWidget(AbstractEditorWidget):
    
    _component = None
    attributes_saved = QtCore.pyqtSignal(str, dict)
    
    def name(self):
        return self._component.name

    def setComponent(self, component):
        raise NotImplementedError

    def saveToObject(self):
        raise NotImplementedError

