import sip
sip.setapi('QVariant', 2)
sip.setapi('QString', 2)

import cPickle

from PyQt4 import QtGui, QtCore

from spikeylab.main.drag_label import FactoryLabel
from spikeylab.stim.stimulusmodel import StimulusModel
from spikeylab.main.abstract_drag_view import AbstractDragView


class ProtocolTabelModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.test_order = []
        self.tests = {}
        self.headers = ['Test type', 'Reps', 'Length', 'Total', 'Generation rate']
        self.setSupportedDragActions(QtCore.Qt.MoveAction)

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
        if index.column() == 2:
            return QtCore.Qt.ItemIsEnabled
        else:
            return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def setData(self, index, value, role):
        print 'setting data!'
        if role == QtCore.Qt.EditRole:
            stimid = self.test_order[index.row()]
            test = self.tests[stimid]
            col = index.column()
            if col == 0:
                test.set_name(value)
            elif col == 1:
                test.set_reps(value)
            elif col == 2:
                test.set_note(value)

            self.editCompleted.emit(value)

    def removeItem(self, index):
        self.removeTest(index.row())
        
    def insertItem(self, index, item):
        self.insertTest(item, index.row())

    def removeTest(self, position):
        print 'remove index', position
        self.beginRemoveRows(QtCore.QModelIndex(), position, position)
        self.test_order.pop(position)
        self.endRemoveRows()

    def insertTest(self, testid, position):
        """Re-inserts exisiting stimulus into order list"""
        print 'insert position', position
        if position == -1:
            position = self.rowCount()
        self.beginInsertRows(QtCore.QModelIndex(), position, position)
        self.test_order.insert(position, testid)
        self.endInsertRows()

    def insertNewTest(self, stim, position):
        """Creates a new Stimulus Model and opens it's appropriate editor"""

        self.beginInsertRows(QtCore.QModelIndex(), position, position)

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

        if isinstance(event.source(), FactoryLabel):
            factory = item
            # create new stimulus then!
            stim = StimulusModel()
            stim.setEditor(factory.editor())
            self.model().insertNewTest(stim, location)
        else:
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

    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            index = self.indexAt(event.pos())
            selected = self.model().data(index, QtCore.Qt.UserRole)
            self.stim_editor = selected.showEditor()
            self.stim_editor.show()

            # self.edit(index)
            print 'modalness', self.stim_editor.isModal()



if __name__ == '__main__':
    
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

