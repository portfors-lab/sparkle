from PyQt4 import QtCore, QtGui

import numpy as np

from spikeylab.stim.selectionmodel import ComponentSelectionModel
from spikeylab.main.abstract_drag_view import AbstractDragView

ERRCELL = QtGui.QColor('firebrick')

class AutoParameterModel(QtCore.QAbstractTableModel):
    SelectionModelRole = 34
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
            param = self._parameters[index.row()]
            if col == 0:
                item = param[self.headers[col]]            
            if 0 < col < 4:
                item = param[self.headers[col]]
                # scale appropriately
                multiplier = self.getDetail(index, 'multiplier')
                if multiplier is not None:
                    return item/multiplier
            elif col == 4:
                if param['start'] > param['stop'] and param['step'] > 0:
                    step = -1*param['step']
                else:
                    step = param['step']
                item = len(np.arange(param['start'], param['stop'], step))
            return item
        elif role == QtCore.Qt.ToolTipRole:
            if 1 <= index.column() <= 3:
                label = self.getDetail(index, 'label')
                return label
        elif role == QtCore.Qt.BackgroundRole:
            # color the background red for bad values
            col = index.column()
            param = self._parameters[index.row()]
            if param['parameter'] == '':
                return None
            if col == 1:
                # I don't want to do this every time maybe...
                ok = self.checkLimits(param['start'], param)
                if not ok:
                    return QtGui.QBrush(ERRCELL)
            if col == 2:
                ok = self.checkLimits(param['stop'], param)
                if not ok:
                    return QtGui.QBrush(ERRCELL)
            if col == 4:
                nsteps = self.data(index, role=QtCore.Qt.DisplayRole)
                if nsteps == 0 :
                    return QtGui.QBrush(ERRCELL)

        elif role == QtCore.Qt.UserRole or role == AbstractDragView.DragRole:  #return the whole python object
            return self._parameters[index.row()]
        elif role == self.SelectionModelRole:
            return self._selectionmap[self._parameters[index.row()]['paramid']]

    def allData(self):
        return self._parameters

    def setData(self, index, value, role=QtCore.Qt.UserRole):
        if role == QtCore.Qt.EditRole:
            param = self._parameters[index.row()]
            if index.column() == 0 :
                param[self.headers[index.column()]] = value

            elif 1 <= index.column() <= 3:
                # check that start and stop values are within limits
                # specified by component type
                multiplier = self.getDetail(index, 'multiplier')
                if multiplier is not None:
                    if self.checkLimits(value*multiplier, param):
                        param[self.headers[index.column()]] = value*multiplier
                        if index.column() == 1: # start value, change component to match
                            selection_model = self._selectionmap[param['paramid']]
                            comps = selection_model.selectionComponents()
                            for component in comps:
                                component.set(param['parameter'], value*multiplier)
            else:
                param[self.headers[index.column()]] = value
        elif role == QtCore.Qt.UserRole:
            "replace all values"
            row = index.row()
            if row == -1:
                row = self.rowCount() -1
            self._parameters[row] = value
        return True

    def getDetail(self, index, detail):
        param = self._parameters[index.row()]
        param_type = param['parameter']
        selection_model = self._selectionmap[param['paramid']]
        comps = selection_model.selectionComponents()
        if len(comps) == 0 or param_type == '':
            return None
        # all components must match
        matching_details = []
        for comp in comps:
            details = comp.auto_details()[param_type]
            matching_details.append(details[detail])
        matching_details = set(matching_details)
        if len(matching_details) > 1:
            print 'Components with mis-matched units!'
            return None
        return matching_details.pop()

    def checkLimits(self, value, param):
        selection_model = self._selectionmap[param['paramid']]
        comps = selection_model.selectionComponents()
        if len(comps) == 0:
            return False
        mins = []
        maxs = []
        for comp in comps:
            # get the limit details for the currently selected parameter type
            details = comp.auto_details()[param['parameter']]
            mins.append(details['min'])
            maxs.append(details['max'])
        lower = max(mins)
        upper = min(maxs)
        if lower <= value <= upper:
            return True
        else:
            print 'value out of bounds'
            print 'lower', lower, 'upper', upper, 'value', value
            return False

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
                             'parameter': '',
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

    def removeItem(self, index):
        self.removeRows(index.row(),1)

    def insertItem(self, index, item):
        """For reorder only, item must already have selectionModel in
        for its id"""
        self.insertRows(index.row(), 1)
        self.setData(index, item)

    def flags(self, index):
        if index.isValid():
            if index.column() < 4:
                return QtCore.Qt.ItemIsDragEnabled | \
                       QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | \
                       QtCore.Qt.ItemIsEditable
            else:
                return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        else:
            print 'flags: index invalid'
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

    def selectionParameters(self, param):
        selection_model = self._selectionmap[param['paramid']]
        comps = selection_model.selectionComponents()
        if len(comps) == 0:
            return []
        editable_sets = []
        for comp in comps:
            editable_sets.append(set(comp.auto_details().keys()))
        editable_paramters = set.intersection(*editable_sets)
        return list(editable_paramters)