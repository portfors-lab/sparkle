from PyQt4 import QtCore, QtGui

import numpy as np

from spikeylab.stim.selectionmodel import ComponentSelectionModel
from spikeylab.main.abstract_drag_view import AbstractDragView

ERRCELL = QtGui.QColor('firebrick')

class AutoParameterModel(QtCore.QAbstractTableModel):
    SelectionModelRole = 34
    _paramid = 0
    emptied = QtCore.pyqtSignal(bool)
    hintRequested = QtCore.pyqtSignal(str)
    stimChanged = QtCore.pyqtSignal(QtCore.QModelIndex, QtCore.QModelIndex)
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

    def clearParameters(self):
        self.beginRemoveRows(QtCore.QModelIndex(), 0, self.rowCount())
        self._parameters = []
        self._selectionmap = {}
        self.endRemoveRows()

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
                    # return integers for whole numbers, floats otherwise
                    return float(item)/multiplier
            elif col == 4:
                if param['step'] > 0:
                    if abs(param['start'] - param['stop']) < param['step']:
                        return 0
                    nsteps = np.around(abs(param['start'] - param['stop']), 4) / param['step']
                    # print 'nsteps', nsteps
                    item = int(np.ceil(nsteps) + 1)
                elif param['start'] == param['stop']:
                    item = 1
                else:
                    item = 0
            return item
        elif role == QtCore.Qt.ToolTipRole:
            if 1 <= index.column() <= 3:
                label = self.getDetail(index, 'label')
                return label
        elif role == QtCore.Qt.ForegroundRole:
            # color the background red for bad values
            if not self.check_valid_cell(index):
                return QtGui.QBrush(ERRCELL)
        elif role == QtCore.Qt.FontRole:
            # color the background red for bad values
            if not self.check_valid_cell(index):
                f = QtGui.QFont()
                f.setWeight(QtGui.QFont.Bold)
                return f

        elif role == QtCore.Qt.UserRole or role == AbstractDragView.DragRole:  #return the whole python object
            return self._parameters[index.row()]
        elif role == self.SelectionModelRole:
            return self._selectionmap[self._parameters[index.row()]['paramid']]

    def check_valid_cell(self, index):
        col = index.column()
        param = self._parameters[index.row()]
        if param['parameter'] == '':
            return False
        if col == 1:
            return self.checkLimits(param['start'], param)
        if col == 2:
            return self.checkLimits(param['stop'], param)
        if col == 4:
            nsteps = self.data(index, role=QtCore.Qt.DisplayRole)
            return nsteps != 0
        return True

    def allData(self):
        return self._parameters

    def setData(self, index, value, role=QtCore.Qt.UserRole):
        if role == QtCore.Qt.EditRole:
            param = self._parameters[index.row()]
            if index.column() == 0 :
                old_multiplier = self.getDetail(index, 'multiplier')
                param[self.headers[index.column()]] = value
                # keep the displayed values the same, so multiply to ajust
                # real underlying value
                try:
                    new_multiplier = float(self.getDetail(index, 'multiplier'))
                except:
                    print index.row(), index.column(), param['parameter'], 'new_multiplier', self.getDetail(index, 'multiplier')

                if old_multiplier is not None and old_multiplier != new_multiplier:
                    for col in range(1,4):
                        i = self.index(index.row(), col)
                        self.setData(i, self.data(i, QtCore.Qt.EditRole)*(new_multiplier/old_multiplier), QtCore.Qt.EditRole)

            elif 1 <= index.column() <= 3:
                # check that start and stop values are within limits
                # specified by component type
                multiplier = self.getDetail(index, 'multiplier')
                if multiplier is not None:
                    if self.checkLimits(value*multiplier, param):
                        param[self.headers[index.column()]] = value*multiplier
            else:
                param[self.headers[index.column()]] = value
        elif role == QtCore.Qt.UserRole:
            "replace all values"
            row = index.row()
            if row == -1:
                row = self.rowCount() -1
            self._parameters[row] = value
        return True

    def updateComponentStartVals(self):
        """Go through selected components for each parameter and set the start value"""
        for param in self._parameters:
            selection_model = self._selectionmap[param['paramid']]
            comps = selection_model.selectionComponents()
            for component in comps:
                component.set(param['parameter'], param['start'])
                # emit signal, so stimulusview knows to update
                self.stimChanged.emit(self._stimmodel.index(0,0), self._stimmodel.index(self._stimmodel.rowCount(), self._stimmodel.columnCount()))
    
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
            if not param_type in comp.auto_details():
                self.hintRequested.emit('INCOMPATABLE COMPONENTS FOR PARAMETER TYPE {}'.format(param_type))
                return None
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
            try:
                details = comp.auto_details()[param['parameter']]
                mins.append(details['min'])
                maxs.append(details['max'])
            except KeyError:
                return False
        lower = max(mins)
        upper = min(maxs)
        if lower <= value <= upper:
            return True
        else:
            # print 'value out of bounds:'
            # print 'lower', lower, 'upper', upper, 'value', value
            return False 

    def setParameterList(self, paramlist):
        self._parameters = paramlist

    def insertRows(self, position, rows, parent = QtCore.QModelIndex()):
        if position == -1:
            position = self.rowCount()
        self.beginInsertRows(parent, position, position + rows - 1)
        for i in range(rows):
            defaultparam = { 'start': 0,
                             'step': 0,
                             'stop': 0,
                             'parameter': '',
                             'paramid' : self._paramid,
                            }
            self._parameters.insert(position, defaultparam)
            self._selectionmap[self._paramid] = ComponentSelectionModel(self._stimmodel)
            self._selectionmap[self._paramid].hintRequested.connect(self.hintRequested)
            self._paramid +=1

        self.endInsertRows()
        if self.rowCount() == 1:
            self.emptied.emit(False)
        return True

    def removeRows(self, position, rows, parent = QtCore.QModelIndex()):
        self.beginRemoveRows(parent, position, position + rows - 1)
        for i in range(rows):
            p = self._parameters.pop(position)
            # cannot purge selection model, or else we have no way of 
            # recovering it when reordering
        self.endRemoveRows()
        if self.rowCount() == 0:
            self.emptied.emit(True)
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

    def setStimView(self, stimview):
        self._stimview = stimview
        self.setStimModel(stimview.model())

    def stimView(self):
        return self._stimview

    def setStimModel(self, model):
        self._stimmodel = model

    def stimModel(self):
        return self._stimmodel

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

    def doc(self):
        """
        JSON doc for recreating this model
        """
        d = []
        for param in self._parameters:
            jp = param.copy()
            indexes = self.selection(param)
            # convert indexes into JSON serializable format
            jindexes = []
            for index in indexes:
                jindexes.append((index.row(), index.column()))
            jp['selection'] = jindexes
            d.append(jp)

        return d

    @staticmethod
    def loadFromTemplate(template, stim_model):
        auto_model = stim_model.autoParams() # or create and set new
        for param in reversed(template):
            index = auto_model.index(0,0)
            auto_model.insertRows(0,1)
            # cheat and steal id, so we can set param directly
            paramid = auto_model._parameters[0]['paramid']
            param['paramid'] = paramid
            selection_tuples = param.pop('selection')
            auto_model.setData(index, param)
            # set the selected components
            selection_model = auto_model.data(index, auto_model.SelectionModelRole)
            for selected in selection_tuples:
                selection_model.select(stim_model.index(*selected))

        return True

    def verify(self):
        for param in self._parameters:
            if param['parameter'] == '':
                return "Auto-parameter type undefined"
            if param['parameter'] not in self.selectionParameters(param):
                return 'Parameter {} not present in all selected components'.format(param['parameter'])
            if param['step'] == 0 and param['start'] != param['stop']:
                return "Auto-parameter step size of 0 not allowed"
            if abs(param['stop'] - param['start']) < param['step']:
                return "Auto-parameter step size larger than range"
            if not self.checkLimits(param['start'], param):
                return "Auto-parameter start value invalid"
            if not self.checkLimits(param['stop'], param):
                return "Auto-parameter stop value invalid"
        return 0
