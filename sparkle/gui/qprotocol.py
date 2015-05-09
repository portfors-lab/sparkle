import sparkle
from sparkle.QtWrapper import QtCore, QtGui
from sparkle.gui.abstract_drag_view import AbstractDragView
from sparkle.gui.qconstants import CursorRole
from sparkle.gui.stim.factory import StimFactory
from sparkle.gui.stim.qstimulus import QStimulusModel
from sparkle.resources import cursors
from sparkle.run.protocol_model import ProtocolTabelModel


class QProtocolTabelModel(QtCore.QAbstractTableModel):
    """Qt wrapper for :class:`ProcotolModel<sparkle.run.protocol_model.ProtocolTabelModel>`,
    based on :qtdoc:`QAbstractTableModel`"""
    def __init__(self, tests=None, parent=None):
        super(QProtocolTabelModel, self).__init__(parent)
        if tests is None:
            self._testmodel = ProtocolTabelModel()
        else:
            self._testmodel = tests
        self.headers = ['Tag', 'Test type', 'Reps', 'Length', 'Total', 'Generation rate']
        self.setSupportedDragActions(QtCore.Qt.MoveAction)

    def headerData(self, section, orientation, role):
        """Get the Header for the columns in the table

        Required by view, see :qtdoc:`subclassing<qabstractitemmodel.subclassing>`

        :param section: column of header to return
        :type section: int
        """
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.headers[section]

    def allHeaders(self):
        """Gets all header text

        :returns: list<str> all header text, in column order"""
        return self.headers
                        
    def rowCount(self, parent=QtCore.QModelIndex()):
        """Determines the numbers of rows the view will draw

        Required by view, see :qtdoc:`subclassing<qabstractitemmodel.subclassing>`
        """
        return self._testmodel.rowCount()

    def columnCount(self, parent=QtCore.QModelIndex()):
        """Determines the numbers of columns the view will draw

        Required by view, see :qtdoc:`subclassing<qabstractitemmodel.subclassing>`
        """
        return len(self.headers)

    def data(self, index, role):
        """Used by the view to determine data to present

        See :qtdoc:`QAbstractItemModel<QAbstractItemModel.data>`, 
        and :qtdoc:`subclassing<qabstractitemmodel.subclassing>`
        """
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            test = self._testmodel.test(index.row())
            col = index.column()
            if col == 0:
                item = test.userTag()
            elif col == 1:
                item = test.stimType()
            elif col == 2:
                item = test.repCount()
            elif col == 3:
                item = test.traceCount()
            elif col == 4:
                item = test.traceCount()*test.loopCount()*test.repCount()
            elif col == 5:
                item = test.samplerate()

            return item
        elif role == QtCore.Qt.UserRole:  #return the whole python object
            test = self._testmodel.test(index.row())
            return QStimulusModel(test)
        elif role == QtCore.Qt.UserRole + 1:  #return the whole python object
            test = self._testmodel.test(index.row())
            return test
        elif role == CursorRole:
            col = index.column()
            if not index.isValid():
                return QtGui.QCursor(QtCore.Qt.ArrowCursor)
            elif col == 0:
                return QtGui.QCursor(QtCore.Qt.IBeamCursor)
            else:
                return cursors.openHand()


    def flags(self, index):
        """"Determines interaction allowed with table cells.

        See :qtdoc:`QAbstractItemModel<QAbstractItemModel.flags>`, 
        and :qtdoc:`subclassing<qabstractitemmodel.subclassing>`
        """
        if index.column() == 0 or index.column == self.headers.index('Reps'):
            return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        else:
            return QtCore.Qt.ItemIsEnabled

    def setData(self, index, value, role):
        """Sets data at *index* to *value* in underlying data structure

        See :qtdoc:`QAbstractItemModel<QAbstractItemModel.setData>`, 
        and :qtdoc:`subclassing<qabstractitemmodel.subclassing>`
        """
        if role == QtCore.Qt.EditRole:
            if isinstance(value, QtCore.QVariant):
                value = value.toPyObject()
            if index.column() == 0:
                test = self._testmodel.test(index.row())
                test.setUserTag(str(value))
                return True
            if index.column() == 2:
                test = self._testmodel.test(index.row())
                test.setRepCount(value)
                return True
        return False
        
    def removeItem(self, index):
        """Alias for removeTest"""
        self.removeTest(index.row())

    def insertItem(self, index, item):
        """Alias for insertTest"""
        self.insertTest(item, index.row())

    def removeTest(self, position):
        """See :meth:`ProcotolModel<sparkle.run.protocol_model.ProtocolTabelModel.remove>`"""
        self.beginRemoveRows(QtCore.QModelIndex(), position, position)
        test = self._testmodel.remove(position)
        self.endRemoveRows()
        return test

    def insertTest(self, stim, position):
        """See :meth:`ProcotolModel<sparkle.run.protocol_model.ProtocolTabelModel.insert>`"""
        if position == -1:
            position = self.rowCount()
        self.beginInsertRows(QtCore.QModelIndex(), position, position)
        self._testmodel.insert(stim,  position)
        self.endInsertRows()

    def clearTests(self):
        """See :meth:`ProcotolModel<sparkle.run.protocol_model.ProtocolTabelModel.clear>`"""
        self.beginRemoveRows(QtCore.QModelIndex(), 0, self.rowCount()-1)
        self._testmodel.clear()
        self.endRemoveRows()

    def stimulusList(self):
        """See :meth:`ProcotolModel<sparkle.run.protocol_model.ProtocolTabelModel.allTests>`"""
        return self._testmodel.allTests()

    def verify(self, windowSize=None):
        """See :meth:`ProcotolModel<sparkle.run.protocol_model.ProtocolTabelModel.verify>`"""
        return self._testmodel.verify(windowSize)

