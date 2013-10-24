import sys
import cPickle
import pickle


from PyQt4 import QtGui, QtCore

class ProtocolTabelModel(QtCore.QAbstractTableModel):

    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.tests = data
        self.headers = ['Test name', 'Reps', 'Note']
        self.setSupportedDragActions(QtCore.Qt.MoveAction)

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.headers[section]
                        
    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.tests)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 3

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            test = self.tests[index.row()]
            col = index.column()
            if col == 0:
                item = test.name
            elif col == 1:
                item = test.reps
            elif col == 2:
                item = test.note

            return item
        elif role == QtCore.Qt.UserRole:  #return the whole python object
            test = self.tests[index.row()]
            return test

    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def setData(self, index, value, role):
        if role == QtCore.Qt.EditRole:
            test = self.tests[index.row()]
            col = index.column()
            if col == 0:
                test.set_name(value)
            elif col == 1:
                test.set_reps(value)
            elif col == 2:
                test.set_note(value)

            self.editCompleted.emit(value)

    def removeTest(self, index):
        self.tests.pop(index)

    def insertTest(self, test, index):
        self.tests.insert(index, test)
        self.layoutChanged.emit()
        

class ProtocolView(QtGui.QTableView):
    def __init__(self,parent=None):
        QtGui.QTableView.__init__(self,parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        # self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-person"):
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-person"):
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        data = event.mimeData()
        bstream = data.retrieveData("application/x-person",
            QtCore.QVariant.ByteArray)
        selected = pickle.loads(bstream.toByteArray())
        self.model().insertTest(selected, 0)
        event.accept()

    def mousePressEvent(self, event):

        index = self.indexAt(event.pos())
        selected = self.model().data(index,QtCore.Qt.UserRole)

        # print self.model().tests
        ## convert to  a bytestream
        bstream = cPickle.dumps(selected)
        mimeData = QtCore.QMimeData()
        mimeData.setData("application/x-person", bstream)

        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)

        # example 1 - the object itself

        # pixmap = QtGui.QPixmap()
        # pixmap = pixmap.grabWidget(self, self.rectForIndex(index))

        # example 2 -  a plain pixmap
        pixmap = QtGui.QPixmap(100, self.height()/2)
        pixmap.fill(QtGui.QColor("orange"))
        drag.setPixmap(pixmap)

        drag.setHotSpot(QtCore.QPoint(pixmap.width()/2, pixmap.height()/2))
        drag.setPixmap(pixmap)

        # if result: # == QtCore.Qt.MoveAction:
            # self.model().removeRow(index.row())
        self.model().removeTest(index.row())
        result = drag.start(QtCore.Qt.MoveAction)

        # super(ProtocolView, self).mousePressEvent(event)

class DummyTest():
    def __init__(self, name, reps, note):
        self.name = name
        self.reps = reps
        self.note = note
    def __repr__(self):
        return "%s\n%s\n%s"% (self.name, self.reps, self.note)


if __name__ == '__main__':
    
    app = QtGui.QApplication(sys.argv)
    app.setStyle("plastique")

    protocol = []
    for itest in range(5):
        dummy = DummyTest('test'+ str(itest), itest*2, 'nothing')
        protocol.append(dummy)

    tableView = ProtocolView()
    tableView.show()

    model = ProtocolTabelModel(protocol)

    tableView.setModel(model)

    sys.exit(app.exec_())

