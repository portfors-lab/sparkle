from PyQt4 import QtGui, QtCore

import cPickle

from spikeylab.main.drag_label import FactoryLabel
from auto_parameter_form import Ui_AutoParamWidget
from spikeylab.stim.selectionmodel import ComponentSelectionModel

PARAMETER_TYPES = ['duration', 'intensity', 'frequency']

class AutoParameterListView(QtGui.QTableView):
    """List View which holds parameter widgets"""
    def __init__(self):
        QtGui.QListView.__init__(self)

        # self.setItemDelegate(AutoParameterDelegate())
        self.setItemDelegateForColumn(0,ComboboxDelegate())
        self.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked | QtGui.QAbstractItemView.SelectedClicked)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.dragline = None
        self.original_pos = None

    def edit(self, index, trigger, event):
        "Sets editing widget for selected list item"
        self.model().updateSelectionModel(index)
        return super(AutoParameterListView, self).edit(index, trigger, event)

    def mousePressEvent(self, event):
        index = self.indexAt(event.pos())
        if event.button() == QtCore.Qt.RightButton:
        # if False:
            print 'drag start', index.row()
            selected = self.model().data(index, QtCore.Qt.UserRole)

            ## convert to  a bytestream
            bstream = cPickle.dumps(selected)
            mimeData = QtCore.QMimeData()
            mimeData.setData("application/x-protocol", bstream)

            self.limbo_component = selected
            drag = QtGui.QDrag(self)
            drag.setMimeData(mimeData)

            # grab an image of the cell we are moving
            # assume all rows same height
            row_height = self.rowHeight(0)
            # -5 becuase it a a little off
            y = (row_height*index.row()) + row_height - 5
            x = self.width()
            rect = QtCore.QRect(5,y,x,row_height)
            pixmap = QtGui.QPixmap()
            pixmap = pixmap.grabWidget(self, rect)

            # below makes the pixmap half transparent
            painter = QtGui.QPainter(pixmap)
            painter.setCompositionMode(painter.CompositionMode_DestinationIn)
            painter.fillRect(pixmap.rect(), QtGui.QColor(0, 0, 0, 127))
            painter.end()
            
            drag.setPixmap(pixmap)

            drag.setHotSpot(QtCore.QPoint(pixmap.width()/2, pixmap.height()/2))
            drag.setPixmap(pixmap)

            self.original_pos = index.row()

            self.model().removeRows(index.row(),1)
            result = drag.start(QtCore.Qt.MoveAction)
        else:
            self.selectRow(index.row())
            self.edit(index, QtGui.QAbstractItemView.DoubleClicked, event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-protocol"):
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            super(AutoParameterListView, self).dragEnterEvent(event)

    def mouseReleaseEvent(self, event):
        print 'mouse release', event.button()

    def dragLeaveEvent(self, event):
        self.dragline = None
        self.viewport().update()
        event.accept()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-protocol"):
            #find the nearest row break to cursor
            # assume all rows same height
            row = self.indexAt(event.pos()).row()
            if row == -1:
                row = self.model().rowCount()
            row_height = self.rowHeight(0)
            y = (row_height*row)
            x = self.width()
            self.dragline = QtCore.QLine(0,y,x,y)          
            self.viewport().update()
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def paintEvent(self, event):
        super(AutoParameterListView, self).paintEvent(event)

        if self.dragline is not None:
            pen = QtGui.QPen(QtCore.Qt.blue)
            painter = QtGui.QPainter(self.viewport())
            painter.setPen(pen)
            painter.drawLine(self.dragline)

    def dropEvent(self, event):
        self.dragline = None
        index = self.indexAt(event.pos())
        print 'drop!', index.row()
        self.model().insertRows(index.row(),1)
        if isinstance(event.source(), FactoryLabel):
            pass
        else:
            data = event.mimeData()
            bstream = data.retrieveData("application/x-protocol",
                                        QtCore.QVariant.ByteArray)
            selected = cPickle.loads(str(bstream))
            self.model().setData(index, selected)

        self.original_pos = None
        event.accept()

    def childEvent(self, event):
        if event.type() == QtCore.QEvent.ChildRemoved:
            # hack to catch drop offs   
            if self.original_pos is not None:
                selected = self.limbo_component
                self.model().insertRows(self.original_pos,1)
                self.model().setData(self.model().index(self.original_pos,0), selected)
                self.original_pos = None

class ComboboxDelegate(QtGui.QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QtGui.QComboBox(parent)
        editor.addItems(PARAMETER_TYPES)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, QtCore.Qt.EditRole)
        typeidx = PARAMETER_TYPES.index(value)
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