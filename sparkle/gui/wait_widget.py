from sparkle.QtWrapper import QtCore, QtGui


class WaitWidget(QtGui.QLabel):
    """Simple wiget that only contains a label "Loading..." So the user
    doesn't think the GUI has frozen."""
    def __init__(self, message= "Loading...", parent=None):
        super(WaitWidget, self).__init__(parent)

        pts = 16
        self.setText(message)
        self.setWindowModality(True)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        font = QtGui.QFont()
        font.setPointSize(pts)
        self.setFont(font)
        self.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        self.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Raised)
        self.setLineWidth(2)
        self.resize(len(message)*pts, pts+40)
