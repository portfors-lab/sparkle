from PyQt4 import QtGui, QtCore

class ComponentSelectionModel(QtGui.QItemSelectionModel):
    """Stores items in the selection model by object, not by position"""
    def __init__(self, model):
        QtGui.QItemSelectionModel.__init__(self, model)
        self._selected_components = []

    def select(self, index, command):
        component = self.model().data(index, QtCore.Qt.UserRole)
        if command == QtGui.QItemSelectionModel.Toggle:
            if component in self._selected_components:
                self._selected_components.remove(component)
                self.selectionChanged.emit(self.selection(), QtGui.QItemSelection(index, index))
            else:
                self._selected_components.append(component)
                self.selectionChanged.emit(self.selection(), QtGui.QItemSelection())

    def selectedIndexes(self):
        model = self.model()
        indexes = []
        for comp in self._selected_components:
            index = model.indexByComponent(comp)
            if index is None:
                # must have been removed from model, discard
                self._selected_components.remove(comp)
            else:
                indexes.append(index)
        return indexes

    def selection(self):
        sel = QtGui.QItemSelection()
        for index in self.selectedIndexes():
            sel.select(index, index)

        return sel

    def __str__(self):
        return "ComponentSelectionModel " + str(id(self))
