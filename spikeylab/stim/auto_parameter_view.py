from PyQt4 import QtGui, QtCore

from spikeylab.main.drag_label import FactoryLabel
from auto_parameter_form import Ui_AutoParamWidget
from spikeylab.stim.selectionmodel import ComponentSelectionModel
from spikeylab.main.abstract_drag_view import AbstractDragView

class AutoParameterTableView(AbstractDragView, QtGui.QTableView):
    """List View which holds parameter widgets"""
    def __init__(self):
        QtGui.QTableView.__init__(self)
        AbstractDragView.__init__(self)

        self.setItemDelegateForColumn(0,ComboboxDelegate())
        self.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked | QtGui.QAbstractItemView.SelectedClicked)
        

    def edit(self, index, trigger, event):
        "Sets editing widget for selected list item"
        self.model().updateSelectionModel(index)
        return super(AutoParameterTableView, self).edit(index, trigger, event)


    def grabImage(self, index):
        # grab an image of the cell we are moving
            # assume all rows same height
        row_height = self.rowHeight(0)
        # -5 becuase it a a little off
        y = (row_height*index.row()) + row_height - 5
        x = self.width()
        rect = QtCore.QRect(5,y,x,row_height)
        pixmap = QtGui.QPixmap()
        pixmap = pixmap.grabWidget(self, rect)
        return pixmap

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            index = self.indexAt(event.pos())
            self.selectRow(index.row())
            self.edit(index, QtGui.QAbstractItemView.DoubleClicked, event)
        else:
            super(AutoParameterTableView, self).mousePressEvent(event)

    def paintEvent(self, event):
        super(AutoParameterTableView, self).paintEvent(event)

        if self.dragline is not None:
            pen = QtGui.QPen(QtCore.Qt.blue)
            painter = QtGui.QPainter(self.viewport())
            painter.setPen(pen)
            painter.drawLine(self.dragline)

    def cursor(self, pos):
        row = self.indexAt(pos).row()
        if row == -1:
            row = self.model().rowCount()
        row_height = self.rowHeight(0)
        y = (row_height*row)
        x = self.width()
        return QtCore.QLine(0,y,x,y)

    def dropEvent(self, event):
        param = self.dropAssist(event)
        index = self.indexAt(event.pos())
        self.model().insertRows(index.row(),1)
        if isinstance(event.source(), FactoryLabel):
            pass
        else:
            self.model().setData(index, param)

        event.accept()


class ComboboxDelegate(QtGui.QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        param = index.data(QtCore.Qt.UserRole)
        parameter_types = index.model().selectionParameters(param)
        editor = QtGui.QComboBox(parent)
        editor.addItems(parameter_types)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, QtCore.Qt.EditRole)
        if value != '':
            param = index.data(QtCore.Qt.UserRole)
            parameter_types = index.model().selectionParameters(param)
            typeidx = parameter_types.index(value)
            editor.setCurrentIndex(typeidx)

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        model.setData(index, value, QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

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
        self.step_lnedt.setText(str(paramdict['step']))
        self.stop_lnedt.setText(str(paramdict['stop']))
        self.start_lnedt.setText(str(paramdict['start']))
        typeidx = PARAMETER_TYPES.index(paramdict['parameter'])
        self.type_cmbx.setCurrentIndex(typeidx)
        self._paramdict = paramdict

    def paramValues(self):
        paramdict = self._paramdict
        paramdict['start'] = float(self.start_lnedt.text())
        paramdict['step'] = float(self.step_lnedt.text())
        paramdict['stop'] = float(self.stop_lnedt.text())
        paramdict['parameter'] = self.type_cmbx.currentText()
        return paramdict

    def paramId(self):
        return self._paramdict['paramid']