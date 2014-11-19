from QtWrapper import QtGui, QtCore

from explore_stim_editor_form import Ui_ExploreStimEditor
from spikeylab.gui.stim.abstract_stim_editor import AbstractStimulusWidget
from spikeylab.gui.stim.expplore_stim_editor import ExploreComponentEditor
from spikeylab.gui.stim.components.qcomponents import wrapComponent

class ExploreStimulusEditor(AbstractStimulusWidget):
    def __init__(self, parent=None):
        super(ExploreStimulusEditor, self).__init__(parent)
        self.ui = Ui_ExploreStimEditor()
        self.ui.setupUi(self)

        self.addBtn.clicked.connect(self.addComponent)

        self.components = []

        self.stimuli_types = get_stimuli_models()
        self._allComponents = []
        
    def setModel(self, model):
        self._model = model
        #must be at least one component & delay
        # for row in range(1,model.rowCount()):
        #     delay = model.component(row,0)

        # self.ui.componentEditor

    def model(self):
        return self._model

    def setStimIndex(row, stimIndex):
        newcomp = self._allComponents[row, stimIndex]
        self._model.removeComponent(row, 1)
        self._model.insertComponent(newcomp, row, 1)

    def setDelay(self, row, delay):
        self._model.component(row,0).setDuration(delay*self.scales[0])

    def repCount(self):
        return self.ui.exNrepsSpnbx.value()

    def addComponent(self):
        comp_stack_editor = ExploreComponentEditor()
        self.layout.AddWidget(comp_stack_editor)
        comp_stack_editor.exploreStimTypeCmbbx.currentIndexChanged.connect(lambda x : self.setStimIndex(0, x))
        comp_stack_editor.delaySpnbx.valueChanged.connect(lambda x : self.setDelay(0, x))

        row = self._model.rowCount()
        delay = Silence()
        self._model.insertComponent(delay, row,0)

        self._allComponents.append([x() for x in self.stimuli_types if x.explore])
        for stim in self._allComponents[row]:
            editor = wrapComponent(stim).showEditor()
            comp_stack_editor.addWidget(editor)

        initcomp = self._allComponents[row, 0]
        self._model.insertComponent(initcomp, row, 1)

        self.components.append(comp_stack_editor)
