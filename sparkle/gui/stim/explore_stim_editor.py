from explore_stim_editor_form import Ui_ExploreStimEditor
from sparkle.QtWrapper import QtCore, QtGui
from sparkle.gui.stim.abstract_stim_editor import AbstractStimulusWidget
from sparkle.gui.stim.components.qcomponents import wrapComponent
from sparkle.gui.stim.explore_component_editor import ExploreComponentEditor
from sparkle.stim.types import get_stimuli_models
from sparkle.stim.types.stimuli_classes import Silence


class ExploreStimulusEditor(AbstractStimulusWidget):
    """Editor for StimulusModel used in search mode"""
    def __init__(self, parent=None):
        super(ExploreStimulusEditor, self).__init__(parent)
        self.ui = Ui_ExploreStimEditor()
        self.ui.setupUi(self)

        self.trackBtnGroup = QtGui.QButtonGroup()

        self.ui.addBtn.clicked.connect(self.addComponentEditor)
        self.ui.exNrepsSpnbx.valueChanged.connect(self.setReps)
        self.ui.exNrepsSpnbx.setKeyboardTracking(False)

        self.funit_fields.append(self.ui.aofsSpnbx)

        self.buttons  = []

        self.stimuli_types = get_stimuli_models()
        self._allComponents = []
        self._model = None
        
    def setModel(self, model):
        "Sets the StimulusModel for this editor"
        self._model = model
        self.ui.aofsSpnbx.setValue(model.samplerate())
        #must be at least one component & delay
        # for row in range(1,model.rowCount()):
        #     delay = model.component(row,0)

        # self.ui.componentEditor

    def model(self):
        return self._model

    def setStimIndex(self, row, stimIndex):
        "Change out the component type in row to the one indexed by stimIndex"
        newcomp = self._allComponents[row][stimIndex]
        self._model.removeComponent(row, 1)
        self._model.insertComponent(newcomp, row, 1)

    def setDelay(self, row, delay):
        self._model.component(row,0).setDuration(delay)
        self.valueChanged.emit()

    def repCount(self):
        return self.ui.exNrepsSpnbx.value()

    def setReps(self, reps):
        if self._model is not None:
            self._model.setRepCount(reps)
        self.ui.exNrepsSpnbx.setValue(reps)
        self.valueChanged.emit()

    def addComponentEditor(self):
        """Adds a new component to the model, and an editor for this component to this editor"""
        row = self._model.rowCount()

        comp_stack_editor = ExploreComponentEditor()
        self.ui.trackStack.addWidget(comp_stack_editor)

        idx_button = IndexButton(row)
        idx_button.pickMe.connect(self.ui.trackStack.setCurrentIndex)
        self.trackBtnGroup.addButton(idx_button)
        self.ui.trackBtnLayout.addWidget(idx_button)
        self.ui.trackStack.setCurrentIndex(row)

        comp_stack_editor.closePlease.connect(self.removeComponentEditor)

        delay = Silence()
        comp_stack_editor.delaySpnbx.setValue(delay.duration())
        self._model.insertComponent(delay, row,0)

        self._allComponents.append([x() for x in self.stimuli_types if x.explore])
        for stim in self._allComponents[row]:
            editor = wrapComponent(stim).showEditor()
            comp_stack_editor.addWidget(editor, stim.name)

        exvocal = comp_stack_editor.widgetForName("Vocalization")
        if exvocal is not None:
            exvocal.filelistView.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

        initcomp = self._allComponents[row][0]
        self._model.insertComponent(initcomp, row, 1)

        self.buttons.append(idx_button)

        comp_stack_editor.exploreStimTypeCmbbx.currentIndexChanged.connect(lambda x : self.setStimIndex(row, x))
        comp_stack_editor.delaySpnbx.valueChanged.connect(lambda x : self.setDelay(row, x))
        comp_stack_editor.valueChanged.connect(self.valueChanged.emit)
        return comp_stack_editor

    def removeComponentEditor(self, widget):
        ntracks = self.ui.trackStack.count()
        index = self.ui.trackStack.indexOf(widget)
        self.ui.trackStack.removeWidget(widget)
        self._model.removeRow(index)
        # remove index button and adjust other numbers
        for idx in range(index+1, ntracks):
            self.buttons[idx].setNum(idx-1)
        self.ui.trackBtnLayout.removeWidget(self.buttons[index])
        btn = self.buttons.pop(index)
        btn.setVisible(False)
        btn.deleteLater()
        self.valueChanged.emit()
        if len(self.buttons) > 0:
            self.buttons[0].setChecked(True)

    def saveToObject(self):
        for icomp in range(self.ui.trackStack.count()):
            self.ui.trackStack.widget(icomp).currentWidget().saveToObject()
        self.ui.aofsSpnbx.setValue(self._model.samplerate())

    def samplerate(self):
        return self._model.samplerate()

    def verify(self, winsz):
        # have the stim check itself and report
        return self._model.verify(winsz)

    def allComponentWidgets(self):
        w = []
        for itrack in range(self.ui.trackStack.count()):
            w.extend(self.ui.trackStack.widget(itrack).widgets())
        return w
        
    def trackEditorWidgets(self):
        w = []
        for itrack in range(self.ui.trackStack.count()):
            w.append(self.ui.trackStack.widget(itrack))
        return w

    def saveTemplate(self):
        template = []
        for itrack in range(self.ui.trackStack.count()):
            comp_stack_editor = self.ui.trackStack.widget(itrack)
            template.append(comp_stack_editor.saveTemplate())
        return template

    def loadTemplate(self, template):
        # wipe any current editors and add according to template
        for i in range(self.ui.trackStack.count()):
            self.removeComponentEditor(self.ui.trackStack.widget(i))

        for track in template:
            comp_stack_editor = self.addComponentEditor()
            comp_stack_editor.loadTemplate(track)

    def closeEvent(self, event):
        pass

class IndexButton(QtGui.QPushButton):
    """Custom button for explore editor to toggle bettween tracks"""
    pickMe = QtCore.Signal(int)
    def __init__(self, num):
        super(IndexButton, self).__init__("Track {}".format(num+1))
        self.num = num
        self.setCheckable(True)
        self.setChecked(True)
        self.toggled.connect(self.toggletoggle)

    def toggletoggle(self, checked):
        if checked:
            self.pickMe.emit(self.num)

    def setNum(self, num):
        self.num = num
        self.setText("Track {}".format(num+1))

if __name__ == '__main__':
    app = QtGui.QApplication([])

    editor = ExploreStimulusEditor()
    editor.show()

    app.exec_()
