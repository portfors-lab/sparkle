from sparkle.QtWrapper import QtCore, QtGui

class LoadFrame(QtGui.QFrame):
  """Just a plain frame to display to the User when you want their patience to 
  wait for something

    text : (str) message to display
    x : (int) center x coord
    y : (int) center y coord
  """
  def __init__(self, text="Loading", x=None, y=None):
    super(LoadFrame, self).__init__()

    layout = QtGui.QHBoxLayout()

    font = QtGui.QFont()
    font.setPointSize(48) 
    self.setFont(font)

    layout.addWidget(QtGui.QLabel(text))
    # can't stop the animation from freezing :(
    # even when the blocking process is in a 
    # different thread.

    # self.dots = QtGui.QLabel("")
    # layout.addWidget(self.dots)
    
    # progressBar = QtGui.QProgressBar()
    # progressBar.setRange(0,0)
    # layout.addWidget(progressBar)

    self.setLayout(layout)
    # self.timer = QtCore.QTimer(self)
    # self.timer.timeout.connect(self.animateDots)
    # self.timer.start(600)

    self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
    self.setFrameStyle(QtGui.QFrame.Raised | QtGui.QFrame.Box)

    self.show()
    if x is not None and y is not None:
      # center this widget of x,y
      self.setGeometry(x - (self.width()/2), y - (self.height()/2), self.width(), self.height())

  def animateDots(self):
    # update number of dots displayed
    ndots = (len(self.dots.text()) + 1) % 4
    self.dots.setText('.'*ndots)

if __name__ == '__main__':
    app = QtGui.QApplication([])
    lf = LoadFrame()
    lf.show()
    app.exec_()
