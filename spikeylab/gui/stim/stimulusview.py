from PyQt4 import QtGui, QtCore

from spikeylab.gui.drag_label import DragLabel
from spikeylab.gui.abstract_drag_view import AbstractDragView
from spikeylab.stim.abstract_stimulus import AbstractStimulusComponent
from spikeylab.gui.stim.selectionmodel import ComponentSelectionModel

ROW_HEIGHT = 100
ROW_SPACE = 25

GRID_PIXEL_MIN = 100
GRID_PIXEL_MAX = 200

#Enums
BUILDMODE = 0
AUTOPARAMMODE = 1

class StimulusView(AbstractDragView, QtGui.QAbstractItemView):
    """View for building/editing stimulus components"""
    hashIsDirty = False
    _height = ROW_HEIGHT
    _width = 10
    _componentDefaults = {}
    componentSelected = QtCore.pyqtSignal(AbstractStimulusComponent)
    countChanged = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        QtGui.QAbstractItemView.__init__(self)
        AbstractDragView.__init__(self)

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
        self._rects = [[]]
        # these orignal settings are important
        self.pixelsPerms = 5
        self.gridms = 25

    def rowReach(self):
        """Row span in pixels

        :returns: int -- row height + space between rows
        """
        return ROW_HEIGHT + ROW_SPACE

    def setPixelScale(self, pxms):
        """Sets the zoom scale

        :param pxms: number of pixels per ms
        :type pxms: int
        """
        pxms = float(pxms)/2
        self.pixelsPerms = pxms
        if pxms*self.gridms < GRID_PIXEL_MIN:
            self.gridms = self.gridms*2
        elif pxms*self.gridms > GRID_PIXEL_MAX:
            self.gridms = self.gridms/2
        self.hashIsDirty = True
        self.viewport().update()

        return self.gridms

    def setModel(self, model):
        """Sets the QStimulusModel for this view"""
        super(StimulusView, self).setModel(model)
        self.setSelectionModel(ComponentSelectionModel(model))
        # initialize nested list to appropriate size
        self._rects = [[None] * self.model().columnCountForRow(x) for x in range(self.model().rowCount())]

        self.hashIsDirty = True
        self._calculateRects()

    def indexXY(self, index):
        """Return the top left coordinates of the item for the given index"""
        rect = self.visualRect(index)
        return rect.x(), rect.y()

    def indexAt(self, point):
        """Returns the QModelIndex of the component at the specified QPoint relative to view coordinates"""
        # Transform the view coordinates into contents widget coordinates.
        wx = point.x() + self.horizontalScrollBar().value()
        wy = point.y() + self.verticalScrollBar().value()
        self._calculateRects()
        # naive search
        for row in range(self.model().rowCount(self.rootIndex())):
            for col in range(self.model().columnCountForRow(row)):
                if self._rects[row][col].contains(wx, wy):
                    return self.model().index(row, col, self.rootIndex())

        return QtCore.QModelIndex()

    def _calculateRects(self):
        """Calculate the sizes of the different components present in this view"""
        if not self.hashIsDirty:
            return

        self._rects = [[None] * self.model().columnCountForRow(x) for x in range(self.model().rowCount())]
        x, y = 0, 0
        maxx = 0
        for row in range(self.model().rowCount(self.rootIndex())):
            y = row*ROW_HEIGHT + row*ROW_SPACE + ROW_SPACE
            x = 0
            for col in range(self.model().columnCountForRow(row)):
                index = self.model().index(row, col, self.rootIndex())
                duration = self.model().data(index, QtCore.Qt.SizeHintRole)
                width = duration * self.pixelsPerms * 1000
                if width is not None:
                    self._rects[row][col] = QtCore.QRect(x,y, width, ROW_HEIGHT)
                    x += width
                maxx = max(maxx, x)

        self._width = maxx + 10
        self._height = y+ROW_HEIGHT
        self.viewport().update()
        self.updateGeometries()
        self.hashIsDirty = False

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

    def somethingChanged(self):
        self.hashIsDirty = True

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

        self.viewport().update()

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

        self._calculateRects()

        viewrect = event.rect()
        painter.fillRect(viewrect, background)
        painter.setPen(foreground)

        fontsz = self.font().pointSize()  

        # draw grid lines
        wid = int(max(viewrect.width(), self._width))
        nlines = int((wid/self.pixelsPerms)/self.gridms)
        y0 = viewrect.y()
        y1 = viewrect.y() + viewrect.height()
        for iline in range(1, nlines + 1):
            x = (iline * self.gridms * self.pixelsPerms) - self.horizontalScrollBar().value()
            painter.drawLine(x, y0+fontsz+2, x, y1)
            painter.drawText(x-5, y0+fontsz+1, str(iline*self.gridms))

        # painting of components
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
        painter.fillRect(viewrect, QtCore.Qt.blue)
        painter.restore()

        if self.dragline is not None:
            pen = QtGui.QPen(QtCore.Qt.blue)
            pen.setWidth(3)
            painter.setPen(pen)
            painter.drawLine(self.dragline)

    def moveCursor(self, cursorAction, modifiers):
        # print "I done care about cursors!"
        return QtCore.QModelIndex()

    def mouseDoubleClickEvent(self, event):
        if self.mode == BUILDMODE:
            if event.button() == QtCore.Qt.LeftButton:
                index = self.indexAt(event.pos())
                self.edit(index)

    def grabImage(self, index):
        # grab an image of the cell  we are moving
        # rect = self._rects[index.row()][index.column()]
        rect = self.visualRect(index)
        pixmap = QtGui.QPixmap()
        pixmap = pixmap.grabWidget(self, rect)     
        return pixmap

    def mousePressEvent(self, event):
        if self.mode == BUILDMODE:
            super(StimulusView, self).mousePressEvent(event)
        else:
            # select and de-select components
            index = self.indexAt(event.pos())
            if index.isValid():
                self.selectionModel().select(index, QtGui.QItemSelectionModel.Toggle)
                comp = self.model().data(index, QtCore.Qt.UserRole+1)
                self.componentSelected.emit(comp)

    def emptySelection(self, empty):
        self.setEnabled(not empty)
        if empty:
            self.clearSelection()

    def updateSelectionModel(self, components):
        # selmodel = self.selectionModel()
        # selmodel.clearSelection()
        selmodel = ComponentSelectionModel(self.model())
        self.setSelectionModel(selmodel)
        for comp in components:
            selmodel.selectComponent(comp)
        self.viewport().update()

    def cursor(self, pos):
        index = self.splitAt(pos)

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

        y0 = index[0]*(ROW_HEIGHT + ROW_SPACE) + ROW_SPACE
        y1 = y0 + ROW_HEIGHT

        # adjust for scrolled viewport
        x -= self.horizontalScrollBar().value()
        y0 -= self.verticalScrollBar().value()
        y1 -= self.verticalScrollBar().value()
        
        return QtCore.QLine(x,y0,x,y1)


    def dropped(self, component, event):
        if isinstance(component, AbstractStimulusComponent):
            row, col = self.splitAt(event.pos())
            index = self.model().createIndex(row, col, component)
            
            self.model().insertComponent(index, component)

            if isinstance(event.source(), DragLabel):
                if component.__class__.__name__ in self._componentDefaults:
                    component.loadState(self._componentDefaults[component.__class__.__name__])
                self.edit(index)

            self.hashIsDirty = True
            self.viewport().update()

    def sizeHint(self):
        return QtCore.QSize(self.width(), self._height)

    def setMode(self, mode):
        self.mode = mode
        if mode == BUILDMODE:
            self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
            self.setSelectionModel(QtGui.QItemSelectionModel(self.model()))
            self.setEnabled(True)
            self.model().updateComponentStartVals()
        else:
            self.model().purgeAutoSelected()
            self.setSelectionModel(ComponentSelectionModel(self.model()))
            self.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)

    def selectionChanged(self, selected, deselected):
        super(StimulusView, self).selectionChanged(selected, deselected)

    def visualRegionForSelection(self, selection):
        region = QtGui.QRegion()
        for index in selection.indexes():
            region = region.united(self._rects[index.row()][index.column()])

        return region

    @staticmethod
    def updateDefaults(sender, state):
        # keep all defaults the same across instances
        StimulusView._componentDefaults[str(sender)] = state

    def updateGeometries(self,a=None, b=None):
        self.horizontalScrollBar().setSingleStep(self.pixelsPerms)
        self.horizontalScrollBar().setPageStep(self.viewport().width())
        self.horizontalScrollBar().setRange(0, max(0, self._width - self.viewport().width()))

        self.verticalScrollBar().setSingleStep(self.pixelsPerms)
        self.verticalScrollBar().setPageStep(self.viewport().height())
        self.verticalScrollBar().setRange(0, max(0, self._height - self.viewport().height()))
        
    def resizeEvent(self, event):
        self.hashIsDirty = True
        super(StimulusView, self).resizeEvent(event)

    def updateVocalAuto(self, component, files):
        auto_model = self.model().autoParams()
        row = auto_model.fileParameter(component)
        if len(files) > 1:
            p = {'parameter' : 'file',
                 'names' : files,
                 'selection' : [component]
            }
            if row is None:
                auto_model.insertItem(auto_model.index(0,0), p)
            else:
                auto_model.setData(auto_model.index(row,0),p)
        elif row is not None:
            # remove the autoparameter
            auto_model.removeRow(row)
        # if row is none and len(files) == 1 then we don't need to do anything
        self.countChanged.emit()
        
