import os
import json
import threading, time

from PyQt4.QtTest import QTest 
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import Qt, QTimer

from spikeylab.stim.stimulusmodel import StimulusModel
from spikeylab.stim.types.stimuli_classes import PureTone, Vocalization, Silence
from spikeylab.stim.stimulus_editor import StimulusEditor
from spikeylab.stim.auto_parameter_model import AutoParameterModel
import test.sample as sample

app = None
def setUp():
    global app
    app = QApplication([])

def tearDown():
    QApplication.closeAllWindows()
    QApplication.processEvents()
    global app
    del app

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
        model.insertComponent(component, (0,0))
        vocal = Vocalization()
        vocal.setFile(sample.samplewav())
        model.insertComponent(vocal, (1,0))
        silence = Silence()
        # have gap between tone and vocal
        silence.setDuration(0.5)
        model.insertComponent(silence, (1,0))
        nsteps = self.add_auto_param(model)
        editor = StimulusEditor()
        editor.setStimulusModel(model)
        self.editor = editor

    def tearDown(self):
        self.editor.close()
        self.editor.deleteLater()

    def test_preview(self):
        
        self.editor.show()
        QTest.mouseClick(self.editor.ui.previewBtn, Qt.LeftButton)

        assert self.editor.previewFig is not None

        self.editor.previewFig.close()
        
    def test_save(self):
        self.editor.show()
        QApplication.processEvents()
        QTimer.singleShot(1000, self.close_dialog)
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
        parameter_model.insertRows(0,1)
        # select first component
        selection_model = parameter_model.data(parameter_model.index(0,0), role=AutoParameterModel.SelectionModelRole)
        selection_model.select(model.index(0,0))
        # set values for autoparams
        auto_parameter = parameter_model.data(parameter_model.index(0,0))
        auto_parameter['start'] = start
        auto_parameter['step'] = step
        auto_parameter['stop'] = stop
        auto_parameter['parameter'] = ptype
        print 'AUTO PARAMETER', auto_parameter
        parameter_model.setData(parameter_model.index(0,0), auto_parameter)


    def close_dialog(self):
        dialog = QApplication.activeModalWidget()
        focused = QApplication.focusWidget()
        QTest.keyClicks(focused, self.tempfile)
        QApplication.processEvents()
        QTest.keyClick(dialog, Qt.Key_Enter)
