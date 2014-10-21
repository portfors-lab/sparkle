import sys
import os
import re
import h5py
import numpy
from PyQt4 import QtCore, QtGui

class H5TreeWidgetItem(QtGui.QTreeWidgetItem):
    def __init__(self, parent, h5node):
        QtGui.QTreeWidgetItem.__init__(self, parent)
        self.h5node = h5node
        if isinstance(h5node, h5py.File):
            self.setText(0, h5node.filename)
        else:
            self.setText(0, h5node.name.rpartition('/')[-1])

    def path(self):        
        path = str(self.data(0, QtCore.Qt.DisplayRole).toString())
        parent = self.parent()
        root = self.treeWidget().invisibleRootItem()
        while parent is not None:
            path = str(parent.data(0, QtCore.Qt.DisplayRole).toString()) + "/" + path
            parent = parent.parent()
        return str(path)

    def getAttributes(self):
        return self.h5node.attrs

        
    def getHDF5Data(self):
        if isinstance(self.h5node, h5py.Dataset):
            return self.h5node
        else:
            return None
            

class H5TreeWidget(QtGui.QTreeWidget):
    nodeChanged = QtCore.pyqtSignal(QtGui.QTreeWidgetItem)
    def __init__(self, *args):
        QtGui.QTreeWidget.__init__(self, *args)
        self.fhandles = {}
        self.roots = {}
        self.header().hide()
        
    def addH5File(self, filename):
        if not filename.startswith('/'):
            filename = os.path.abspath(filename)
        if not filename in self.fhandles.keys():
            file_handle = h5py.File(filename, 'r')
            self.fhandles[filename] = file_handle
            item = H5TreeWidgetItem(self, file_handle)
            self.addTopLevelItem(item)
            item.setText(0, QtCore.QString(filename))
            self.addTree(item, file_handle)

    def addH5Handle(self, handle):
        filename = handle.filename
        if not filename in self.fhandles.keys():
            self.fhandles[filename] = handle
            item = H5TreeWidgetItem(self, handle)
            self.addTopLevelItem(item)
            self.roots[filename] = item
            item.setText(0, filename)
            self.addTree(item, handle)
            
    def addTree(self, currentItem, node):
        if isinstance(node, h5py.Group) or isinstance(node, h5py.File):
            for child in node:
                item = H5TreeWidgetItem(currentItem, node[child])
                self.addTree(item, node[child])

    def update(self, handle):
        filename = handle.filename
        handle = self.fhandles[filename]
        top_groups = handle.keys()
        root = self.roots[filename]
        existing = [root.child(i).data(0, QtCore.Qt.DisplayRole) for i in range(root.childCount())]
        for group in top_groups:
            if group not in existing:
                item = H5TreeWidgetItem(root, handle[group])
                item.setText(0, group)
                self.addTree(item, handle[group])

    def getOpenFileName(self, path):
        """Added this little function to avoid repetition.  It returns
        the filename part of a selected HDF5 path.
        """
        for key, value in self.fhandles.items():
            if path.startswith(key):
                return key
        return None

    def selectionChanged(self, selected, deselected):
        super(H5TreeWidget, self).selectionChanged(selected, deselected)
        self.setCurrentIndex(selected.indexes()[0])
        self.nodeChanged.emit(self.currentItem())

    def closeCurrentFile(self):
        to_delete = {}
        for item in self.selectedItems():
            filename = self.getOpenFileName(item.path())
            try:
                fhandle = self.fhandles[filename]
                fhandle.close()
                del self.fhandles[filename]
            except KeyError:
                print 'File not open:', filename
            current = item
            parent = current.parent()
            while current.parent() != None:
                current = parent
                parent = current.parent()
            to_delete[current] = 1
        for item in to_delete.keys():
            index = self.indexOfTopLevelItem(item)
            self.takeTopLevelItem(index)
            del item
            
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    QtGui.qApp = app
    # mainwin = DataVizGui()
    mainwin = QtGui.QMainWindow()
    tree = H5TreeWidget(mainwin)    
    tree.addH5File('C:\\Users\\amy.boyle\\audiolab_data\\open_testing.hdf5')
    mainwin.setCentralWidget(tree)
    mainwin.show()
    app.exec_()
                