class ComponentDelegate(QtGui.QStyledItemDelegate):

    def paint(self, painter, option, index):
        component = index.model().data(index, role=QtCore.Qt.UserRole)
        painter.drawRect(option.rect)

        component.paint(painter, option.rect, option.palette)

    def sizeHint(self, option, index):
        # calculate size by data component
        component = index.internalPointer()
        width = self.component.duration() * self.pixelsPerms*1000
        return QtCore.QSize(width, 50)

    def createEditor(self, parent, option, index):
        # bring up separate window for component parameters
        view = parent.parentWidget()
        component = view.model().data(index)

        if component is not None:
            editor = component.showEditor()
        else:
            print 'delegate data type', type(component)
            raise Exception('UnknownDelegateType')

        # connect editor to update defaults
        editor.attributesSaved.connect(view.updateDefaults)
        editor.attributesSaved.connect(view.somethingChanged)

        if component.name == 'Vocalization':
            # find any associated file auto-parameters
            files = view.model().autoParams().findFileParam(component)
            if files is not None:
                editor.selectMany(files)
            editor.vocalFilesChanged.connect(view.updateVocalAuto)

        return editor

    def setModelData(self, editor, model, index):
        """Saves the input from the editor widget to the model component"""
        editor.saveToObject()
        # need to save over component object in stimulus model
        model.dataEdited()

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