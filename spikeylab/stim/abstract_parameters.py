from PyQt4 import QtGui

from spikeylab.stim.abstract_editor import AbstractEditorWidget

class AbstractParameterWidget(AbstractEditorWidget):
    
    _component = None
    
    def name(self):
        return self._component.name

    def setComponent(self, component):
        raise NotImplementedError

    def saveToObject(self):
        raise NotImplementedError

