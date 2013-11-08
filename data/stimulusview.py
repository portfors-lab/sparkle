import pickle
from PyQt4 import QtGui, QtCore

from audiolab.data.stimulusmodel import *


ROW_HEIGHT = 100
COLUMN_SPACE = 25

class StimulusView(QtGui.QAbstractItemView):
    hashIsDirty = False
    _rects = [[]]
    # def __init__(self, parent=None):
    #     super(StimulusView, self).__init__(parent)
        # self.horizontalScrollBar().setRange(0, 0)
        # self.verticalScrollBar().setRange(0, 0)

    def setModel(self, model):
        super(StimulusView, self).setModel(model)
        # initialize nested list to appropriate size
        self._rects = [[None] * self.model().columnCountForRow(x) for x in range(self.model().rowCount())]

        self.hashIsDirty = True
        self.calculateRects()

    def indexAt(self, point):
        # Transform the view coordinates into contents widget coordinates.
        wx = point.x() + self.horizontalScrollBar().value()
        wy = point.y() + self.verticalScrollBar().value()
        self.calculateRects()
        # naive search
        for row in range(self.model().rowCount(self.rootIndex())):
            for col in range(self.model().columnCountForRow(row)):
                if self._rects[row][col].contains(wx, wy):
                    return self.model().index(row, col, self.rootIndex())

        return QtCore.QModelIndex()

    def calculateRects(self):
        if not self.hashIsDirty:
            return

        x, y = 0, 0
        for row in range(self.model().rowCount(self.rootIndex())):
            y += row*ROW_HEIGHT + COLUMN_SPACE
            x = 0
            for col in range(self.model().columnCountForRow(row)):
                index = self.model().index(row, col, self.rootIndex())
                width = self.model().data(index, QtCore.Qt.SizeHintRole)
                if width is not None:
                    self._rects[row][col] = QtCore.QRect(x,y, width, ROW_HEIGHT)
                    x += width

    def isIndexHidden(self, index):
        return False

    def visualRect(self, index):
    #     if len(self._rects[index.row()]) -1 < index.column():
    #         return QtCore.QRect()
        return self.visualRectRC(index.row(),index.column())

    def visualRectRC(self, row, column):
        if len(self._rects)-1 < row or len(self._rects[row])-1 < column:
            print 'index out of boundsssss!!!'
            return QtCore.QRect()
        rect = self._rects[row][column]
        if rect.isValid():
            return QtCore.QRect(rect.x() - self.horizontalScrollBar().value(),
                         rect.y() - self.verticalScrollBar().value(),
                         rect.width(), rect.height())
        else:
            return rect

    def dataChanged(self, topleft, bottomright):
        self.hashIsDirty = True
        super(StimulusView, self).dataChanged(topleft, bottomright)

    def rowsInserted(self, parent, start, end):
        self.hashIsDirty = True
        super(PieView, self).rowsInserted(parent, start, end)

    def rowsAboutToBeRemoved(self, parent, start, end):
        self.hashIsDirty = True
        super(PieView, self).rowsAboutToBeRemoved(parent, start, end)

    def verticalOffset(self):
        return self.verticalScrollBar().value()

    def horizontalOffset(self):
        return self.horizontalScrollBar().value()

    def scrollTo(self, index, ScrollHint):
        # copied verbatim from chart example
        area = self.viewport().rect()
        rect = self.visualRect(index)

        if rect.left() < area.left():
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() + rect.left() - area.left())
        elif rect.right() > area.right():
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() + min(
                    rect.right() - area.right(), rect.left() - area.left()))

        if rect.top() < area.top():
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() + rect.top() - area.top())
        elif rect.bottom() > area.bottom():
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() + min(
                    rect.bottom() - area.bottom(), rect.top() - area.top()))

    def scrollContentsBy(self, dx, dy):
        # self.scrollDirtyRegion(dx,dy) #in web example
        self.viewport().scroll(dx, dy)

    def setSelection(self, rect, command):
        # I don't want RB selection -- do I need this?
    
        # translate from viewport coordinates to widget coordinates?
        contentsRect = rect.translated(self.horizontalScrollBar().value(),
                self.verticalScrollBar().value()).normalized()

        self.calculateRects()

        rows = self.model().rowCount(self.rootIndex())
        columns = self.model().columnCount(self.rootIndex())
        indexes = []

    def paintEvent(self, event):
        selections = self.selectionModel()
        option = self.viewOptions()
        state = option.state

        background = option.palette.base()
        foreground = QtGui.QPen(option.palette.color(QtGui.QPalette.WindowText))
        textPen = QtGui.QPen(option.palette.color(QtGui.QPalette.Text))
        highlightedPen = QtGui.QPen(option.palette.color(QtGui.QPalette.HighlightedText))

        painter = QtGui.QPainter(self.viewport())
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        painter.fillRect(event.rect(), background)
        painter.setPen(foreground)  
        painter.drawText(5,5, "Testing yo!")

        # actual painting of widget?
        for row in range(self.model().rowCount(self.rootIndex())):
            for col in range(self.model().columnCountForRow(row)):
                index = self.model().index(row, col, self.rootIndex())
                component = self.model().data(index, QtCore.Qt.UserRole)
                if component is not None:
                    option = self.viewOptions()
                    option.rect = self.visualRectRC(row, col)
                    self.itemDelegate().paint(painter, option, index)

    def moveCursor(self, cursorAction, modifiers):
        print "I done care about cursors!"
        return QtCore.QModelIndex()

