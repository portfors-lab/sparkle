from QtWrapper import QtCore

from spikeylab.gui.stim.abstract_editor import AbstractEditorWidget

class AbstractComponentWidget(AbstractEditorWidget):
    """Common functions for Component editors"""
    _component = None
    attributesSaved = QtCore.Signal(str, dict)
    
    def name(self):
        """Gets the component name

        :returns: str -- name of component
        """
        return self._component.name

    def component(self):
        """Gets the component for this editor

        :returns: AbstractStimulusComponent
        """
        return self._component

    def setComponent(self, component):
        """Sets the component for this editor, updates fields 
        appropriately.

        Must be implemented by subclass

        :param component: component this editor is acting on
        :type component: (sublcass of) :class:`AbstractStimulusComponent<spikeylab.stim.abstract_component.AbstractStimulusComponent>`
        """
        raise NotImplementedError

    def saveToObject(self):
        """Saves the values in the editor fields to the component
        object

        Must be implemented by subclass
        """
        raise NotImplementedError