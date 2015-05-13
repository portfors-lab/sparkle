import os

import numpy as np
import yaml
from nose.tools import assert_equal, raises

import test.sample as sample
from sparkle.QtWrapper import QtCore, QtGui
from sparkle.gui.stim.factory import CCFactory, TCFactory
from sparkle.gui.stim.qstimulus import QStimulusModel
from sparkle.gui.stim.stimulus_editor import StimulusEditor
from sparkle.stim.auto_parameter_model import AutoParameterModel
from sparkle.stim.reorder import order_function
from sparkle.stim.stimulus_model import StimulusModel
from sparkle.stim.types.stimuli_classes import PureTone, Vocalization
from sparkle.tools.systools import get_src_directory

src_dir = get_src_directory()
with open(os.path.join(src_dir,'settings.conf'), 'r') as yf:
    config = yaml.load(yf)
USE_RMS = config['use_rms']

class TestQStimModel():
    def test_insert_data(self):
        data = StimulusModel()
        model = QStimulusModel(data)
        fake_component0 = PureTone()
        fake_component1 = Vocalization()

        model.insertComponent(model.createIndex(0, 0, fake_component0), fake_component0)
        model.insertComponent(model.createIndex(0, 0, fake_component1), fake_component1)
        assert model.data(model.index(0,0), role=QtCore.Qt.UserRole+1) == fake_component1
        assert model.data(model.index(0,1), role=QtCore.Qt.UserRole+1) == fake_component0

    def test_remove_data(self):
        data = StimulusModel()
        model = QStimulusModel(data)
        fake_component0 = PureTone()
        index = model.createIndex(0, 0, fake_component0)
        model.insertComponent(index, fake_component0)
        model.removeComponent(index)
        assert model.data(model.index(0,0), role=QtCore.Qt.UserRole) == None

    def test_component_index(self):
        data = StimulusModel()
        model = QStimulusModel(data)
        fake_component0 = PureTone()
        # component will be added to the lowest index in row
        model.insertComponent(model.createIndex(0, 2, fake_component0), fake_component0)
        index = model.indexByComponent(fake_component0)
        assert (index.row(),index.column()) == (0,0)

    @raises(IndexError)
    def test_set_data(self):
        data = StimulusModel()
        model = QStimulusModel(data)
        fake_component0 = PureTone()
        model.setData(model.index(0,0), fake_component0)

    def test_row_column_count(self):
        data = StimulusModel()
        model = QStimulusModel(data)
        fake_component0 = PureTone()
        assert model.columnCountForRow(0) == 0
        assert model.rowCount() == 0
        model.insertComponent(model.createIndex(0, 0, fake_component0), fake_component0)
        assert model.columnCountForRow(0) == 1
        assert model.rowCount() == 1

    def test_trace_count_no_auto(self):
        data = StimulusModel()
        model = QStimulusModel(data)
        component0 = PureTone()
        component1 = PureTone()
        model.insertComponent(model.createIndex(0, 0, component0), component0)
        model.insertComponent(model.createIndex(0, 0, component1), component1)

        assert model.traceCount() == 1

    def test_trace_count_no_components(self):
        data = StimulusModel()
        self.add_auto_param(data)        
        model = QStimulusModel(data)

        assert model.traceCount() == 0

    def test_template_with_autoparams(self):
        data = StimulusModel()
        model = QStimulusModel(data)
        component =  PureTone()
        model.insertComponent(model.createIndex(0, 0, component), component)
        self.add_auto_param(data) 

        model.setEditor(StimulusEditor)
        template = model.templateDoc()

        clone = QStimulusModel.loadFromTemplate(template)

        assert clone.editor.name == model.editor.name
        assert clone.traceCount() == model.traceCount()

    def test_template_tuning_curve(self):
        tcf = TCFactory()
        data = tcf.create()
        model = QStimulusModel(data)
        model.setEditor(tcf.editor())

        template = model.templateDoc()

        clone = QStimulusModel.loadFromTemplate(template)
        assert clone.editor.name == model.editor.name
        assert clone.traceCount() == model.traceCount()


    def test_verify_with_bad_frequency_auto_parameter_disallowed(self):
        component = PureTone()
        stim_model = StimulusModel()
        stim_model.setReferenceVoltage(100, 0.1)
        stim_model.insertComponent(component, 0,0)

        model = QStimulusModel(stim_model)

        ap_model = model.autoParams()
        ap_model.insertRows(0,1)
        ap_model.toggleSelection(ap_model.index(0,0), component)
        
        # setData always deals with base units
        values = ['frequency', 100000, 300000, 25000]
        for i, value in enumerate(values):
            ap_model.setData(ap_model.index(0,i), value, QtCore.Qt.EditRole)

        invalid = stim_model.verify(windowSize=0.1)
        print 'msg', invalid
        assert invalid == 0
        assert stim_model.containsPval('frequency', 75000)

    def add_auto_param(self, model):
        # adds an autoparameter to the given model
        ptype = 'intensity'
        start = 0
        step = 1
        stop = 3

        parameter_model = model.autoParams()
        parameter_model.insertRow(0)
        # select first component
        parameter_model.toggleSelection(0, model.component(0,0))
        # set values for autoparams
        parameter_model.setParamValue(0, start=start, step=step, 
                                      stop=stop, parameter=ptype)

        # parameter_model = model.autoParams()
        # parameter_model.insertRows(0,1)
        # auto_parameter = parameter_model.data(parameter_model.index(0,0))
        # auto_parameter['start'] = start
        # auto_parameter['step'] = step
        # auto_parameter['stop'] = stop
        # parameter_model.setData(parameter_model.index(0,0), auto_parameter)

        return len(range(start,stop,step)) + 1
