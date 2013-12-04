import sip
sip.setapi('QVariant', 2)
sip.setapi('QString', 2)

import cPickle, pickle

from PyQt4 import QtGui, QtCore

from spikeylab.stim.component_label import ComponentTemplateLabel
ROW_HEIGHT = 100
ROW_SPACE = 25

PIXELS_PER_MS = 5
GRID_MS = 25

#Enums
BUILDMODE = 0
AUTOPARAMMODE = 1

class StimulusView(QtGui.QAbstractItemView):
    """View for building/editing stimulus components"""
    hashIsDirty = False
    _rects = [[]]
    _height = ROW_HEIGHT
    def __init__(self, parent=None):
        super(StimulusView, self).__init__(parent)
        self.horizontalScrollBar().setRange(0, 0)
        self.verticalScrollBar().setRange(0, 0)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.dragline = None

        self.setItemDelegate(ComponentDelegate())
        self.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

        self.mode = BUILDMODE

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

        self._rects = [[None] * self.model().columnCountForRow(x) for x in range(self.model().rowCount())]
        x, y = 0, 0
        for row in range(self.model().rowCount(self.rootIndex())):
            y = row*ROW_HEIGHT + row*ROW_SPACE
            x = 0
            for col in range(self.model().columnCountForRow(row)):
                index = self.model().index(row, col, self.rootIndex())
                duration = self.model().data(index, QtCore.Qt.SizeHintRole)
                width = duration * PIXELS_PER_MS * 1000
                if width is not None:
                    self._rects[row][col] = QtCore.QRect(x,y, width, ROW_HEIGHT)
                    x += width

        self._height = y+ROW_HEIGHT

    def splitAt(self, point):
        wx = point.x() + self.horizontalScrollBar().value()
        wy = point.y() + self.verticalScrollBar().value()

        row = wy/(ROW_HEIGHT + ROW_SPACE)
        if row > self.model().rowCount(self.rootIndex()) - 1:
            row = self.model().rowCount(self.rootIndex()) - 1
        for col in range(self.model().columnCountForRow(row)):
            if self._rects[row][col].contains(wx, wy):
                return (row, col)
        return row, self.model().columnCountForRow(row)

    def isIndexHidden(self, index):
        return False

    def visualRect(self, index):
        if len(self._rects[index.row()]) -1 < index.column() or index.row() == -1:
            #Er, so I don't know why this was getting called with index -1
            return QtCore.QRect()
    
        return self.visualRectRC(index.row(),index.column())

    def visualRectRC(self, row, column):
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
        super(StimulusView, self).rowsInserted(parent, start, end)

    def rowsAboutToBeRemoved(self, parent, start, end):
        self.hashIsDirty = True
        super(StimulusView, self).rowsAboutToBeRemoved(parent, start, end)

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

    def paintEvent(self, event):
        selections = self.selectionModel()
        option = self.viewOptions()
        state = option.state

        if self.parentWidget() is not None:
            background = self.parentWidget().palette().color(1)
        else:
            background = option.palette.base()

        foreground = QtGui.QPen(option.palette.color(QtGui.QPalette.WindowText))
        textPen = QtGui.QPen(option.palette.color(QtGui.QPalette.Text))
        highlightedPen = QtGui.QPen(option.palette.color(QtGui.QPalette.HighlightedText))

        painter = QtGui.QPainter(self.viewport())
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        self.calculateRects()

        viewrect = event.rect()
        painter.fillRect(viewrect, background)
        painter.setPen(foreground)  

        # draw grid lines
        nlines = (viewrect.width()/PIXELS_PER_MS)/GRID_MS
        y0 = viewrect.y()
        y1 = viewrect.y()+viewrect.height()
        for iline in range(nlines):
            x = iline * GRID_MS * PIXELS_PER_MS
            painter.drawLine(x, y0, x, y1)

        # actual painting of widget?
        for row in range(self.model().rowCount(self.rootIndex())):
            for col in range(self.model().columnCountForRow(row)):
                index = self.model().index(row, col, self.rootIndex())
                component = self.model().data(index, QtCore.Qt.UserRole)
                if component is not None:
                    option = self.viewOptions()
                    option.rect = self.visualRectRC(row, col)
                    self.itemDelegate().paint(painter, option, index)

        # highlight selected components
        region = self.visualRegionForSelection(self.selectionModel().selection())
        
        painter.save()
        painter.setClipRegion(region)
        painter.setOpacity(0.5)
        # painter.fillRect(viewrect, option.palette.highlight())
        painter.fillRect(viewrect, QtCore.Qt.blue)
        painter.restore()


        if self.dragline is not None:
            pen = QtGui.QPen(QtCore.Qt.red)
            painter.setPen(pen)
            painter.drawLine(self.dragline)

    def moveCursor(self, cursorAction, modifiers):
        # print "I done care about cursors!"
        return QtCore.QModelIndex()

    def mousePressEvent(self, event):
        if self.mode == BUILDMODE:
            if event.button() == QtCore.Qt.LeftButton:
                index = self.indexAt(event.pos())
                if not index.isValid():
                    return
                selected = self.model().data(index,QtCore.Qt.UserRole)

                mimeData = QtCore.QMimeData()
                mimeData.setData("application/x-component", selected.serialize())

                drag = QtGui.QDrag(self)
                drag.setMimeData(mimeData)

                # grab an image of the cell  we are moving
                rect = self._rects[index.row()][index.column()]
                pixmap = QtGui.QPixmap()
                pixmap = pixmap.grabWidget(self, rect)

                # below makes the pixmap half transparent
                painter = QtGui.QPainter(pixmap)
                painter.setCompositionMode(painter.CompositionMode_DestinationIn)
                painter.fillRect(pixmap.rect(), QtGui.QColor(0, 0, 0, 127))
                painter.end()
                
                drag.setPixmap(pixmap)

                drag.setHotSpot(QtCore.QPoint(pixmap.width()/2, pixmap.height()/2))
                drag.setPixmap(pixmap)

                # if result: # == QtCore.Qt.MoveAction:
                    # self.model().removeRow(index.row())
                self.model().removeComponent((index.row(), index.column()))
                self.hashIsDirty = True
                result = drag.start(QtCore.Qt.MoveAction)

            elif event.button() == QtCore.Qt.RightButton:
                index = self.indexAt(event.pos())
                self.edit(index)
                # super(StimulusView, self).mousePressEvent(event)
        else:
            # select and de-select components
            # super(StimulusView, self).mousePressEvent(event)
            index = self.indexAt(event.pos())
            if not index.isValid():
                return
            self.selectionModel().select(index, QtGui.QItemSelectionModel.Toggle)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-component"):
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-component"):
            #find the nearest row break to cursor
            # assume all rows same height

            index = self.splitAt(event.pos())
            if len(self._rects[index[0]])-1 < index[1]:
                if index[1] == 0:
                    # empty row
                    x = 0
                else:
                    rect = self._rects[index[0]][index[1]-1]
                    x = rect.x() + rect.width()
            else:
                rect = self._rects[index[0]][index[1]]
                x = rect.x()

            y0 = index[0]*(ROW_HEIGHT + ROW_SPACE)
            y1 = y0 + ROW_HEIGHT

            self.dragline = QtCore.QLine(x,y0,x,y1)          
            self.viewport().update()

            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):

        self.dragline = None
        data = event.mimeData()
        stream = data.retrieveData("application/x-component",
            QtCore.QVariant.ByteArray)
        component = cPickle.loads(str(stream))

        location = self.splitAt(event.pos())

        self.model().insertComponent(component, location)

        if isinstance(event.source(), ComponentTemplateLabel):
            index = self.model().index(location[0], location[1])
            self.edit(index)

        self.hashIsDirty = True
        self.viewport().update()

        event.accept()

    def sizeHint(self):
        return QtCore.QSize(self.width(), self._height)

    def setMode(self, mode):
        self.mode = mode
        if mode == BUILDMODE:
            self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
            self.setSelectionModel(QtGui.QItemSelectionModel(self.model()))
        else:
            self.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)

    def selectionChanged(self, selected, deselected):
        # print 'selection changed', selected, deselected
        super(StimulusView, self).selectionChanged(selected, deselected)

    def visualRegionForSelection(self, selection):
        region = QtGui.QRegion()
        for index in selection.indexes():
            region = region.united(self._rects[index.row()][index.column()])

        return region