class ComponentDelegate(QtGui.QStyledItemDelegate):

    def paint(self, painter, option, index):
        component = index.data()
        # component.paint(painter, option.rect, option.palette, ComponentDelegate.ReadOnly)

        image = QtGui.QImage("./ducklings.jpg)")
        painter.drawImage(0,0,image)

        painter.drawRect(option.rect)

        # set text color
        painter.setPen(QtGui.QPen(QtCore.Qt.black))
        value = index.data(QtCore.Qt.DisplayRole)
        if value.isValid():
            text = value.toString()
            # print 'location', option.rect.x(), option.rect.y(), option.rect.width(), option.rect.height()
            painter.drawText(option.rect, QtCore.Qt.AlignLeft, text)

    def sizeHint(self, option, index):
        # calculate size by data component
        component = index.data()
        width = self.component.duration() * PIXELS_PER_MS*1000
        return QtCore.QSize(width, 50)

    def createEditor(self, parent, option, index):
        # bring up separate window for component parameters
        component = index.data(QtCore.Qt.UserRole)
        component = pickle.loads(str(component.toString()))
        print parent, option, index, component

        if component is not None:

            editor = ComponentEditor(component)
            # editor.exec_()
        else:
            print 'delegate data type', type(component)
            editor = ComponentEditor(component)

        # editor = StarEditor(parent)
        # editor.editingFinished.connect(self.commitAndCloseEditor)
        return editor

    def setEditorData(self, editor, index):
        print 'Er, set editor data?'
        component = index.data(QtCore.Qt.UserRole)
        editor.setComponent(component)

    def setModelData(self, editor, model, index):
        print 'Set model Data!'
        component = index.data()
        model.setData(index, editor.component())

    def commitAndCloseEditor(self):
        print 'comit and close editor'
        editor = self.sender()
        self.commitData.emit(editor)
        self.closeEditor.emit(editor)

class ComponentEditor(QtGui.QDialog):
    editingFinished = QtCore.pyqtSignal()

    def __init__(self, component, parent = None):
        super(ComponentEditor, self).__init__(parent)

        self._component = component
        inputfield = QtGui.QLineEdit(component.__class__.__name__, self)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(inputfield)
        self.setLayout(layout)
        # self.show()

    def sizeHint(self):
        return QtCore.QSize(300,400)

    def setComponent(self, component):
        print 'Editor recieved', component
 
    def component(self):
        return self._component

if __name__ == "__main__":
    import sys
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
    stim.addComponent(tone2)
    stim.addComponent(tone1)
    stim.addComponent(tone0)

    stim.addComponent(tone4, (1,0))
    stim.addComponent(tone5, (1,0))
    stim.addComponent(tone3, (1,0))

    viewer = StimulusView()
    viewer.setItemDelegate(ComponentDelegate())
    viewer.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked)
    viewer.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
    viewer.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
    viewer.setModel(stim)
    viewer.show()
    app.exec_()