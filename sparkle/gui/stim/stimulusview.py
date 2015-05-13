from sparkle.QtWrapper import QtCore, QtGui
from sparkle.gui.abstract_drag_view import AbstractDragView
from sparkle.gui.drag_label import DragLabel
from sparkle.gui.qconstants import AutoParamMode, BuildMode, CursorRole
from sparkle.gui.stim.selectionmodel import ComponentSelectionModel
from sparkle.stim.abstract_component import AbstractStimulusComponent

ROW_HEIGHT = 100
ROW_SPACE = 25

GRID_PIXEL_MIN = 100
GRID_PIXEL_MAX = 200

class StimulusView(AbstractDragView, QtGui.QAbstractItemView):
    """View for building/editing stimulus components"""
    _viewIsDirty = False
    _height = ROW_HEIGHT
    _width = 10
    _componentDefaults = {}
    componentSelected = QtCore.Signal(AbstractStimulusComponent)
    countChanged = QtCore.Signal()
    hintRequested = QtCore.Signal(str)
    def __init__(self, parent=None):
        super(StimulusView, self).__init__()

        self.horizontalScrollBar().setRange(0, 0)
        self.verticalScrollBar().setRange(0, 0)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.dragline = None

        self.setItemDelegate(ComponentDelegate())
        self.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

        self.mode = BuildMode
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
        :returns: float -- the miliseconds between grid lines
        """
        pxms = float(pxms)/2
        self.pixelsPerms = pxms
        if pxms*self.gridms < GRID_PIXEL_MIN:
            self.gridms = self.gridms*2
        elif pxms*self.gridms > GRID_PIXEL_MAX:
            self.gridms = self.gridms/2
        self._viewIsDirty = True
        self.viewport().update()

        return self.gridms

    def setModel(self, model):
        """Sets the model this view represents. :qtdoc:`Re-implemented<QAbstractItemView.setModel>`

        :param model: model to set
        :type model: :class:`QStimulusModel<sparkle.gui.stim.stimulus_model.QStimulusModel>`
        """
        super(StimulusView, self).setModel(model)
        self.setSelectionModel(ComponentSelectionModel(model))
        # initialize nested list to appropriate size
        self._rects = [[None] * self.model().columnCountForRow(x) for x in range(self.model().rowCount())]

        self._viewIsDirty = True
        self._calculateRects()

    def indexXY(self, index):
        """Returns the top left coordinates of the item for the given index

        :param index: index for the item
        :type index: :qtdoc:`QModelIndex`
        :returns: (int, int) -- (x, y) view coordinates of item
        """
        rect = self.visualRect(index)
        return rect.x(), rect.y()

    def indexAt(self, point):
        """Returns the index of the component at *point* relative to view coordinates.
        If there is None, and empty index is returned. :qtdoc:`Re-implemented<QAbstractItemView.indexAt>`

        :param point: the point, in view coordinates, to find an index for
        :type point: :qtdoc:`QPoint`
        :returns: :qtdoc:`QModelIndex`
        """
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
        # calculates the size of each component, a rectangle representative of the relative
        # duration of the component
        if not self._viewIsDirty:
            return

        self._rects = [[None] * self.model().columnCountForRow(x) for x in range(self.model().rowCount()+1)]
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
        self._viewIsDirty = False

    def splitAt(self, point):
        """Gets the nearest index to *point*, *point* does not have to be over 
        an item. index can be +1 more in row and/or column than existing items

        :param point: any point within the view, in view coordinates
        :type point: :qtdoc:`QPoint`
        :returns: (int, int) -- (row, column) of the nearest index
        """
        wx = point.x() + self.horizontalScrollBar().value()
        wy = point.y() + self.verticalScrollBar().value()

        row = wy/(ROW_HEIGHT + ROW_SPACE)
        if row > self.model().rowCount(self.rootIndex()) - 1:
            row = self.model().rowCount(self.rootIndex())
        for col in range(self.model().columnCountForRow(row)):
            if self._rects[row][col].contains(wx, wy):
                return (row, col)
        return row, self.model().columnCountForRow(row)

    def isIndexHidden(self, index):
        """Items are never hidden. :qtdoc:`Re-implemented<QAbstractItemView.isIndexHidden>`
        
        :returns: bool -- False
        """
        return False

    def visualRect(self, index):
        """The rectangle for the bounds of the item at *index*. :qtdoc:`Re-implemented<QAbstractItemView.visualRect>`

        :param index: index for the rect you want
        :type index: :qtdoc:`QModelIndex`
        :returns: :qtdoc:`QRect` -- rectangle of the borders of the item
        """
        if len(self._rects[index.row()]) -1 < index.column() or index.row() == -1:
            #Er, so I don't know why this was getting called with index -1
            return QtCore.QRect()
    
        return self.visualRectRC(index.row(),index.column())

    def visualRectRC(self, row, column):
        """The rectangle for the bounds of the item at *row*, *column*

        :param row: row of the item
        :type row: int
        :param column: column of the item
        :type column: int
        :returns: :qtdoc:`QRect` -- rectangle of the borders of the item
        """
        rect = self._rects[row][column]
        if rect.isValid():
            return QtCore.QRect(rect.x() - self.horizontalScrollBar().value(),
                         rect.y() - self.verticalScrollBar().value(),
                         rect.width(), rect.height())
        else:
            return rect

    def dataChanged(self, topleft, bottomright):
        """Marks view for repaint. :qtdoc:`Re-implemented<QAbstractItemView.dataChanged>`"""
        self._viewIsDirty = True
        super(StimulusView, self).dataChanged(topleft, bottomright)

    def rowsInserted(self, parent, start, end):
        """Marks view for repaint. :qtdoc:`Re-implemented<QAbstractItemView.rowsInserted>`"""
        self._viewIsDirty = True
        super(StimulusView, self).rowsInserted(parent, start, end)

    def rowsAboutToBeRemoved(self, parent, start, end):
        """Marks view for repaint. :qtdoc:`Re-implemented<QAbstractItemView.rowsAboutToBeRemoved>`"""
        self._viewIsDirty = True
        super(StimulusView, self).rowsAboutToBeRemoved(parent, start, end)

    def somethingChanged(self):
        """Marks view for repaint"""
        self._viewIsDirty = True

    def verticalOffset(self):
        """Offset caused by vertical scrollbar. :qtdoc:`Re-implemented<QAbstractItemView.verticalOffset>`

        :returns: int -- number of increments (pixels) down in scroll bar
        """
        return self.verticalScrollBar().value()

    def horizontalOffset(self):
        """Offset caused by horizontal scrollbar. :qtdoc:`Re-implemented<QAbstractItemView.horizontalOffset>`

        :returns: int -- number of increments (pixels) over in scroll bar
        """
        return self.horizontalScrollBar().value()

    def scrollTo(self, index, ScrollHint):
        """:qtdoc:`Re-implemented<QAbstractItemView.scrollTo>`"""
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
        """Scrolls the viewport. :qtdoc:`Re-implemented<QAbstractScrollArea.scrollContentsBy>`"""
        # self.scrollDirtyRegion(dx,dy) #in web example
        self.viewport().scroll(dx, dy)

    def paintEvent(self, event):
        """All custom painting, draws the entire view. :qtdoc:`Re-implemented<qabstractscrollarea.paintEvent>`"""
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
        """Returns an empty index. :qtdoc:`Re-implemented<QAbstractItemView.moveCursor>`"""
        return QtCore.QModelIndex()

    def mouseDoubleClickEvent(self, event):
        """Launches an editor for the component, if the mouse cursor is over an item"""
        if self.mode == BuildMode:
            if event.button() == QtCore.Qt.LeftButton:
                index = self.indexAt(event.pos())
                self.edit(index)

    def mouseMoveEvent(self, event):
        super(StimulusView, self).mouseMoveEvent(event)
        if self.mode == AutoParamMode:
            # default is buildmode, so we need to set if auto-param mode
            index = self.indexAt(event.pos())
            cursor = self.model().data(index, CursorRole, self.mode)
            self.setCursor(cursor)

            
    def grabImage(self, index):
        """Gets an image of the item at *index*

        :param index: index of an item in the view
        :type index: :qtdoc:`QModelIndex`
        :returns: :qtdoc:`QPixmap`
        """
        # rect = self._rects[index.row()][index.column()]
        rect = self.visualRect(index)
        pixmap = QtGui.QPixmap()
        pixmap = pixmap.grabWidget(self, rect)     
        return pixmap

    def mousePressEvent(self, event):
        """In Auto-parameter selection mode, mouse press over an item emits
        `componentSelected`"""
        if self.mode == BuildMode:
            super(StimulusView, self).mousePressEvent(event)
        else:
            # select and de-select components
            index = self.indexAt(event.pos())
            if index.isValid():
                self.selectionModel().select(index, QtGui.QItemSelectionModel.Toggle)
                comp = self.model().data(index, AbstractDragView.DragRole)
                self.componentSelected.emit(comp)
                self.hintRequested.emit('Click components to toggle more members of auto-parameter\n\n-or-\n\nEdit fields of auto-parameter (parameter type should be selected first)')

    def emptySelection(self, empty):
        """Enables the view if not *empty*, clears the current selection and
        disables view if is *emtpy*

        :param emtpy: whether there are any components in the view
        :type emtpy: bool
        """
        self.setEnabled(not empty)
        if empty:
            # self.clearSelection()
            # Clear selection doesn't work? But removing individually does
            m = self.selectionModel()
            for index in m.selectedIndexes():
                m.select(index, QtGui.QItemSelectionModel.Deselect)
            self.hintRequested.emit('To add a parameter, Drag "Add" onto empty auto-parameter table')

    def updateSelectionModel(self, components):
        """Creates a new selection model and adds *components* to it

        :param components: components in this view to add to the selection
        :type components: list<:class:`AbstractStimulusComponent<sparkle.stim.abstract_component.AbstractStimulusComponent>`
        """
        # selmodel = self.selectionModel()
        # selmodel.clearSelection()
        selmodel = ComponentSelectionModel(self.model())
        self.setSelectionModel(selmodel)
        for comp in components:
            selmodel.selectComponent(comp)
        self.viewport().update()

    def cursor(self, pos):
        """Returns a line for the cursor as position *pos*

        :param pos: mouse cursor position
        :type pos: :qtdoc:`QPoint`
        :returns: :qtdoc:`QLine` -- position between items (indicates where drops will go)
        """
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
        """Adds the dropped *component* into the model. 
        :meth:`Re-implemented<sparkle.gui.abstract_drag_view.AbstractDragView.dropped>`
        """
        if isinstance(component, AbstractStimulusComponent):
            row, col = self.splitAt(event.pos())
            index = self.model().createIndex(row, col, component)
            
            self.model().insertComponent(index, component)

            if isinstance(event.source(), DragLabel):
                if component.__class__.__name__ in self._componentDefaults:
                    component.loadState(self._componentDefaults[component.__class__.__name__])
                self.edit(index)

            self._viewIsDirty = True
            self.viewport().update()

    def sizeHint(self):
        return QtCore.QSize(self.width(), self._height)

    def setMode(self, mode):
        """Sets the "mode" for this view:

        BuildMode 0: Allowing adding, moving and editing of component items

        AutoParamMode 1: For adding components to a selection of an 
        auto-parameter. clicks toggle membership in selection. Moving and 
        editing of components disabled.
        
        :param mode: which mode to set
        :type mode: int
        """
        self.mode = mode
        if mode == BuildMode:
            self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
            self.setSelectionModel(QtGui.QItemSelectionModel(self.model()))
            self.setEnabled(True)
            self.model().updateComponentStartVals()
        else:
            self.model().purgeAutoSelected()
            self.setSelectionModel(ComponentSelectionModel(self.model()))
            self.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)

    def setSelection(self, rect, flags):
        # selection handled manually in mouse handlers
        pass

    def visualRegionForSelection(self, selection):
        """Gets the region of all of the components in selection

        :param selection: a selection model for this view
        :type selection: :qtdoc:`QItemSelectionModel`
        :returns: :qtdoc:`QRegion` -- union of rects of the selected components
        """
        region = QtGui.QRegion()
        for index in selection.indexes():
            region = region.united(self._rects[index.row()][index.column()])

        return region

    @staticmethod
    def updateDefaults(sender, state):
        """Updates the input defaults for the component fields

        :param sender: Component (:class:`AbstractStimulusComponent<sparkle.stim.abstract_component.AbstractStimulusComponent>`) class name to set the defaults for
        :type sender: str
        :param state: the return value from that component's :meth:`stateDict<sparkle.stim.abstract_component.AbstractStimulusComponent.stateDict>` method
        :type state: dict
        """
        # keep all defaults the same across instances
        StimulusView._componentDefaults[str(sender)] = state

    @staticmethod
    def getDefaults():
        """Returns a dict of all the latest default settings that have been set in all views"""
        return StimulusView._componentDefaults

    def updateGeometries(self,a=None, b=None):
        self.horizontalScrollBar().setSingleStep(self.pixelsPerms)
        self.horizontalScrollBar().setPageStep(self.viewport().width())
        self.horizontalScrollBar().setRange(0, max(0, self._width - self.viewport().width()))

        self.verticalScrollBar().setSingleStep(self.pixelsPerms)
        self.verticalScrollBar().setPageStep(self.viewport().height())
        self.verticalScrollBar().setRange(0, max(0, self._height - self.viewport().height()))
        
    def resizeEvent(self, event):
        """Mark repaint needed. :qtdoc:`Re-implemented<QWidget.resizeEvent>`"""
        self._viewIsDirty = True
        super(StimulusView, self).resizeEvent(event)

    def updateVocalAuto(self, component, files):
        """Updates the auto-parameter with selected *component* to have
        *files*. Adds auto-parameter if not already present. The auto-parameter is expected to have only one selected
        component (the one given). If length of files < 1, removes the
        auto-parameter from the model.

        :param component: Component that the auto-parameter is modifying
        :type component: :class:`AbstractStimulusComponent<sparkle.stim.abstract_component.AbstractStimulusComponent>`
        :param files: list of file names to act as the auto-parameter list
        :type files: list<str>
        """
        auto_model = self.model().autoParams()
        row = auto_model.fileParameter(component)
        if len(files) > 1:
            clean_component = self.model().data(self.model().indexByComponent(component), AbstractDragView.DragRole)
            p = {'parameter' : 'filename',
                 'names' : files,
                 'selection' : [clean_component]
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
    """Delegate to represent stimulus components"""
    def paint(self, painter, option, index):
        """Uses the :meth:`paint<sparkle.gui.stim.components.qcomponents.QStimulusComponent.paint>` 
        method of the component it represents to fill in an appropriately 
        sized rectange. :qtdoc:`Re-implemented<QStyledItemDelegate.paint>`"""
        component = index.model().data(index, role=QtCore.Qt.UserRole)
        painter.drawRect(option.rect)

        component.paint(painter, option.rect, option.palette)

    def sizeHint(self, option, index):
        """Size based on component duration and a fixed height"""
        # calculate size by data component
        component = index.internalPointer()
        width = self.component.duration() * self.pixelsPerms*1000
        return QtCore.QSize(width, 50)

    def createEditor(self, parent, option, index):
        """Creates an editor in a separate window, specific for the component
        type this delegate represents. :qtdoc:`Re-implemented<QStyledItemDelegate.createEditor>`"""
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
        """Saves the input from the editor widget to the model component.
        :qtdoc:`Re-implemented<QStyledItemDelegate.setModelData>`"""
        editor.saveToObject()
        # need to save over component object in stimulus model
        model.dataEdited()

        # clean up
        editor.attributesSaved.disconnect()
        if hasattr(editor, 'vocalFilesChanged'):
            editor.vocalFilesChanged.disconnect()
        editor.close()

    def updateEditorGeometry(self, editor, option, index):
        """centers the editor widget. :qtdoc:`Re-implemented<QStyledItemDelegate.updateEditorGeometry>`"""
        qr = editor.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)

        editor.move(qr.topLeft())

    def eventFilter(self, editor, event):
        """Sets focus to the editor. :qtdoc:`Re-implemented<QStyledItemDelegate.eventFilter>`"""
        if event.type() == QtCore.QEvent.FocusIn:
            editor.setContentFocus()
            return True

        return super(ComponentDelegate, self).eventFilter(editor, event)



if __name__ == "__main__":
    import sys
    from sparkle.stim.stimulus_model import *
    from sparkle.stim.types.stimuli_classes import *
    from sparkle.gui.stim.qstimulus import QStimulusModel
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
    # vocal0.setFile(r'C:\Users\amy.boyle\Dropbox\daqstuff\M1_FD024\M1_FD024_syl_12.wav')
    vocal0.setFile(r'/home/leeloo/testdata/M1_FD024/M1_FD024_syl_12.wav')

    silence0 = Silence()
    silence0.setDuration(0.025)

    stim = StimulusModel()
    stim.insertComponent(tone2)
    stim.insertComponent(tone1)
    stim.insertComponent(tone0)

    stim.insertComponent(tone4, 1, 0)
    stim.insertComponent(tone5, 1, 0)
    stim.insertComponent(vocal0, 1, 0)

    stim.insertComponent(tone3, 2, 0)
    stim.insertComponent(silence0, 2, 0)

    viewer = StimulusView()
    
    viewer.setModel(QStimulusModel(stim))
    viewer.resize(500,400)
    viewer.show()
    app.exec_()
