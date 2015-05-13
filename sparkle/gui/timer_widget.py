import time

from sparkle.QtWrapper import QtCore, QtGui


class TimerWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(TimerWidget, self).__init__(parent)

        layout = QtGui.QVBoxLayout()

        title = QtGui.QLabel("Timer")
        title.setAlignment(QtCore.Qt.AlignHCenter)
        layout.addWidget(title)

        self.theTime = QtGui.QLabel("00:00.0")
        self.theTime.setAlignment(QtCore.Qt.AlignHCenter)
        layout.addWidget(self.theTime)

        self.startBtn = QtGui.QPushButton("Start")
        self.startBtn.clicked.connect(self.startTimer)
        self.stopBtn = QtGui.QPushButton("Stop")
        self.stopBtn.clicked.connect(self.stopTimer)
        self.stopBtn.setEnabled(False)

        btnLayout = QtGui.QHBoxLayout()
        btnLayout.addWidget(self.startBtn)
        btnLayout.addWidget(self.stopBtn)

        layout.addLayout(btnLayout)
        self.setLayout(layout)

        # use a timer object to update the timer text, not to be trusted for 
        # recording the actual time, though
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateTime)

        self.addedTime = 0

    def startTimer(self, event):

        self.start_time = time.time()
        self.timer.start(100)
        self.startBtn.setEnabled(False)
        self.stopBtn.setEnabled(True)
        self.stopBtn.setText("Stop")

        self.stopBtn.clicked.disconnect()
        self.stopBtn.clicked.connect(self.stopTimer)

    def stopTimer(self, event):
        now = time.time()
        elapsed = now - self.start_time
        self.addedTime = elapsed
        self.timer.stop()

        self.startBtn.setEnabled(True)
        self.stopBtn.setText("Reset")
        self.stopBtn.clicked.disconnect()
        self.stopBtn.clicked.connect(self.resetTimer)

    def resetTimer(self):
        self.addedTime = 0
        self.theTime.setText("00:00.0")

    def updateTime(self):

        now = time.time()
        elapsed = now - self.start_time + self.addedTime

        self.theTime.setText("{:02d}:{:04.1f}".format(int(elapsed)/60, elapsed % 60))

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
        
    super_rad_timer = TimerWidget()

    super_rad_timer.resize(400, 200)
    super_rad_timer.show()

    sys.exit(app.exec_())
