from sparkle.QtWrapper import QtCore, QtGui


class OrderDialog(QtGui.QDialog):
    def __init__(self, items):
        super(OrderDialog, self).__init__()

        layout = QtGui.QVBoxLayout()
        self.orderlist = QtGui.QListWidget()
        self.orderlist.addItems(items)
        self.orderlist.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.orderlist.setMinimumWidth(self.orderlist.sizeHintForColumn(0))
        layout.addWidget(self.orderlist)
        okBtn = QtGui.QPushButton('OK')
        okBtn.clicked.connect(self.accept)
        layout.addWidget(okBtn)
        self.setLayout(layout)
        self.okBtn = okBtn

    def order(self):
        allitems  = [str(self.orderlist.item(i).text()) for i in range(self.orderlist.count())]
        return allitems
