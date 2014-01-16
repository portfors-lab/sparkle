from PyQt4 import QtCore

from spikeylab.stim.selectionmodel import ComponentSelectionModel

class AutoParameterModel(QtCore.QAbstractTableModel):
    _paramid = 0
    def __init__(self, stimulus=None):
        super(AutoParameterModel, self).__init__()
        self._parameters = []
        self._stimview = None #this should be any view for StimulusModel
        self._stimmodel = stimulus
        self._selectionmap = {}
        self.headers = ['parameter', 'start', 'stop', 'step', 'nsteps']

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.headers[section]

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._parameters)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 5

    def data(self, index, role=QtCore.Qt.UserRole):
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            col = index.column()
            if col < 4:
                param = self._parameters[index.row()]
                item = param[self.headers[col]]            
            elif col == 4:
                item = '?'
            return item

        elif role == QtCore.Qt.UserRole:  #return the whole python object
            return self._parameters[index.row()]
        
    def allData(self):
        return self._parameters

    def setData(self, index, value, role=0):
        if role == QtCore.Qt.EditRole:
            param = self._parameters[index.row()]
            param[self.headers[index.column()]] = value
        else:
            row = index.row()
            if row == -1:
                row = self.rowCount() -1
            self._parameters[row] = value
        return True

    def setParameterList(self, paramlist):
        self._parameters = paramlist

    def insertRows(self, position, rows, parent = QtCore.QModelIndex()):
        if position == -1:
            position = self.rowCount()
        self.beginInsertRows(parent, position, position + rows - 1)
        for i in range(rows):
            defaultparam = { 'start': 0,
                             'step': 1,
                             'stop': 0,
                             'parameter': 'duration',
                             'paramid' : self._paramid,
                            }
            self._parameters.insert(position, defaultparam)
            self._selectionmap[self._paramid] = ComponentSelectionModel(self._stimmodel)
            self._paramid +=1

        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent = QtCore.QModelIndex()):
        self.beginRemoveRows(parent, position, position + rows - 1)
        for i in range(rows):
            p = self._parameters.pop(position)
            # cannot purge selection model, or else we have no way of 
            # recovering it when reordering
        self.endRemoveRows()
        return True

    def flags(self, index):
        if index.isValid():
            return QtCore.Qt.ItemIsDragEnabled | \
                   QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | \
                   QtCore.Qt.ItemIsEditable
        else:
            return QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled | \
                   QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | \
                   QtCore.Qt.ItemIsEditable

    def setStimView(self, stimview):
        self._stimview = stimview
        self.setStimModel(stimview.model())

    def stimView(self):
        return self._stimview

    def setStimModel(self, model):
        self._stimmodel = model

    def supportedDropActions(self):
        return QtCore.Qt.MoveAction

    def updateSelectionModel(self, index):
        if self._stimview is not None:
            param = self._parameters[index.row()]
            paramid = param['paramid']
            self._stimview.setSelectionModel(self._selectionmap[paramid])
            self._stimview.viewport().update()
    
    def parentModel(self):
        """The StimulusModel for which this model acts on"""
        return self._stimview.model()

    def selection(self, param):
        """
        Return the selected Indexes for the given parameter
        """
        selection_model = self._selectionmap[param['paramid']]
        return selection_model.selectedIndexes()