from sparkle.QtWrapper import QtCore, QtGui


class ComponentSelectionModel(QtGui.QItemSelectionModel):
    """Stores items in the selection model by object, not by position"""
    hintRequested = QtCore.Signal(str)
    def __init__(self, model):
        super(ComponentSelectionModel, self).__init__(model)
        self._selectedComponents = []

    def select(self, index, command=QtGui.QItemSelectionModel.Toggle):
        """Changes the inclusion of the given *index* in the selection model"""
        component = self.model().data(index, QtCore.Qt.UserRole)
        self.selectComponent(component, index)

    def selectComponent(self, component, index=None, command=QtGui.QItemSelectionModel.Toggle):
        """Selects the given *component* according to *command* policy
        (actually, only toggle supported). If index is None, looks up index
        of component in model"""
        if command == QtGui.QItemSelectionModel.Toggle:
            if component in self._selectedComponents:
                self._selectedComponents.remove(component)
                if index is None:
                    index = self.model().indexByComponent(component)
                self.selectionChanged.emit(self.selection(), QtGui.QItemSelection(index, index))
                if len(self._selectedComponents) == 0:
                    self.hintRequested.emit('Select Components in view to modify')
            else:
                self._selectedComponents.append(component)
                self.selectionChanged.emit(self.selection(), QtGui.QItemSelection())
                self.hintRequested.emit('Select more components, or click again to toggle inclusion. To edit parameter type or bounds, select parameter field in table')
        else:
            raise Exception("Selection command not supported")

    def selectedIndexes(self):
        """Returns a list of QModelIndex currently in the model"""
        model = self.model()
        indexes = []
        for comp in self._selectedComponents:
            index = model.indexByComponent(comp)
            if index is None:
                # must have been removed from model, discard
                self._selectedComponents.remove(comp)
            else:
                indexes.append(index)
        return indexes

    def selection(self):
        """Returns items in selection as a QItemSelection object"""
        sel = QtGui.QItemSelection()
        for index in self.selectedIndexes():
            sel.select(index, index)
        return sel

    def selectionComponents(self):
        """Returns the names of the component types in this selection"""
        comps = []
        model = self.model()
        for comp in self._selectedComponents:
            index = model.indexByComponent(comp)
            if index is not None:
                comps.append(comp)
        return comps

    def __str__(self):
        return "ComponentSelectionModel " + str(id(self))
