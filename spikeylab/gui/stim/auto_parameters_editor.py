from PyQt4 import QtGui, QtCore

from spikeylab.gui.drag_label import DragLabel
from spikeylab.gui.stim.auto_parameter_view import AutoParameterTableView, AddLabel
from spikeylab.gui.trashcan import TrashWidget
from spikeylab.gui.hidden_widget import WidgetHider
from spikeylab.stim.reorder import order_function

class Parametizer(QtGui.QWidget):
    """Container widget for the auto parameters"""
    hintRequested = QtCore.pyqtSignal(str)
    visibilityChanged = QtCore.pyqtSignal(bool)
    titleChange = QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        layout = QtGui.QVBoxLayout()
        btnLayout = QtGui.QHBoxLayout()
        
        self.addLbl = DragLabel(AddLabel)

        separator = QtGui.QFrame()
        separator.setFrameShape(QtGui.QFrame.VLine)
        separator.setFrameShadow(QtGui.QFrame.Sunken)
        
        self.trashLbl = TrashWidget(self)
        
        self.randomizeCkbx = QtGui.QCheckBox("Randomize order")

        btnLayout.addWidget(self.addLbl)
        btnLayout.addWidget(self.trashLbl)
        btnLayout.addWidget(separator)
        btnLayout.addWidget(self.randomizeCkbx)

        self.paramList = AutoParameterTableView()
        self.paramList.installEventFilter(self.trashLbl)
        self.paramList.hintRequested.connect(self.hintRequested)

        layout.addWidget(self.paramList)
        layout.addLayout(btnLayout)
        self.setLayout(layout)
        self.setWindowTitle('Auto Parameters')

    def view(self):
        """Gets the AutoParameter View

        :returns: :class:`AutoParameterTableView<spikeylab.gui.stim.auto_parameter_view.AutoParameterTableView>`
        """
        return self.paramList

    def setModel(self, model):
        """sets the model for the auto parameters

        :param model: The data stucture for this editor to provide access to
        :type model: :class:`QAutoParameterModel<spikeylab.gui.stim.qauto_parameter_model.QAutoParameterModel>`
        """
        self.paramList.setModel(model)
        model.hintRequested.connect(self.hintRequested)
        model.rowsInserted.connect(self.updateTitle)
        model.rowsRemoved.connect(self.updateTitle)
        self.updateTitle()
        
    def updateTitle(self):
        """Updates the Title of this widget according to how many parameters are currently in the model"""
        title = 'Auto Parameters ({})'.format(self.paramList.model().rowCount())
        self.titleChange.emit(title)
        self.setWindowTitle(title)

    def showEvent(self, event):
        """When this widget is shown it has an effect of putting
        other widgets in the parent widget into different editing modes, emits
        signal to notify other widgets. Restores the previous selection the last
        time this widget was visible"""
        selected = self.paramList.selectedIndexes()
        model = self.paramList.model()

        self.visibilityChanged.emit(1)
        if len(selected) > 0:
            # select the correct components in the StimulusView
            self.paramList.parameterChanged.emit(model.selection(selected[0]))
            self.hintRequested.emit('Select parameter to edit. \
                Parameter must have selected components in order to edit fields')
        elif model.rowCount() > 0:
            # just select first item
            self.paramList.selectRow(0)
            self.paramList.parameterChanged.emit(model.selection(model.index(0,0)))
            self.hintRequested.emit('Select parameter to edit. \
                Parameter must have selected components in order to edit fields')
        else:
            model.emptied.emit(True)
            self.hintRequested.emit('Drag to add parameter first')

    def hideEvent(self, event):
        """notifies other widgets this editor is not longer visible"""
        self.visibilityChanged.emit(0)
        self.hintRequested.emit('Drag Components onto view to Add. Double click to edit; right drag to move.')

    def closeEvent(self, event):
        """Emits a signal to update start values on components"""
        self.visibilityChanged.emit(0)


class HidableParameterEditor(WidgetHider):
    """A hidable container for the parameter widget. Wraps some of it methods"""
    def __init__(self, parent=None):
        self.parametizer = Parametizer()
        WidgetHider.__init__(self, self.parametizer, parent=parent)

        self.parametizer.titleChange.connect(self.updateTitle)
        # wrap methods from parametizer
        for m in ['setModel', 'hintRequested', 'visibilityChanged', 
                    'view', 'randomizeCkbx']:
            setattr(self, m, getattr(self.parametizer, m))

    def updateTitle(self, title):
        """Updates the title of this widget"""
        self.title.setText(title)

    def sizeHint(self):
        return QtCore.QSize(560,40)


if __name__ == '__main__':
    import sys
    from spikeylab.gui.stim.stimulusview import *
    from spikeylab.stim.stimulusmodel import *

    app  = QtGui.QApplication(sys.argv)

    stim = StimulusModel()
    stimview = StimulusView()
    stimview.setModel(stim)
    automagic = Parametizer(stimview)
    automagic.show()

    app.exec_()