class ComponentDelegate(QtGui.QStyledItemDelegate):

    def paint(self, painter, option, index):
        component = index.data(QtCore.Qt.UserRole)
        # component = cPickle.loads(str(component.toString()))

        painter.drawRect(option.rect)

        component.paint(painter, option.rect, option.palette)

    def sizeHint(self, option, index):
        # calculate size by data component
        component = index.data()
        width = self.component.duration() * PIXELS_PER_MS*1000
        return QtCore.QSize(width, 50)

    def createEditor(self, parent, option, index):
        # bring up separate window for component parameters
        component = index.data(QtCore.Qt.UserRole)
        # component = cPickle.loads(str(component.toString()))

        if component is not None:
            editor = component.showEditor()
        else:
            print 'delegate data type', type(component)
            raise Exception('UnknownDelegateType')

        return editor


    def setModelData(self, editor, model, index):
        """Saves the input from the editor widget to the model component"""
        editor.saveToObject()
        # need to save over component object in stimulus model
        model.setData(index, editor.component())

    def updateEditorGeometry(self, editor, option, index):
        # center the widget
        qr = editor.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)

        editor.move(qr.topLeft())

    def eventFilter(self, editor, event):
        if event.type() == QtCore.QEvent.FocusIn:
            editor.setContentFocus()
            return True

        return super(ComponentDelegate, self).eventFilter(editor, event)

if __name__ == "__main__":
    import sys
    from spikeylab.stim.stimulusmodel import *
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

    vocal0 = Vocalization()
    vocal0.setFile(r'C:\Users\amy.boyle\Dropbox\daqstuff\M1_FD024\M1_FD024_syl_12.wav')
    # vocal0.setFile(r'C:\Users\Leeloo\Dropbox\daqstuff\M1_FD024\M1_FD024_syl_12.wav')

    silence0 = Silence()
    silence0.setDuration(0.025)

    stim = StimulusModel()
    stim.insertComponent(tone2)
    stim.insertComponent(tone1)
    stim.insertComponent(tone0)

    stim.insertComponent(tone4, (1,0))
    stim.insertComponent(tone5, (1,0))
    stim.insertComponent(vocal0, (1,0))

    stim.insertComponent(tone3, (2,0))
    stim.insertComponent(silence0, (2,0))

    viewer = StimulusView()
    
    viewer.setModel(stim)
    viewer.resize(500,400)
    viewer.show()
    app.exec_()