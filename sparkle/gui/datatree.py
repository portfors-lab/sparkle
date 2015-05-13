from sparkle.QtWrapper import QtCore, QtGui


class DataTreeItem(QtGui.QTreeWidgetItem):
    def __init__(self, parent, datakey):
        super(DataTreeItem, self).__init__(parent)
        self.setText(0, datakey)
        self.data = datakey

    def findChild(self, datakey):
        for i in range(self.childCount()):
            if str(self.child(i).text(0)) == datakey:
                return self.child(i)
        return None

    def path(self):
        parent =  self.parent()
        path = str(self.text(0))
        while parent is not None:
            if len(str(parent.text(0))) > 0:
                path = str(parent.text(0)) + '/' + path
            parent = parent.parent()
        return path

class DataTree(QtGui.QTreeWidget):
    nodeChanged = QtCore.Signal(str)

    def addData(self, data):
        self.setHeaderLabel(data.filename)
        self.data = data
        rootnode = DataTreeItem(self, '')
        self.addTopLevelItem(rootnode)
        self.build(rootnode)
        self.expandItem(rootnode)

    def build(self, node):
        # find and add children to node
        # if hasattr(node.data, 'keys'):
        datakeys = self.data.keys(str(node.path()))
        if datakeys is not None:
            datakeys = sorted(datakeys, key=lambda item: (item.partition('_')[0], int(item.rpartition('_')[-1]) if item[-1].isdigit() else float('inf')))
            # datakeys = node.data.keys()
            for dataname in datakeys:
                subnode = node.findChild(dataname)
                if subnode is None:
                    # add it if not present
                    subnode = DataTreeItem(node, dataname)
                self.build(subnode)

    def update(self):
        # go through entire tree and fill in missing nodes
        # assumes single top level item
        self.build(self.topLevelItem(0))

    def clearTree(self):
        item = self.takeTopLevelItem(0)
        del item
        self.data = None

    def selectionChanged(self, selected, deselected):
        super(DataTree, self).selectionChanged(selected, deselected)
        if len(selected.indexes()) > 0:
            self.setCurrentIndex(selected.indexes()[0])
            path = self.currentItem().path()
            self.nodeChanged.emit(path)
