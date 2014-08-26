import os
import json

from PyQt4.QtTest import QTest 
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import Qt, QTimer
import unittest

from spikeylab.gui.stim.qstimulus import QStimulusModel
from spikeylab.stim.stimulusmodel import StimulusModel
from spikeylab.stim.types.stimuli_classes import PureTone, Vocalization, Silence
from spikeylab.gui.stim.stimulus_editor import StimulusEditor
from spikeylab.stim.auto_parameter_model import AutoParameterModel
import test.sample as sample
from test.util import qtbot


class TestStimulusEditor():

    def setUp(self):
        self.tempfile = os.path.join(os.path.abspath(os.path.dirname(__file__)), u"tmp", 'testsave.json')
        model = StimulusModel()
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
        editor.setStimulusModel(QStimulusModel(model))
        self.editor = editor

    def tearDown(self):
        self.editor.close()
        self.editor.deleteLater()

    def test_preview(self):
        
        self.editor.show()
        QTest.mouseClick(self.editor.ui.previewBtn, Qt.LeftButton)

        assert self.editor.previewFig is not None

        self.editor.previewFig.close()
        
    @unittest.skip("Works indepdently but not in batch?")
    def test_save(self):
        self.editor.show()
        QApplication.processEvents()
        # QTimer.singleShot(1000, self.close_dialog)
        # qtbot.listen_for_file_dialog(sample.test_template())
        QTest.mouseClick(self.editor.ui.saveBtn, Qt.LeftButton)
        
        # blocks until timer runs out
        with open(self.tempfile, 'r') as jf:
            template = json.load(jf)

        assert isinstance(template, dict)

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