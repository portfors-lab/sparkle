import os

from sparkle.QtWrapper import QtCore, QtGui


class TrashWidget(QtGui.QPushButton):
    """Widget which serves as a drop location to remove items from a model/view"""
    itemTrashed = QtCore.Signal()
    """Signal_ sent when an item has dropped over this widget

    .. _Signal: http://pyqt.sourceforge.net/Docs/sparkle.QtWrapper/new_style_signals_slots.html#PyQt4.QtCore.Signal
    """
    def __init__(self,parent=None):
        super(TrashWidget, self).__init__(parent)

        thisfolder = os.path.dirname(os.path.realpath(__file__))
        self.trashIcon = QtGui.QIcon(os.path.join(thisfolder,'trash.png'))
        self.setFlat(True)
        self.setIcon(self.trashIcon)
        self.setIconSize(QtCore.QSize(25,25))
        self.setAcceptDrops(True)
        self.setToolTip("Drag here to delete")

        self._underMouse = False

    def dragEnterEvent(self, event):
        """Changes apperance of button when a dragged mouse cursor is over it"""
        self.setFlat(False)
        event.accept()

    def dragLeaveEvent(self, event):
        """Changes apperance of button when a dragged mouse cursor leaves it"""
        self.setFlat(True)
        event.accept()

    def dragMoveEvent(self, event):
        """This needs to be allowed"""
        event.accept()

    def leaveEvent(self, event):
        """Sets button image back to normal after a drop"""
        self.setFlat(True)
        event.accept()

    def dropEvent(self, event):
        """Emits the itemTrashed signal, data contained in drag 
        operation left to be garbage collected"""
        super(TrashWidget, self).dropEvent(event)
        self.itemTrashed.emit()

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.ChildRemoved and self.underMouse():
            return True
        else:
            return super(type(self.parent()), self.parent()).eventFilter(source, event)