class ProtocolView(AbstractDragView, QtGui.QTableView):
    def __init__(self,parent=None):
        super(ProtocolView, self).__init__()

        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.horizontalHeader().setMovable(True)

    def paintEvent(self, event):
        """Adds cursor line for view if drag active.  Passes event to superclass
        see :qtdoc:`qtdocs<qabstractscrollarea.paintEvent>`"""
        super(ProtocolView, self).paintEvent(event)

        if self.dragline is not None:
            pen = QtGui.QPen(QtCore.Qt.blue)
            painter = QtGui.QPainter(self.viewport())
            painter.setPen(pen)
            painter.drawLine(self.dragline)

    def dropped(self, item, event):
        """Adds the dropped test *item* into the protocol list.

        Re-implemented from :meth:`AbstractDragView<sparkle.gui.abstract_drag_view.AbstractDragView.dropped>`
        """
        location = self.rowAt(event.pos().y())

        if isinstance(item, StimFactory):
            factory = item
            # create new stimulus then!
            stim = factory.create()
            if stim is not None:
                self.model().insertTest(stim, location)
        elif event.source() == self:
            self.model().insertTest(item, location)

    def grabImage(self, index):
        """Returns an image of the test row.

        Re-implemented from :meth:`AbstractDragView<sparkle.gui.abstract_drag_view.AbstractDragView.grabImage>`
        """
        # grab an image of the cell we are moving
        # assume all rows same height
        row_height = self.rowHeight(0)
        # -5 because it's a little off
        y = (row_height*index.row()) + row_height - 5
        x = self.width()
        rect = QtCore.QRect(5,y,x,row_height)
        pixmap = QtGui.QPixmap()
        pixmap = pixmap.grabWidget(self, rect)
        return pixmap

    def cursor(self, pos):
        """Returns a line at the nearest row split between tests.

        Re-implemented from :meth:`AbstractDragView<sparkle.gui.abstract_drag_view.AbstractDragView.cursor>`
        """
        row = self.indexAt(pos).row()
        if row == -1:
            row = self.model().rowCount()
        row_height = self.rowHeight(0)
        y = row_height*row
        x = self.width()
        return QtCore.QLine(0,y,x,y)

    def mousePressEvent(self, event):
        """Launches edit of cell if first column clicked, otherwise passes to super class"""
        index = self.indexAt(event.pos())
        if index.isValid():
            if index.column() == 0:
                self.edit(index, QtGui.QAbstractItemView.DoubleClicked, event)
            else:
                super(ProtocolView, self).mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Creates and shows editor for stimulus (test) selected"""
        if event.button() == QtCore.Qt.LeftButton:
            index = self.indexAt(event.pos())
            if index.isValid():
                selected = self.model().data(index, QtCore.Qt.UserRole)
                self.stimEditor = selected.showEditor()
                self.stimEditor.show()

    def indexXY(self, index):
        """Coordinates for the test row at *index*

        Re-implemented from :meth:`AbstractDragView<sparkle.gui.abstract_drag_view.AbstractDragView.indexXY>`
        """
        # just want the top left of row selected
        row = index.row()
        if row == -1:
            row = self.model().rowCount()
        y = self.rowHeight(0)*row
        return 0, y


if __name__ == '__main__': # pragma: no cover
    
    import sys, os
    from sparkle.stim.stimulus_model import StimulusModel
    from sparkle.stim.types.stimuli_classes import *
    app = QtGui.QApplication(sys.argv)

    tone0 = PureTone()
    tone0.setDuration(0.02)
    tone1 = PureTone()
    tone1.setDuration(0.040)
    tone2 = PureTone()
    tone2.setDuration(0.010)

    tone3 = PureTone()
    tone3.setDuration(0.03)
    tone4 = PureTone()
    tone4.setDuration(0.030)
    tone5 = PureTone()
    tone5.setDuration(0.030)

    vocal0 = Vocalization()
    test_file = os.path.join(os.path.expanduser('~'),r'Dropbox\daqstuff\M1_FD024\M1_FD024_syl_12.wav')
    vocal0.setFile(test_file)

    silence0 = Silence()
    silence0.setDuration(0.025)

    stim0 = StimulusModel()
    stim1 = StimulusModel()
    stim0.insertComponent(tone2)
    stim1.insertComponent(tone1)
    # stim.insertComponent(tone0)

    # stim.insertComponent(tone4, (1,0))
    stim1.insertComponent(tone5, 1,0)
    stim0.insertComponent(vocal0, 1,0)

    # stim.insertComponent(tone3, (2,0))
    # stim.insertComponent(silence0, (2,0))

    stim0.setLoopCount(3)
    stim0.setStimType('Custom')
    stim1.setStimType('Custom')

    tableView = ProtocolView()
    tableView.show()
    tableView.resize(400,400)

    model = QProtocolTabelModel(ProtocolTabelModel())
    model.insertTest(stim0,0)
    model.insertTest(stim1,0)

    tableView.setModel(model)

    sys.exit(app.exec_())
