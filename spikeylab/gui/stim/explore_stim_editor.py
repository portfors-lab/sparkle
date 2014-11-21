from QtWrapper import QtGui, QtCore

from explore_stim_editor_form import Ui_ExploreStimEditor
from spikeylab.gui.stim.abstract_stim_editor import AbstractStimulusWidget
from spikeylab.gui.stim.explore_component_editor import ExploreComponentEditor
from spikeylab.gui.stim.components.qcomponents import wrapComponent
from spikeylab.stim.types import get_stimuli_models
from spikeylab.stim.types.stimuli_classes import Silence
    
class ExploreStimulusEditor(AbstractStimulusWidget):
    def __init__(self, parent=None):
        super(ExploreStimulusEditor, self).__init__(parent)
        self.ui = Ui_ExploreStimEditor()
        self.ui.setupUi(self)

        self.ui.addBtn.clicked.connect(self.addComponent)
        self.ui.exNrepsSpnbx.valueChanged.connect(self.setReps)
        self.ui.exNrepsSpnbx.setKeyboardTracking(False)

        self.funit_fields.append(self.ui.aosrSpnbx)
        self.funit_labels.append(self.ui.funit_lbl)

        self.components = []

        self.stimuli_types = get_stimuli_models()
        self._allComponents = []
        self._model = None
        
    def setModel(self, model):
        self._model = model
        self.ui.aosrSpnbx.setValue(model.samplerate()/self.scales[1])
        #must be at least one component & delay
        # for row in range(1,model.rowCount()):
        #     delay = model.component(row,0)

        # self.ui.componentEditor

    def model(self):
        return self._model

    def setStimIndex(self, row, stimIndex):
        newcomp = self._allComponents[row][stimIndex]
        self._model.removeComponent(row, 1)
        self._model.insertComponent(newcomp, row, 1)

    def setDelay(self, row, delay):
        self._model.component(row,0).setDuration(delay*self.scales[0])
        self.valueChanged.emit()

    def repCount(self):
        return self.ui.exNrepsSpnbx.value()

    def setReps(self, reps):
        if self._model is not None:
            self._model.setRepCount(reps)
        self.ui.exNrepsSpnbx.setValue(reps)
        self.valueChanged.emit()

    def addComponent(self):
        comp_stack_editor = ExploreComponentEditor()
        self.ui.layout.addWidget(comp_stack_editor)

        row = self._model.rowCount()
        delay = Silence()
        comp_stack_editor.delaySpnbx.setValue(delay.duration()/self.scales[0])
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

        self.components.append(comp_stack_editor)

        comp_stack_editor.exploreStimTypeCmbbx.currentIndexChanged.connect(lambda x : self.setStimIndex(row, x))
        comp_stack_editor.delaySpnbx.valueChanged.connect(lambda x : self.setDelay(row, x))
        comp_stack_editor.valueChanged.connect(self.valueChanged.emit)

    def saveToObject(self):
        for comp in self.components:
            comp.currentWidget().saveToObject()
        self.ui.aosrSpnbx.setValue(self._model.samplerate()/self.scales[1])

    def samplerate(self):
        return self._model.samplerate()

    def verify(self, winsz):
        # have the stim check itself and report
        return self._model.verify(winsz)

if __name__ == '__main__':
    app = QtGui.QApplication([])

    editor = ExploreStimulusEditor()
    editor.show()

    app.exec_()
