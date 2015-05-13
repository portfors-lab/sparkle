from sparkle.QtWrapper import QtCore
from sparkle.gui.stim.abstract_editor import AbstractEditorWidget


class AbstractComponentWidget(AbstractEditorWidget):
    """Common functions for Component editors"""
    _component = None
    attributesSaved = QtCore.Signal(str, dict)
    def __init__(self, parent=None):
        super(AbstractComponentWidget, self).__init__(parent)
        # used to keep track of widget that are used to change component
        # parameters, primarily important for testing
        self.inputWidgets = {}

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
        :type component: (sublcass of) :class:`AbstractStimulusComponent<sparkle.stim.abstract_component.AbstractStimulusComponent>`
        """
        raise NotImplementedError

    def saveToObject(self):
        """Saves the values in the editor fields to the component
        object

        Must be implemented by subclass
        """
        raise NotImplementedError
