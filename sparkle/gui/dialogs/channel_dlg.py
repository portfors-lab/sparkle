from sparkle.QtWrapper import QtCore, QtGui

from sparkle.acq.daq_tasks import get_ai_chans

class ChannelDialog(QtGui.QDialog):
    def __init__(self, device_name):
        super(ChannelDialog, self).__init__()
        
        layout = QtGui.QGridLayout()
        cnames = get_ai_chans(device_name)

        layout.addWidget(QtGui.QLabel("Channels for device: "+ device_name), 0, 0)
        row = 1
        col = 0
        max_row = 16
        self.channel_switches = []
        for channel in cnames:
            channel_box = QtGui.QCheckBox(channel)
            self.channel_switches.append(channel_box)
            layout.addWidget(channel_box, row, col)
            row += 1
            if row > max_row:
                row = 1
                col +=1

        okBtn = QtGui.QPushButton("OK")
        okBtn.clicked.connect(self.accept)
        cancelBtn = QtGui.QPushButton("Cancel")
        cancelBtn.clicked.connect(self.reject)
        layout.addWidget(okBtn, max_row+1, 0)
        row += 1
        layout.addWidget(cancelBtn, max_row+1, 1)

        self.setLayout(layout)
        self.setWindowModality(QtCore.Qt.ApplicationModal)

    def getSelectedChannels(self):
        chosen_channel_names = []
        for channel in self.channel_switches:
            if channel.isChecked():
                chosen_channel_names.append(str(channel.text()))
        return chosen_channel_names

    def setSelectedChannels(self, chosen_channel_names):
        for channel in self.channel_switches:
            if channel.text() in chosen_channel_names:
                channel.setChecked(True)
            else:
                channel.setChecked(False)

if __name__ == "__main__":
    app = QtGui.QApplication([])
    picker = ChannelPicker("PCI-6259")
    picker.show()
    app.exec_()


