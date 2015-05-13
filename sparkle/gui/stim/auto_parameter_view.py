import re

from sparkle.QtWrapper import QtCore, QtGui
from sparkle.gui.abstract_drag_view import AbstractDragView
from sparkle.gui.stim.smart_spinbox import SmartSpinBox, trim


class AddLabel(object):
    name = "Add"
        
class AutoParameterTableView(AbstractDragView, QtGui.QTableView):
    """Table View which holds auto parameter details, with a parameter per row"""
    hintRequested = QtCore.Signal(str)
    parameterChanged = QtCore.Signal(list)
    dragActive = QtCore.Signal(bool)
    def __init__(self, parent=None):
        super(AutoParameterTableView, self).__init__()

        self.setItemDelegate(SmartDelegate())
        self.setItemDelegateForColumn(0,ComboboxDelegate())
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        palette = self.palette()
        palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(100,100,255))
        self.setPalette(palette)

    # def setModel(self, model):
    #     super(AutoParameterTableView, self).setModel(model)
    #     self.model.rowScale.connect(self.setRowScale)

    # def edit(self, index, trigger, event):
    #     "Sets editing widget for selected list item"
    #     if index.isValid():
    #         self.model().updateSelectionModel(index)
    #     return super(AutoParameterTableView, self).edit(index, trigger, event)

    def grabImage(self, index):
        """Returns an image of the parameter row.

        Re-implemented from :meth:`AbstractDragView<sparkle.gui.abstract_drag_view.AbstractDragView.grabImage>`
        """
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
        """Begins edit on cell clicked, if allowed, and passes event to super class"""
        index = self.indexAt(event.pos())
        if index.isValid():
            self.selectRow(index.row())
            # selecting the row sets the current index to 0,0 for tab
            # order to work correctly, we must set the current index
            self.setCurrentIndex(index)
            self.parameterChanged.emit(self.model().selection(index))
            self.edit(index, QtGui.QAbstractItemView.DoubleClicked, event)
        super(AutoParameterTableView, self).mousePressEvent(event)

    def paintEvent(self, event):
        """Adds cursor line for view if drag active. Passes event to superclass
        see :qtdoc:`qtdocs<qabstractscrollarea.paintEvent>`"""
        super(AutoParameterTableView, self).paintEvent(event)

        if self.dragline is not None:
            pen = QtGui.QPen(QtCore.Qt.blue)
            painter = QtGui.QPainter(self.viewport())
            painter.setPen(pen)
            painter.drawLine(self.dragline)

    def cursor(self, pos):
        """Returns a line at the nearest row split between parameters.

        Re-implemented from :meth:`AbstractDragView<sparkle.gui.abstract_drag_view.AbstractDragView.cursor>`
        """
        row = self.indexAt(pos).row()
        if row == -1:
            row = self.model().rowCount()
        row_height = self.rowHeight(0)
        y = (row_height*row)
        x = self.width()
        return QtCore.QLine(0,y,x,y)

    def dropped(self, param, event):
        """Adds the dropped parameter *param* into the protocol list.

        Re-implemented from :meth:`AbstractDragView<sparkle.gui.abstract_drag_view.AbstractDragView.dropped>`
        """
        if event.source() == self or isinstance(param, AddLabel):
            index = self.indexAt(event.pos())
            self.model().insertRows(index.row(),1)
            if event.source() == self:
                self.model().setData(index, param)
            else:
                self.hintRequested.emit('Select Components in view to modify -- click to toggle membership of component in auto-parameter')
                row = index.row()
                # select rows doesn't work with -ve indexes
                if row == -1:
                    row = self.model().rowCount() - 1
                self.selectRow(row)
                self.parameterChanged.emit(self.model().selection(index))
        self.dragActive.emit(False)

    def indexXY(self, index):
        """Coordinates for the parameter row at *index*

        Re-implemented from :meth:`AbstractDragView<sparkle.gui.abstract_drag_view.AbstractDragView.indexXY>`
        """
        row = index.row()
        if row == -1:
            row = self.model().rowCount()
        y = self.rowHeight(0)*row
        return 0, y

    def componentSelection(self, comp):
        """Toggles the selection of *comp* from the currently active parameter"""
        # current row which is selected in auto parameters to all component selection to
        indexes = self.selectedIndexes()
        index = indexes[0]
        self.model().toggleSelection(index, comp)


class ComboboxDelegate(QtGui.QStyledItemDelegate):
    """Drop down editor for parameter selection

    All functions re-implemented from :qtdoc:`QStyledItemDelegate`"""
    def createEditor(self, parent, option, index):
        parameter_types = index.model().selectedParameterTypes(index)
        # tight couple hack to remove disallowed selection of file from table
        if 'filename' in parameter_types:
            parameter_types.remove('filename')
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
    """Just a deletegate with a :class:`SmartSpinBox<sparkle.gui.stim.smart_spinbox.SmartSpinBox>`"""
    _scales = ['ms', 'kHz']
    def createEditor(self, parent, option, index):
        spnbox = SmartSpinBox(parent)
        model = parent.parentWidget().model().model
        unit = model.getDetail(index.row(), 'unit')
        if unit is None:
            # parameter type must be selected first, don't show editor
            return None
        if unit == 's':
            spnbox.setScale(self._scales[0])
        elif unit == 'Hz':
            spnbox.setScale(self._scales[1])
        else:
            spnbox.setScale(unit)
    
        spnbox.setMinimum(model.getDetail(index.row(), 'min'))
        spnbox.setMaximum(model.getDetail(index.row(), 'max'))
        spnbox.setKeyboardTracking(True)
        return spnbox
        
    def displayText(self, value, locale):
        # we don't have the luxury of index and model, so we got the
        # model to include the base unit we can parse out and manually
        # adjust the scale here. This is essentially code duplicated
        # from SmartSpinBox
        txt = super(SmartDelegate, self).displayText(value, locale)
        result = re.search('[a-zA-Z]+', txt)
        if result is not None:
            unit = result.group(0)
            val = re.search('-?\d+\.?\d*', txt).group(0)
            if unit == 's':
                if self._scales[0] == 'ms':
                    txt = trim(float(val)*1000) + ' ms'
            elif unit == 'Hz':
                if self._scales[1] == 'kHz':
                    txt = trim(float(val)*0.001) + ' kHz'
            else:
                txt = trim(float(val))
        return txt

    @staticmethod
    def updateScales(tscale, fscale):
        SmartDelegate._scales[0] = tscale
        SmartDelegate._scales[1] = fscale
