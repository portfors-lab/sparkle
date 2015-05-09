import json
import os
import unittest

import qtbot
import test.sample as sample
from sparkle.QtWrapper.QtCore import Qt, QTimer
from sparkle.QtWrapper.QtGui import QApplication
from sparkle.QtWrapper.QtTest import QTest
from sparkle.gui.stim.factory import BuilderFactory
from sparkle.gui.stim.qstimulus import QStimulusModel
from sparkle.gui.stim.stimulus_editor import StimulusEditor
from sparkle.stim.auto_parameter_model import AutoParameterModel
from sparkle.stim.stimulus_model import StimulusModel
from sparkle.stim.types.stimuli_classes import PureTone, Silence, Vocalization

ALLOW = 100

class TestStimulusEditor():

    def setUp(self):
        self.tempfile = os.path.join(os.path.abspath(os.path.dirname(__file__)), u"tmp", 'testsave.json')
        model = StimulusModel()
        model.setMaxVoltage(1.5, 10.0)
        model.setReferenceVoltage(100, 0.1)
        model.setRepCount(7)
        # add tone, vocalization, and silence components
        component = PureTone()
        component.setIntensity(34)
        component.setDuration(0.2)
        model.insertComponent(component, 0,0)
        vocal = Vocalization()
        vocal.setFile(sample.samplewav())
        model.insertEmptyRow()
        model.insertComponent(vocal, 1,0)
        silence = Silence()
        # have gap between tone and vocal
        silence.setDuration(0.5)
        model.insertComponent(silence, 1,0)
        nsteps = self.add_auto_param(model)
        editor = StimulusEditor()
        editor.setModel(QStimulusModel(model))
        self.editor = editor
        self.stim = model

    def tearDown(self):
        self.editor.close()
        self.editor.deleteLater()        
        QApplication.closeAllWindows()
        QApplication.processEvents()

    def test_preview(self):
        
        self.editor.show()
        QTest.mouseClick(self.editor.ui.previewBtn, Qt.LeftButton)

        assert self.editor.previewFig is not None

        self.editor.previewFig.close()
        
    # @unittest.skip("Works indepdently but not in batch?")
    def test_save(self):
        self.editor.show()
        QApplication.processEvents()
        QTimer.singleShot(1000, self.close_dialog)
        # qtbot.handle_modal_widget(sample.test_template(), wait=False)
        QTest.mouseClick(self.editor.ui.saveBtn, Qt.LeftButton)
        
        # blocks until timer runs out
        with open(self.tempfile, 'r') as jf:
            template = json.load(jf)

        assert isinstance(template, dict)

    def test_move_auto_parameter(self):
        self.editor.show()

        signals, docs, overloads = self.stim.expandedStim()
        # check the first two, make sure they are not the same
        key = 'duration'
        assert docs[0]['components'][0][key] != docs[1]['components'][0][key]

        QTest.qWait(ALLOW)
        qtbot.click(self.editor.ui.parametizer.hideBtn)
        QTest.qWait(ALLOW)
        pztr = self.editor.ui.parametizer.parametizer

        qtbot.drag(pztr.paramList, pztr.paramList, pztr.paramList.model().index(0,0))
        QTest.qWait(ALLOW)

        signals, docs, overloads = self.stim.expandedStim()
        # check the first two, make sure they are not the same
        assert docs[0]['components'][0][key] != docs[1]['components'][0][key]

    def test_rep_count_persistant(self):
        self.editor.show()

        le_count = 44
        self.editor.ui.nrepsSpnbx.setValue(le_count)
        QTest.qWait(ALLOW)
        
        assert self.stim.repCount() == le_count

        factory = BuilderFactory()
        newstim = factory.create()
        
        # add a component so the editor doesn't complain when we close it
        component = PureTone()
        newstim.insertComponent(component, 0,0)
        newstim.setReferenceVoltage(100, 0.1)

        qstim = QStimulusModel(newstim)
        neweditor = qstim.showEditor()
        neweditor.show()

        assert newstim.repCount() == le_count
        assert neweditor.ui.nrepsSpnbx.value() == le_count

        neweditor.close()
        neweditor.deleteLater()

    def add_auto_param(self, model):
        # adds an autoparameter to the given model
        ptype = 'duration'
        start = .1
        step = .2
        stop = 1.0

        parameter_model = model.autoParams()
        parameter_model.insertRow(0)
        # select first component
        parameter_model.toggleSelection(0, model.component(0,0))
        # set values for autoparams
        parameter_model.setParamValue(0, start=start, step=step, 
                                      stop=stop, parameter=ptype)

    def close_dialog(self):
        print 'what what'
        dialog = QApplication.activeModalWidget()
        focused = QApplication.focusWidget()
        QTest.keyClicks(focused, self.tempfile)
        QApplication.processEvents()
        # QTest.keyClick(dialog, Qt.Key_Enter)
        print 'accepting'
        dialog.accept()
