from PyQt4 import QtGui, QtCore

from auto_parameter_form import Ui_AutoParamWidget
from spikeylab.stim.selectionmodel import ComponentSelectionModel

PARAMETER_TYPES = ['duration', 'intensity', 'frequency']

class AutoParameterListView(QtGui.QListView):
    """List View which holds parameter widgets"""
    def __init__(self):
        QtGui.QListView.__init__(self)

        self.setItemDelegate(AutoParameterDelegate())
        self.setEditTriggers(QtGui.QAbstractItemView.CurrentChanged | QtGui.QAbstractItemView.DoubleClicked | QtGui.QAbstractItemView.SelectedClicked)
        self.setAcceptDrops(True)
        self.setDragDropMode(QtGui.QAbstractItemView.InternalMove)

    def edit(self, index, trigger, event):
        "Sets editing widget for selected list item"
        self.model().updateSelectionModel(index)
        return super(AutoParameterListView, self).edit(index, trigger, event)

class AutoParameterModel(QtCore.QAbstractListModel):
    _paramid = 0
    def __init__(self, stimulus=None):
        super(AutoParameterModel, self).__init__()
        self._parameters = []
        self._stimview = None #this should be any view for StimulusModel
        self._stimmodel = stimulus
        self._selectionmap = {}

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._parameters)

    def data(self, index, role=QtCore.Qt.UserRole):
        return self._parameters[index.row()]
        
    def setData(self, index, value, role):
        self._parameters[index.row()] = value
        return True

    def setParameterList(self, paramlist):
        self._parameters = paramlist

    def insertParameter(self, param, position):
        self.beginInsertRows(QtCore.QModelIndex(), position, position)
        self._parameters.insert(position, param)
        self.endInsertRows()

    def insertRows(self, position, rows, parent = QtCore.QModelIndex()):
        self.beginInsertRows(parent, position, position + rows - 1)
        for i in range(rows):
            defaultparam = { 'start': 0,
                             'delta': 1,
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


class AutoParameterDelegate(QtGui.QStyledItemDelegate):

    def paint(self, painter, option, index):
        # paint a fake editor widget
        painter.drawRect(option.rect)

        param = index.model().data(index, QtCore.Qt.UserRole)
        if option.state & QtGui.QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        else:
            tmpedit = AutoParamWidget()
            tmpedit.setParamValues(param)
            tmpedit.setGeometry(option.rect)
            selfie = QtGui.QPixmap.grabWidget(tmpedit, QtCore.QRect(0,0, tmpedit.width(), tmpedit.height()))
            painter.drawPixmap(option.rect, selfie)
            tmpedit.close()
        

    def sizeHint(self, option, index):
        #this will always be the same?
        return QtCore.QSize(100,150)

    def createEditor(self, parent, option, index):
        editor = AutoParamWidget(parent)
        return editor

    def setEditorData(self, editor, index):
        param = index.data(QtCore.Qt.UserRole)
        editor.setParamValues(param)

    def setModelData(self, editor, model, index):
        param = editor.paramValues()
        model.setData(index, param, QtCore.Qt.EditRole)


class AutoParamWidget(QtGui.QWidget, Ui_AutoParamWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.type_cmbx.addItems(PARAMETER_TYPES)

    def setParamValues(self, paramdict):
        self.step_lnedt.setText(str(paramdict['delta']))
        self.stop_lnedt.setText(str(paramdict['stop']))
        self.start_lnedt.setText(str(paramdict['start']))
        typeidx = PARAMETER_TYPES.index(paramdict['parameter'])
        self.type_cmbx.setCurrentIndex(typeidx)
        self._paramdict = paramdict

    def paramValues(self):
        paramdict = self._paramdict
        paramdict['start'] = float(self.start_lnedt.text())
        paramdict['delta'] = float(self.step_lnedt.text())
        paramdict['stop'] = float(self.stop_lnedt.text())
        paramdict['parameter'] = self.type_cmbx.currentText()
        return paramdict

    def paramId(self):
        return self._paramdict['paramid']