from sparkle.QtWrapper import QtCore, QtGui


class QBorder(QtGui.QFrame):
    def __init__(self, parent):
        super(QBorder, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

    def showBorder(self, show):
        if show:
            self.setStyleSheet("border: 3px solid turquoise")
            self.resize(self.parent().size())
        else:
            self.setStyleSheet("border: 0px")
