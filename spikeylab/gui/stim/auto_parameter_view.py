from PyQt4 import QtGui, QtCore

from spikeylab.gui.abstract_drag_view import AbstractDragView
from spikeylab.gui.stim.smart_spinbox import SmartSpinBox

class AddLabel(object):
    name = "Add"
        
class AutoParameterTableView(AbstractDragView, QtGui.QTableView):
    """List View which holds parameter widgets"""
    hintRequested = QtCore.pyqtSignal(str)
    parameterChanged = QtCore.pyqtSignal(list)
    def __init__(self):
        QtGui.QTableView.__init__(self)
        AbstractDragView.__init__(self)

        self.setItemDelegate(SmartDelegate())
        self.setItemDelegateForColumn(0,ComboboxDelegate())
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        palette = self.palette()
        palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(100,100,255))
        self.setPalette(palette)

    # def edit(self, index, trigger, event):
    #     "Sets editing widget for selected list item"
    #     if index.isValid():
    #         self.model().updateSelectionModel(index)
    #     return super(AutoParameterTableView, self).edit(index, trigger, event)

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
        index = self.indexAt(event.pos())
        if index.isValid():
            self.selectRow(index.row())
            self.parameterChanged.emit(self.model().selection(index))
            self.edit(index, QtGui.QAbstractItemView.DoubleClicked, event)
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
        if event.source() == self or isinstance(param, AddLabel):
            index = self.indexAt(event.pos())
            self.model().insertRows(index.row(),1)
            if event.source() == self:
                self.model().setData(index, param)
            else:
                self.hintRequested.emit('Select Components in view to modify')
                row = index.row()
                # select rows doesn't work with -ve indexes
                if row == -1:
                    row = self.model().rowCount() - 1
                self.selectRow(row)
                self.parameterChanged.emit(self.model().selection(index))

        event.accept()
        
    def indexXY(self, index):
        """Return the top left coordinates of the row for the given index"""
        row = index.row()
        if row == -1:
            row = self.model().rowCount()
        y = self.rowHeight(0)*row
        return 0, y

    def componentSelection(self, comp):
        # current row which is selected in auto parameters to all component selection to
        indexes = self.selectedIndexes()
        index = indexes[0]
        # if len(index) > 1:
        #     print 'indexes', index
        #     raise Exception("Multiple indexes selected per click")
        self.model().toggleSelection(index, comp)

class ComboboxDelegate(QtGui.QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        parameter_types = index.model().selectedParameterTypes(index)
        editor = QtGui.QComboBox(parent)
        editor.addItems(parameter_types)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, QtCore.Qt.EditRole)
        if value != '':
            parameter_types = index.model().selectedParameterTypes(index)
            typeidx = parameter_types.index(value)
            editor.setCurrentIndex(typeidx)

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        model.setData(index, value, QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class SmartDelegate(QtGui.QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        spnbox = SmartSpinBox(parent)
        # could set this in setEditorData to reflect
        # parameter specific max and mins
        spnbox.setMinimum(0)
        spnbox.setMaximum(2000)
        return spnbox