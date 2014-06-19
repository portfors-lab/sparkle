from PyQt4 import QtGui, QtCore

from spikeylab.stim.abstract_editor import AbstractEditorWidget

class AbstractParameterWidget(AbstractEditorWidget):
    
    _component = None
    attributesSaved = QtCore.pyqtSignal(str, dict)
    
    def name(self):
        return self._component.name

    def component(self):
        return self._component

    def setComponent(self, component):
        raise NotImplementedError

    def saveToObject(self):
        raise NotImplementedError