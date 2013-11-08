from PyQt4 import QtGui, QtCore

from stimeditor_form import Ui_StimulusEditor

PIXELS_PER_MS = 5

class ComponentWidget(QtGui.QWidget):
    def __init__(self, component, parent=None):
        super(ComponentWidget,self).__init__(parent)
        self.component = component

        # set image according to component type
        component_name_label = QtGui.QLabel('component')
        if component.name == "puretone":
            self.setStyleSheet("background-image:url(./ducklings.jpg)")
        else:
            self.setStyleSheet("background-image:url(./ducklings.jpg)")

        vert = QtGui.QVBoxLayout()
        vert.addWidget(component_name_label)
        self.setLayout(vert)

    def sizeHint(self):
        width = self.component.duration * PIXELS_PER_MS*1000
        return QtCore.QSize(width, 50)

class ComponentDelegate(QtGui.QStyledItemDelegate):

    def paint(self, painter, option, index):
        component = index.data()
        # component.paint(painter, option.rect, option.palette, ComponentDelegate.ReadOnly)

        image = QtGui.QImage("./ducklings.jpg)")
        painter.drawImage(0,0,image)

        painter.drawRect(option.rect)

        # set text color
        painter.setPen(QPen(Qt.black))
        value = index.data(Qt.DisplayRole)
        if value.isValid():
            text = value.toString()
            painter.drawText(option.rect, Qt.AlignLeft, text)

    def sizeHint(self, option, index):
        # calculate size by data component
        component = index.data()
        width = self.component.duration() * PIXELS_PER_MS*1000
        return QtCore.QSize(width, 50)

    def createEditor(self, parent, option, index):
        # bring up separate window for component parameters
        print 'TODO: implement component editor'
        # editor = StarEditor(parent)
        # editor.editingFinished.connect(self.commitAndCloseEditor)
        # return editor

    def setEditorData(self, editor, index):
        component = index.data()
        editor.setComponent(component)

    def setModelData(self, editor, model, index):
        component = index.data()
        model.setData(index, editor.component())

    def commitAndCloseEditor(self):
        editor = self.sender()
        self.commitData.emit(editor)
        self.closeEditor.emit(editor)

class TrackWidget(QtGui.QAbstractItemView):
    def __init__(self, component_list, parent=None):


class TrackWidget1(QtGui.QListWidget):
    def __init__(self, component_list, parent=None):
        super(TrackWidget, self).__init__(parent)
        self.setDragEnabled(True)
        # self.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self.viewport().setAcceptDrops(True)

        self.set_model_components(component_list)
        self.setFlow(QtGui.QListView.LeftToRight)

    def set_model_components(self, component_list):
        for comp in component_list:
            item_widget = ComponentWidget(comp, self)
            item = QtGui.QListWidgetItem(self)
            item.setSizeHint(item_widget.sizeHint())
            self.addItem(item)
            self.setItemWidget(item, item_widget)

    def dropEvent(self, event):
        print 'drop event'
        # move, not copy, item
        if event.source() == self:
            print 'me!'
            event.accept()
        else:
            event.ignore()
            print 'someone else', event.source()

        super(TrackWidget,self).dropEvent(event)

    def mousePressEvent(self, event):

        index = self.indexAt(event.pos())
        item = self.itemAt(event.pos())
        selected = self.model().data(index,QtCore.Qt.UserRole)

        print 'index', index
        # print 'selected', selected
        super(TrackWidget,self).mousePressEvent(event)

class StimulusEditor(QtGui.QWidget):
    def __init__(self, stimulus, parent=None):
        super(StimulusEditor,self).__init__(parent)
        self.ui = Ui_StimulusEditor()
        self.ui.setupUi(self)

        # self.tracks = [self.ui.track0]
        self.tracks = []
        # set up tracks as lists that you can drag and drop with
        for itrack in range(0,len(stimulus.segments)):
            track = TrackWidget(stimulus.segments[itrack])
            self.ui.track_layout.addWidget(track)
            self.tracks.append(track)


if __name__ == "__main__":
    import sys
    from stimulusmodel import *
    app  = QtGui.QApplication(sys.argv)

    tone0 = PureTone()
    tone0.setDuration(0.02)
    tone1 = PureTone()
    tone1.setDuration(0.040)
    tone2 = PureTone()
    tone2.setDuration(0.010)

    tone3 = PureTone()
    tone3.setDuration(0.03)
    tone4 = PureTone()
    tone4.setDuration(0.030)
    tone5 = PureTone()
    tone5.setDuration(0.030)

    stim = StimulusModel()
    stim.add_component(tone2)
    stim.add_component(tone1)
    stim.add_component(tone0)

    stim.add_component(tone4, (1,0))
    stim.add_component(tone5, (1,0))
    stim.add_component(tone3, (1,0))

    main = StimulusEditor(stim)
    main.show()
    app.exec_()