import numpy as np

from sparkle.QtWrapper import QtCore, QtGui
from sparkle.gui.abstract_drag_view import AbstractDragView
from sparkle.gui.qconstants import CursorRole
from sparkle.gui.stim.selectionmodel import ComponentSelectionModel
from sparkle.resources import cursors
from sparkle.stim.auto_parameter_model import AutoParameterModel

ERRCELL = QtGui.QColor('firebrick')

class QAutoParameterModel(QtCore.QAbstractTableModel):
    """PyQt wrapper for AutoParameterModel, for it to be able to 
    interface with the :class:`AutoParameterTableView<sparkle.gui.stim.auto_parameter_view.AutoParameterTableView>`"""
    SelectionModelRole = 34
    emptied = QtCore.Signal(bool)
    hintRequested = QtCore.Signal(str)
    countChanged = QtCore.Signal()
    def __init__(self, model):
        super(QAutoParameterModel, self).__init__()
        self.model = model
        self._selectionmap = {}
        self._headers = ['parameter', 'start', 'stop', 'step', 'nsteps']

    def headerData(self, section, orientation, role):
        """Gets the Header for the columns in the table

        Required by view, see :qtdoc:`subclassing<qabstractitemmodel.subclassing>`

        :param section: column of header to return
        :type section: int
        """
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._headers[section]

    def rowCount(self, parent=QtCore.QModelIndex()):
        """Determines the numbers of rows the view will draw

        Required by view, see :qtdoc:`subclassing<qabstractitemmodel.subclassing>`
        """
        return self.model.nrows()

    def columnCount(self, parent=QtCore.QModelIndex()):
        """Determines the numbers of columns the view will draw

        Required by view, see :qtdoc:`subclassing<qabstractitemmodel.subclassing>`
        """
        return len(self._headers)

    def clearParameters(self):
        """Removes all parameters from model"""
        self.beginRemoveRows(QtCore.QModelIndex(), 0, self.rowCount())
        self.model.clear_parameters()
        self.endRemoveRows()

    def data(self, index, role=QtCore.Qt.UserRole):
        """Used by the view to determine data to present

        See :qtdoc:`QAbstractItemModel<QAbstractItemModel.data>`, 
        and :qtdoc:`subclassing<qabstractitemmodel.subclassing>`
        """
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            field = self._headers[index.column()]
            val = self.model.paramValue(row, field)
            if 1 <= index.column() <= 3:
                # standard units for data, not necessary current for UI
                # view will scale and convert appropriately
                unit = self.model.getDetail(index.row(), 'unit')
                if val is not None and unit is not None:
                    return str(val) + ' ' + unit
                else:
                    return val
            else:
                return val

        elif role == QtCore.Qt.EditRole:
            row = index.row()
            field = self._headers[index.column()]
            return self.model.paramValue(row, field)
            # return self.model.paramValue(row, field)
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
            param = self.model.param(index.row())
            for comp in param['selection']:
                comp.clean()
            return param

        elif role == self.SelectionModelRole:
            # may need to translate to QModelIndexes
            return self.model.selection(self.model.param(index.row()))
        
        elif role == CursorRole:
            col = index.column()
            if not index.isValid():
                return QtGui.QCursor(QtCore.Qt.ArrowCursor)
            elif col == 0:
                return cursors.pointyHand()
            elif col < 4:
                return cursors.handEdit()
            else:
                return cursors.openHand()

    def setData(self, index, value, role=QtCore.Qt.UserRole):
        """Sets data at *index* to *value* in underlying data structure

        See :qtdoc:`QAbstractItemModel<QAbstractItemModel.setData>`, 
        and :qtdoc:`subclassing<qabstractitemmodel.subclassing>`
        """
        if role == QtCore.Qt.EditRole:
            if isinstance(value, QtCore.QVariant):
                value = value.toPyObject()
            elif isinstance(value, QtCore.QString):
                value = str(value)
            self.model.setVerifiedValue(index.row(), self._headers[index.column()], value)
            self.countChanged.emit()
        elif role == QtCore.Qt.UserRole:
            row = index.row()
            if row == -1:
                row = self.rowCount() -1
            self.model.overwriteParam(row, value)
        return True

    def checkValidCell(self, index):
        """Asks the model if the value at *index* is valid

        See :meth:`isFieldValid<sparkle.stim.auto_parameter_model.AutoParameterModel.isFieldValid>`
        """
        col = index.column()
        row = index.row()
        return self.model.isFieldValid(row, self._headers[index.column()])

    def findFileParam(self, comp):
        """wrapper for :meth:`findFileParam<sparkle.stim.auto_parameter_model.AutoParameterModel.findFileParam>`"""
        return self.model.findFileParam(comp)

    def setParameterList(self, paramlist):
        """clears parameter list and assigns *paramlist*"""
        self._parameters = paramlist

    def insertRows(self, position, rows, parent = QtCore.QModelIndex()):
        """Inserts new parameters and emits an emptied False signal

        :param position: row location to insert new parameter
        :type position: int
        :param rows: number of new parameters to insert
        :type rows: int
        :param parent: Required by QAbstractItemModel, can be safely ignored
        """
        self.beginInsertRows(parent, position, position + rows - 1)
        for i in range(rows):
            self.model.insertRow(position)
            # self._selectionmap[self._paramid].hintRequested.connect(self.hintRequested)
        self.endInsertRows()
        if self.rowCount() == 1:
            self.emptied.emit(False)
        return True

    def removeRows(self, position, rows, parent = QtCore.QModelIndex()):
        """Removes parameters from the model. Emits and emptied True signal, if there are no parameters left.

        :param position: row location of parameters to remove
        :type position: int
        :param rows: number of parameters to remove
        :type rows: int
        :param parent: Required by QAbstractItemModel, can be safely ignored
        """
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
        """Removes the parameters at *index*"""
        self.removeRows(index.row(), 1)

    def insertItem(self, index, item):
        """Inserts parameter *item* at index"""
        row = index.row()
        self.beginInsertRows(QtCore.QModelIndex(), row, row)
        self.model.insertRow(row)
        self.endInsertRows()
        self.model.overwriteParam(index.row(), item)

    def flags(self, index):
        """"Determines interaction allowed with table cells.

        See :qtdoc:`QAbstractItemModel<QAbstractItemModel.flags>`, 
        and :qtdoc:`subclassing<qabstractitemmodel.subclassing>`
        """
        if index.isValid():
            if self.model.editableRow(index.row()) and index.column() < 4:
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
        """Toggles a component in or out of the currently 
        selected parameter's compnents list"""
        self.model.toggleSelection(index.row(), comp)

    def selection(self, index):
        """Returns the selected Indexes of components for 
        the given parameter"""
        return self.model.selection(index.row())

    def selectedParameterTypes(self, index):
        """Returns a list of the parameter types valid as
        options for the parameter field for parameter at *index*"""
        return self.model.selectedParameterTypes(index.row())

    def fileParameter(self, comp):
        """Returns the row which comp is found in

        wrapper for :meth:`findFileParam<sparkle.stim.auto_parameter_model.AutoParameterModel.findFileParam>`
        """
        return self.model.fileParameter(comp)

    def verify(self):
        """Wrapper for :meth:`verify<sparkle.stim.auto_parameter_model.AutoParameterModel.verify>`"""
        return self.model.verify()
