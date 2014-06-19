from PyQt4 import QtGui, QtCore
from commentform import Ui_CellCommentDialog

class CellCommentDialog(QtGui.QDialog):
    def __init__(self, cellid=0):
        QtGui.QDialog.__init__(self, None)
        self.ui = Ui_CellCommentDialog()
        self.ui.setupUi(self)

        self.setWindowTitle("Cell Comment")
        self.ui.cellidLbl.setNum(cellid)

    def comment(self):
        return self.ui.commentTxtedt.toPlainText()