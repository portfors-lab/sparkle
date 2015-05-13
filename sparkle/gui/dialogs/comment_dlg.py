from comment_dlg_form import Ui_CellCommentDialog
from sparkle.QtWrapper import QtGui


class CellCommentDialog(QtGui.QDialog):
    """Dialog for collecting user comments per protocol run"""
    def __init__(self, cellid=0):
        super(CellCommentDialog, self).__init__()
        self.ui = Ui_CellCommentDialog()
        self.ui.setupUi(self)

        self.setWindowTitle("Cell Comment")
        self.ui.cellidLbl.setNum(cellid)

    def comment(self):
        """Get the comment enters in this widget

        :returns: str -- user entered comment
        """
        return self.ui.commentTxtedt.toPlainText()

    def setComment(self, msg):
        """Sets the widget text to *msg*

        :param msg: overwrites any existing text with *msg*
        :type msg: str
        """
        self.ui.commentTxtedt.setPlainText(msg)
        # move text cursor to end
        self.ui.commentTxtedt.moveCursor(QtGui.QTextCursor.End)
