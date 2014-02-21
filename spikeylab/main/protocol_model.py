import spikeylab

import cPickle

from PyQt4 import QtGui, QtCore

# from spikeylab.main.drag_label import DragLabel
from spikeylab.stim.factory import StimFactory
from spikeylab.stim.stimulusmodel import StimulusModel
from spikeylab.main.abstract_drag_view import AbstractDragView


class ProtocolTabelModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.test_order = []
        self.tests = {}
        self.headers = ['Test type', 'Reps', 'Length', 'Total', 'Generation rate']
        self.setSupportedDragActions(QtCore.Qt.MoveAction)
        self.caldb = None
        self.calv = None
        self.calibration_vector = None
        self.calibration_frequencies = None

    def setReferenceVoltage(self, caldb, calv):
        self.caldb = caldb
        self.calv = calv
        for test in self.tests.values():
            test.setReferenceVoltage(caldb, calv)

    def setCalibration(self, db_boost_array, frequencies):
        self.calibration_vector = db_boost_array
        self.calibration_frequencies = frequencies
        for test in self.tests.values():
            test.setCalibration(db_boost_array, frequencies)

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.headers[section]
                        
    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.test_order)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 5

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            stimid = self.test_order[index.row()]
            test = self.tests[stimid]
            col = index.column()
            if col == 0:
                item = test.stimType()
            elif col == 1:
                item = test.repCount()
            elif col == 2:
                item = test.traceCount()
            elif col == 3:
                item = test.traceCount()*test.loopCount()*test.repCount()
            elif col ==4:
                item = test.samplerate()

            return item
        elif role == QtCore.Qt.UserRole:  #return the whole python object
            stimid = self.test_order[index.row()]
            test = self.tests[stimid]
            return test
        elif role == QtCore.Qt.UserRole+1:  #return the whole python object
            stimid = self.test_order[index.row()]
            return stimid

    def flags(self, index):
        if index.column() == 1:
            return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        else:
            return QtCore.Qt.ItemIsEnabled

    def setData(self, index, value, role):
        if role == QtCore.Qt.EditRole:
            if index.column() == 1:
                stimid = self.test_order[index.row()]
                test = self.tests[stimid]
                test.setRepCount(value)

    def removeItem(self, index):
        self.removeTest(index.row())

    def insertItem(self, index, item):
        self.insertTest(item, index.row())

    def removeTest(self, position):
        """Removes a test from the order list, but not keeps a reference"""
        self.beginRemoveRows(QtCore.QModelIndex(), position, position)
        self.test_order.pop(position)
        self.endRemoveRows()

    def insertTest(self, testid, position):
        """Re-inserts exisiting stimulus into order list"""
        if position == -1:
            position = self.rowCount()
        self.beginInsertRows(QtCore.QModelIndex(), position, position)
        self.test_order.insert(position, testid)
        self.endInsertRows()

    def insertNewTest(self, stim, position):
        """Creates inserts a new test into list"""
        if position == -1:
            position = self.rowCount()
        self.beginInsertRows(QtCore.QModelIndex(), position, position)
        stim.setReferenceVoltage(self.caldb, self.calv)
        stim.setCalibration(self.calibration_vector, self.calibration_frequencies)
        # cannot serialize Qt objects, so must use a proxy list
        self.test_order.insert(position, stim.stimid)
        self.tests[stim.stimid] = stim

        self.endInsertRows()
    
    def stimulusList(self):
        """Return a list of StimulusModels in correct order"""
        stimuli = []
        for testid in self.test_order:
            stimuli.append(self.tests[testid])
        return stimuli

    def verify(self, window_size=None):
        """Verify that this protocol model is valid. Return 0 if sucessful,
        a failure message otherwise"""
        if self.rowCount() == 0:
            return "Protocol must have at least one test"
        if self.caldb is None or self.calv is None:
            return "Protocol reference voltage not set"
        for testid in self.test_order:
            test = self.tests[testid]
            msg = test.verify(window_size)
            if msg:
                return msg
        return 0

class ProtocolView(AbstractDragView, QtGui.QTableView):
    def __init__(self,parent=None):
        QtGui.QTableView.__init__(self,parent)
        AbstractDragView.__init__(self)

        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

    def paintEvent(self, event):
        super(ProtocolView, self).paintEvent(event)

        if self.dragline is not None:
            pen = QtGui.QPen(QtCore.Qt.blue)
            painter = QtGui.QPainter(self.viewport())
            painter.setPen(pen)
            painter.drawLine(self.dragline)

    def dropEvent(self, event):
        item = self.dropAssist(event)
        location = self.rowAt(event.pos().y())

        if isinstance(item, StimFactory):
            factory = item
            # create new stimulus then!
            stim = StimulusModel()
            factory.init_stim(stim)
            stim.setEditor(factory.editor())
            self.model().insertNewTest(stim, location)
        elif event.source() == self:
            selected_id = item
            self.model().insertTest(selected_id, location)

        event.accept()

    def grabImage(self, index):
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
        row = self.indexAt(pos).row()
        if row == -1:
            row = self.model().rowCount()
        row_height = self.rowHeight(0)
        y = row_height*row
        x = self.width()
        return QtCore.QLine(0,y,x,y)

    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            index = self.indexAt(event.pos())
            selected = self.model().data(index, QtCore.Qt.UserRole)
            self.stim_editor = selected.showEditor()
            self.stim_editor.show()

    def indexXY(self, index):
        """Return the top left coordinates of the row for the given index"""
        row = index.row()
        if row == -1:
            row = self.model().rowCount()
        y = self.rowHeight(0)*row
        return 0, y


if __name__ == '__main__': # pragma: no cover
    
    import sys, os
    from spikeylab.stim.stimulusmodel import StimulusModel
    from spikeylab.stim.types.stimuli_classes import *
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
    stim1.insertComponent(tone5, (1,0))
    stim0.insertComponent(vocal0, (1,0))

    # stim.insertComponent(tone3, (2,0))
    # stim.insertComponent(silence0, (2,0))

    stim0.setLoopCount(3)

    tableView = ProtocolView()
    tableView.show()
    tableView.resize(400,400)

    model = ProtocolTabelModel()
    model.insertNewTest(stim0,0)
    model.insertNewTest(stim1,0)

    tableView.setModel(model)

    sys.exit(app.exec_())

