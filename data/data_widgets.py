from PyQt4 import QtGui

from stimeditor_form import Ui_StimulusEditor

PIXELS_PER_MS = 10

class ComponentWidget(QtGui.QWidget):
    def __init__(self, component, parent=None):
        super(ComponentWidget,self).__init__(parent)
        self.component = component

        # set icon
        if component.name == "puretone":
            self.setStyleSheet("background-image:url(./ducklings.jpg)")
        else:
            self.setStyleSheet("background-image:url(./ducklings.jpg)")

        width = component.duration * PIXELS_PER_MS*1000
        self.resize(width, self.height())

class ComponentDelegate(QtGui.QItemDelegate):

    def paint(self, painter, option, index):

        image = QtGui.QImage("./ducklings.jpg)")
        painter.drawImage(0,0,image)

        painter.drawRect(option.rect)

        # set text color
        painter.setPen(QPen(Qt.black))
        value = index.data(Qt.DisplayRole)
        if value.isValid():
            text = value.toString()
            painter.drawText(option.rect, Qt.AlignLeft, text)

            

class StimulusEditor(QtGui.QWidget):
    def __init__(self, stimulus, parent=None):
        super(StimulusEditor,self).__init__(parent)
        self.ui = Ui_StimulusEditor()
        self.ui.setupUi(self)

        self.tracks = [self.ui.trackView0]
        # set up tracks as lists that you can drag and drop with
        for range(1,len(stimulus.ntracks1)-1)):
            track = QtGui.QListView()
            track.setFlow(QtGui.QListView.LeftToRight)
            self.ui.track_layout.addWidget(track)

        # now populate tracks appropriately
        for range(0,len(stimulus.ntracks1)-1)):
