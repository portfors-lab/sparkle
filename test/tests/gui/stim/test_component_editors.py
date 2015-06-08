import os

import qtbot
from sparkle.QtWrapper import QtCore, QtGui, QtTest
from sparkle.gui.stim.components.qcomponents import wrapComponent
from sparkle.gui.stim.components.vocal_parameters import VocalParameterWidget
from sparkle.stim.types import get_stimuli_models
from sparkle.stim.types.stimuli_classes import *
from sparkle.stim.types.stimuli_classes import PureTone, Vocalization
from test import sample


class TestVocalizationEditor():
    def setUp(self):
        self.component = Vocalization()
        self.qcomponent = wrapComponent(self.component)
        self.editor = self.qcomponent.showEditor()

        fpath = sample.samplewav()
        parentdir, fname = os.path.split(fpath)
        self.editor.setRootDirs(parentdir, parentdir)
        self.editor.show()

    def tearDown(self):
        self.editor.close()
        self.editor.deleteLater()
        QtGui.QApplication.processEvents()     

    def xtest_file_order(self):
        # these methods of selecting files, won't work in testing (only)
        # due to the bugs or whatever while trying to use automated testing

        # select all the (wav) files in folder
        # self.editor.filelistView.selectAll()
        # QtGui.QApplication.processEvents()
        # QtTest.QTest.qWait(5000)

        # qtbot.drag_view(self.editor.filelistView, (0,0), (0,2))

        #... so I'm going to try and cheat
        QtTest.QTest.qWait(100)
        qtbot.drag(self.editor.filelistView, self.editor.filelistView, self.editor.filelistView.model().index(0,0))

        original_order = self.editor.fileorder

        # can't find a way to get a hold of the file order dialog :(
        qtbot.click(self.editor.orderBtn)
        qtbot.handle_modal_widget(wait=True, func=reorder)
        # QtTest.QTest.qWait(1000)

        new_order = self.editor.fileorder

        assert new_order == original_order

    def test_file_select_many(self):
        QtTest.QTest.qWait(100)
        qtbot.drag(self.editor.filelistView, self.editor.filelistView, self.editor.filelistView.model().index(0,0))
        
        self.editor.saveToObject()

        values = self.component.stateDict()
        assert values['filename'] is not None
        assert len(self.editor.fileorder) > 1

    def test_file_select_many_then_one(self):
        # make sure previous selection is clearing
        QtTest.QTest.qWait(100)
        qtbot.drag(self.editor.filelistView, self.editor.filelistView, self.editor.filelistView.model().index(0,0))
        QtTest.QTest.qWait(100)

        qtbot.click(self.editor.filelistView, self.editor.filelistView.model().index(0,0))        
        QtTest.QTest.qWait(100)
        self.editor.saveToObject()

        values = self.component.stateDict()
        assert values['filename'] is not None
        assert len(self.editor.fileorder) == 1

    def test_all_input_fields(self):
        QtTest.QTest.qWait(100)

        self.editor.dbSpnbx.setValue(66)
        self.editor.risefallSpnbx.setValue(0.022)

        qtbot.click(self.editor.filelistView, self.editor.filelistView.model().index(0,0))        
        QtTest.QTest.qWait(100)
        self.editor.saveToObject()

        values = self.component.stateDict()
        assert values['filename'] is not None
        assert len(self.editor.fileorder) == 1
        assert values['intensity'] == 66
        assert values['risefall'] == 0.022

def reorder(widget):
    qtbot.drag_view(widget.orderlist, (0,0), (1,0))
    QtTest.QTest.qWait(1000)
    qtbot.click(widget.okBtn)

class TestEditors():
    def setUp(self):
        stimuli_types = get_stimuli_models()
        self.allComponents = [wrapComponent(x()) for x in stimuli_types]
    
    def test_all_editor_must_haves(self):
        for comp in self.allComponents:
            # print comp.name, comp
            editor = comp.showEditor()
            assert editor.name() == comp.name
            assert editor.component() == comp
            val = 0.01
            for parameter_name, field in editor.inputWidgets.items():
                field.setValue(val)
            editor.saveToObject()
            state = comp.stateDict()    
            for parameter_name, field in editor.inputWidgets.items():
                assert state[parameter_name] == val
            editor.close()
            editor.deleteLater()        

class TestSquareWaveEditor():
    def setUp(self):
        self.component = SquareWave()
        self.qcomponent = wrapComponent(self.component)
        self.editor = self.qcomponent.showEditor()

    def tearDown(self):
        self.editor.close()
        self.editor.deleteLater()        

    def test_update_paramters(self):
        self.editor.durationInputWidget().setValue(0.44)
        self.editor.amp_input.setValue(0.44)
        self.editor.freq_input.setValue(444)
        self.editor.saveToObject()
        state = self.component.stateDict()
        assert state['duration'] == 0.44
        assert state['amplitude'] == 0.44
        assert state['frequency'] == 444

    def test_amplitude_scaling_V(self):
        self.editor.vradio.setChecked(True)
        self.editor.amp_factor_input.setValue(33)
        self.editor.amp_input.setValue(2)
        assert self.editor.amp_input.text() == '66 mV'
        self.editor.saveToObject()
        state = self.component.stateDict()
        assert state['amplitude'] == 2

    def test_amplitude_scaling_A(self):
        self.editor.aradio.setChecked(True)
        self.editor.amp_factor_input.setValue(33)
        self.editor.amp_input.setValue(2)
        assert self.editor.amp_input.text() == '66 pA'
        self.editor.saveToObject()
        state = self.component.stateDict()
        assert state['amplitude'] == 2
