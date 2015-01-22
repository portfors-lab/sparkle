from spikeylab.gui.stim.explore_stim_editor import ExploreStimulusEditor
from spikeylab.stim.stimulus_model import StimulusModel

class TestExploreStimEditor():

  def setUp(self):
    self.editor = ExploreStimulusEditor()
    self.model = StimulusModel()
    self.editor.setModel(self.model)

  def tearDown(self):
    self.editor.close()

  def test_add_remove_tracks(self):
    #lotsa adding and removing... had a bug here before
    assert self.editor.ui.trackStack.count() == 0
    assert self.model.rowCount() == 0
    assert len(self.editor.buttons) == 0
    self.editor.addComponentEditor()
    assert self.model.rowCount() == 1
    assert self.editor.ui.trackStack.count() == 1
    assert self.editor.buttons[-1].text() == "Track 1"
    self.editor.addComponentEditor()
    assert self.model.rowCount() == 2
    assert self.editor.ui.trackStack.count() == 2
    assert self.editor.buttons[-1].text() == "Track 2"
    self.editor.removeComponentEditor(self.editor.ui.trackStack.widget(0))
    assert self.model.rowCount() == 1
    assert self.editor.ui.trackStack.count() == 1
    assert self.editor.buttons[-1].text() == "Track 1"
    self.editor.addComponentEditor()
    assert self.model.rowCount() == 2
    assert self.editor.ui.trackStack.count() == 2
    assert self.editor.buttons[-1].text() == "Track 2"
    self.editor.removeComponentEditor(self.editor.ui.trackStack.widget(1))
    self.editor.removeComponentEditor(self.editor.ui.trackStack.widget(0))
    assert self.editor.ui.trackStack.count() == 0
    assert self.model.rowCount() == 0
    assert len(self.editor.buttons) == 0
    self.editor.addComponentEditor()
    assert self.model.rowCount() == 1
    assert self.editor.ui.trackStack.count() == 1
    assert self.editor.buttons[-1].text() == "Track 1"
    self.editor.addComponentEditor()
    assert self.model.rowCount() == 2
    assert self.editor.ui.trackStack.count() == 2
    assert self.editor.buttons[-1].text() == "Track 2"

  def test_save_load_inputs(self):
    self.editor.addComponentEditor()
    self.editor.addComponentEditor()
    
    # reach in and set values on inputs
    tone_editor = self.editor.ui.trackStack.widget(0).componentStack.widgetForName('Pure Tone')
    tone_editor.inputWidgets['frequency'].setValue(666)
    tone_editor.inputWidgets['duration'].setValue(0.666)

    # reach in and set values on inputs
    tone_editor = self.editor.ui.trackStack.widget(1).componentStack.widgetForName('Pure Tone')
    tone_editor.inputWidgets['frequency'].setValue(777)
    tone_editor.inputWidgets['duration'].setValue(0.777)

    template = self.editor.saveTemplate()
    new_explore_editor = ExploreStimulusEditor()
    new_explore_model = StimulusModel()
    new_explore_editor.setModel(new_explore_model)
    new_explore_editor.loadTemplate(template)

    tone_editor = new_explore_editor.ui.trackStack.widget(0).componentStack.widgetForName('Pure Tone')
    assert tone_editor.inputWidgets['frequency'].value() == 666
    assert tone_editor.inputWidgets['duration'].value() == 0.666

    tone_editor = new_explore_editor.ui.trackStack.widget(1).componentStack.widgetForName('Pure Tone')
    assert tone_editor.inputWidgets['frequency'].value() == 777
    assert tone_editor.inputWidgets['duration'].value() == 0.777

    assert new_explore_model.rowCount() == 2
    
    new_explore_editor.close()