from PyQt4 import QtCore, QtGui
import numpy as np

from spikeylab.gui.stim.selectionmodel import ComponentSelectionModel
from spikeylab.gui.abstract_drag_view import AbstractDragView
from spikeylab.stim.auto_parameter_model import AutoParameterModel

ERRCELL = QtGui.QColor('firebrick')

class QAutoParameterModel(QtCore.QAbstractTableModel):
    SelectionModelRole = 34
    emptied = QtCore.pyqtSignal(bool)
    hintRequested = QtCore.pyqtSignal(str)
    # stimChanged = QtCore.pyqtSignal(QtCore.QModelIndex, QtCore.QModelIndex)
    def __init__(self, model):
        super(QAutoParameterModel, self).__init__()
        self.model = model
        self._selectionmap = {}

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.model.header(section)

    def rowCount(self, parent=QtCore.QModelIndex()):
        return self.model.nrows()

    def columnCount(self, parent=QtCore.QModelIndex()):
        return self.model.ncols()

    def clearParameters(self):
        self.beginRemoveRows(QtCore.QModelIndex(), 0, self.rowCount())
        self.model.clear_parameters()
        self.endRemoveRows()

    def data(self, index, role=QtCore.Qt.UserRole):
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            col = index.column()
            param = self.model.param(index.row())
            if col == 0:
                item = param[self.model.header(col)]            
            if 0 < col < 4:
                item = param[self.model.header(col)]
                # scale appropriately
                multiplier = self.model.getDetail(index.row(), 'multiplier')
                if multiplier is not None:
                    # return integers for whole numbers, floats otherwise
                    # print 'data val', float(item)/multiplier
                    return float(item)/multiplier
            elif col == 4:
                if param['step'] > 0:
                    if abs(param['start'] - param['stop']) < param['step']:
                        return 0
                    nsteps = np.around(abs(param['start'] - param['stop']), 4) / param['step']
                    item = int(np.ceil(nsteps)+1)
                elif param['start'] == param['stop']:
                    item = 1
                else:
                    item = 0
            return item
        elif role == QtCore.Qt.ToolTipRole:
            if 1 <= index.column() <= 3:
                label = self.model.getDetail(index.row(), 'label')
                return label
        elif role == QtCore.Qt.ForegroundRole:
            # color the background red for bad values
            if not self.checkValidCell(index):
                return QtGui.QBrush(ERRCELL)
        elif role == QtCore.Qt.FontRole:
            # color the background red for bad values
            if not self.checkValidCell(index):
                f = QtGui.QFont()
                f.setWeight(QtGui.QFont.Bold)
                return f

        elif role == QtCore.Qt.UserRole or role == AbstractDragView.DragRole:  #return the whole python object
            return self.model.param(index.row())

        elif role == self.SelectionModelRole:
            # may need to translate to QModelIndexes
            return self.model.selection(self.model.param(index.row()))
            # return self._selectionmap[self._parameters[index.row()]['paramid']]

    def setData(self, index, value, role=QtCore.Qt.UserRole):
        if role == QtCore.Qt.EditRole:
            if index.column() == 0 :
                old_multiplier = self.model.getDetail(index.row(), 'multiplier')
                self.model.setParamValue(index.row(), parameter=str(value))
                # keep the displayed values the same, so multiply to ajust
                # real underlying value
                new_multiplier = self.model.getDetail(index.row(), 'multiplier')
                if old_multiplier is not None and old_multiplier != new_multiplier:
                    new_multiplier = float(new_multiplier)
                    for col in range(1,4):
                        i = self.index(index.row(), col)
                        self.setData(i, self.data(i, QtCore.Qt.EditRole)*(new_multiplier/old_multiplier), QtCore.Qt.EditRole)

            elif 1 <= index.column() <= 3:
                # check that start and stop values are within limits
                # specified by component type
                if isinstance(value, QtCore.QVariant):
                    value = value.toPyObject()
                multiplier = self.model.getDetail(index.row(), 'multiplier')
                if multiplier is not None:
                    if self.model.checkLimits(value*multiplier, self.model.param(index.row())):
                        kwd = {self.model.header(index.column()) : value*multiplier}
                        self.model.setParamValue(index.row(), **kwd)
            else:
                kwd = {self.model.header(index.column()) : value}
                self.model.setParamValue(index.row(), **kwd)


        elif role == QtCore.Qt.UserRole:
            print "replace all values"
            row = index.row()
            if row == -1:
                row = self.rowCount() -1
            self.model.overwriteParam(row, value)
        return True

    def checkValidCell(self, index):
        col = index.column()
        param = self.model.param(index.row())
        if param['parameter'] == '':
            return False
        if col == 1:
            return self.model.checkLimits(param['start'], param)
        if col == 2:
            return self.model.checkLimits(param['stop'], param)
        if col == 4:
            nsteps = self.data(index, role=QtCore.Qt.DisplayRole)
            return nsteps != 0
        return True

    def setParameterList(self, paramlist):
        self._parameters = paramlist

    def insertRows(self, position, rows, parent = QtCore.QModelIndex()):
        self.beginInsertRows(parent, position, position + rows - 1)
        for i in range(rows):
            self.model.insertRow(position)
            # self._selectionmap[self._paramid].hintRequested.connect(self.hintRequested)
        self.endInsertRows()
        if self.rowCount() == 1:
            self.emptied.emit(False)
        return True

    def removeRows(self, position, rows, parent = QtCore.QModelIndex()):
        self.beginRemoveRows(parent, position, position + rows - 1)
        for i in range(rows):
            self.model.removeRow(position)
            # cannot purge selection model, or else we have no way of 
            # recovering it when reordering
        self.endRemoveRows()
        if self.rowCount() == 0:
            self.emptied.emit(True)
        return True

    def removeItem(self, index):
        self.removeRows(index.row(), 1)

    def insertItem(self, index, item):
        """For reorder only, item must already have selectionModel in
        for its id"""
        row = index.row()
        self.beginInsertRows(QtCore.QModelIndex(), row, row)
        self.model.insertRow(row)
        self.endInsertRows()
        self.model.overwriteParam(index.row(), item)

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

    def supportedDropActions(self):
        return QtCore.Qt.MoveAction

    def toggleSelection(self, index, comp):
        self.model.toggleSelection(index.row(), comp)

    def selection(self, index):
        """
        Return the selected Indexes for the given parameter
        """
        return self.model.selection(index.row())

    def selectedParameterTypes(self, index):
        return self.model.selectedParameterTypes(index.row())

    def verify(self):
        return self.model.verify()