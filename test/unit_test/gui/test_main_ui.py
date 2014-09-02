import os, glob
import json

import h5py
from nose.tools import assert_in, assert_equal
from PyQt4 import QtGui, QtCore, QtTest

from spikeylab.gui.control import MainWindow
from spikeylab.data.dataobjects import AcquisitionData
from spikeylab.gui.stim.abstract_parameters import AbstractParameterWidget
from spikeylab.tools.systools import rand_id

import test.sample as sample
import qtbot

PAUSE = 200
ALLOW = 15

class TestMainSetup():
    def setUp(self):
        self.tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), u"tmp")

    def tearDown(self):
        files = glob.glob(self.tempfolder + os.sep + '[a-zA-Z0-9_]*.hdf5')
        for f in files:
            os.remove(f)

    def test_bad_inputs_file(self):
        fname = os.path.join(self.tempfolder, 'testdatafile.hdf5')
        inputsfile = sample.badinputs()
        self.form = MainWindow(datafile=fname, filemode='w', inputsFilename=inputsfile)
        self.form.close()
        # so no errors?

class TestMainUI():
    def setUp(self):
        self.tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), u"tmp")
        fname = os.path.join(self.tempfolder, 'testdatafile' +rand_id()+'.hdf5')
        self.form = MainWindow(datafile=fname, filemode='w')
        self.form.ui.reprateSpnbx.setValue(10)
        self.form.show()
        # so that the data display doesn't get in the way of out
        # mouse movements
        self.form.ui.plotDock.close()
        self.form.showMaximized()
        QtGui.QApplication.processEvents()

    def tearDown(self):
        self.form.close()
        QtGui.QApplication.closeAllWindows()

        # delete all data files in temp folder -- this will also clear out past
        # test runs that produced errors and did not delete their files
        files = glob.glob(self.tempfolder + os.sep + '[a-zA-Z0-9_]*.hdf5')
        for f in files:
            os.remove(f)

    def test_tone_explore_defaults(self):
        """The defaults should combine to be a viable set-up"""
        self.explore_run('pure tone')

    def test_vocal_explore(self):
        self.explore_run('vocalization')

    def test_save_calibration(self):
        """Defaults should be viable"""
        self.form.ui.tabGroup.setCurrentIndex(2)

        qtbot.click(self.form.ui.calibrationWidget.ui.savecalCkbx)
        QtTest.QTest.qWait(ALLOW)
        
        qtbot.click(self.form.ui.startBtn)
        QtTest.QTest.qWait(ALLOW)
        assert self.form.ui.runningLabel.text() == "RECORDING"

        self.wait_until_done()

        assert self.form.calvals['use_calfile'] == True
        fname = self.form.acqmodel.datafile.filename
        calname = self.form.acqmodel.datafile.calibration_list()[0]

        assert self.form.calvals['calname'] is not None

        # close the UI, and the datafile also closes
        self.form.close()
        # give it a change to clean up
        QtTest.QTest.qWait(1000)

        # now check saved data
        hfile = h5py.File(fname, 'r')
        signals = hfile[calname]['signal']
        stim = json.loads(signals.attrs['stim'])
        cal_vector = hfile[calname]['calibration_intensities']

        # make sure displayed counts jive with saved file
        nreps = self.form.ui.calibrationWidget.ui.nrepsSpnbx.value()
        assert_in('components', stim[0])
        assert_equal(stim[0]['samplerate_da'], hfile[calname].attrs['samplerate_ad'])

        npts = (self.form.ui.aisrSpnbx.value()*self.form.fscale)*(self.form.ui.windowszSpnbx.value()*self.form.tscale)
        # print 'data shape', signals.shape, (nreps, npts)
        assert_equal(signals.shape,(nreps, npts))
        assert cal_vector.shape == ((npts/2+1),)
        hfile.close()

    def test_apply_calibration(self):
        self.run_all_apply_cal(True)

    def test_apply_calibration_nocal(self):
        self.run_all_apply_cal(False)

    def run_all_apply_cal(self, withcal):
        self.form.ui.tabGroup.setCurrentIndex(2)
        QtTest.QTest.qWait(ALLOW)

        qtbot.click(self.form.ui.calibrationWidget.ui.applycalCkbx)
        QtTest.QTest.qWait(ALLOW)

        # test for each option available
        for i in range(self.form.ui.calibrationWidget.ui.calTypeCmbbx.count()):
            self.run_apply_cal(withcal)
            qtbot.move(self.form.ui.calibrationWidget.ui.calTypeCmbbx)
            qtbot.wheel(-1)
            QtTest.QTest.qWait(100)

    def run_apply_cal(self, withcal):
        if withcal:
            self.set_fake_calibration()
            assert self.form.calvals['calname'] != ''

        calname = self.form.calvals['calname']
        assert self.form.calvals['use_calfile'] == withcal

        qtbot.click(self.form.ui.startBtn)
        QtTest.QTest.qWait(ALLOW)
        assert self.form.ui.runningLabel.text() == "RECORDING"

        self.wait_until_done()

        # make sure no calibration is present
        assert self.form.calvals['use_calfile'] == withcal
        assert self.form.calvals['calname'] == calname

    def test_tuning_curve(self):
        
        self.setup_tc()

        assert self.form.acqmodel.protocol_model().rowCount() == 1

        qtbot.click(self.form.ui.startBtn)
        QtTest.QTest.qWait(ALLOW)
        assert self.form.ui.runningLabel.text() == "RECORDING"

        # modal dialog will block qt methods in main thread
        qtbot.handle_modal_widget(wait=True, press_enter=False)

    def xtest_chart(self):
        # doesnt work, will fix it when I get back to chart dev
        self.setup_tc()

        assert self.form.acqmodel.protocol_model().rowCount() == 1
        qtbot.move(self.form.ui.modeCmbx)
        qtbot.wheel(-1)
        QtTest.QTest.qWait(100)

        qtbot.click(self.form.ui.startBtn)

        QtTest.QTest.qWait(ALLOW)
        assert self.form.ui.runningLabel.text() == "RECORDING"
        assert self.form.ui.stopBtn.isEnabled()

        # modal dialog will block qt methods in main thread
        qtbot.handle_modal_widget(wait=True, press_enter=False)

        assert not self.form.ui.stopBtn.isEnabled()

    def setup_tc(self):
        self.form.ui.tabGroup.setCurrentIndex(1)
        QtGui.QApplication.processEvents()
        pv = self.form.ui.protocolView
        
        qtbot.drag(self.form.ui.stimulusChoices.tcLbl, pv)

    def test_saved_stim(self):
        self.form.ui.tabGroup.setCurrentIndex(1)
        QtGui.QApplication.processEvents()
        pv = self.form.ui.protocolView
        

        # modal dialog will block qt methods in main thread
        qtbot.handle_modal_widget(sample.test_template(), wait=False)

        qtbot.drag(self.form.ui.stimulusChoices.templateLbl, pv)

        QtTest.QTest.qWait(ALLOW)
        qtbot.click(self.form.ui.startBtn)
        QtTest.QTest.qWait(ALLOW)
        assert self.form.ui.runningLabel.text() == "RECORDING"

        # modal dialog will block qt methods in main thread
        qtbot.handle_modal_widget(wait=True, press_enter=False)

    def test_tone_protocol(self):
        self.protocol_run([('pure tone',{'duration': 10, 'frequency': 22}), ('silence',{'duration': 15})])

    def test_auto_parameter_protocol(self):
        self.protocol_run([('pure tone',{'duration': 66, 'frequency': 22}), ('pure tone',{'duration': 33})],
            [['duration', 10, 50, 10]])

    def explore_run(self, comptype):
        self.form.ui.tabGroup.setCurrentIndex(0)
        stimuli = [str(self.form.ui.exploreStimTypeCmbbx.itemText(i)).lower() for i in xrange(self.form.ui.exploreStimTypeCmbbx.count())]
        tone_idx = stimuli.index(comptype)
        qtbot.move(self.form.ui.exploreStimTypeCmbbx)

        # scroll the mouse the number of ticks equal to it's index
        QtTest.QTest.qWait(1000)
        qtbot.wheel(-1*tone_idx)

        if comptype == 'vocalization':
            # We are going to cheat and set the vocal folders directly
            fpath = sample.samplewav()
            parentdir, fname = os.path.split(fpath)
            self.form.exvocal.setRootDirs(parentdir, parentdir)
            QtTest.QTest.qWait(200) # needs longer allow
            idx = self.form.exvocal.filemodel.index(fpath)
            # print 'idx of vocal file', idx.row()
            qtbot.click(self.form.exvocal.filelistView, idx)
            QtTest.QTest.qWait(ALLOW)

        qtbot.click(self.form.ui.startBtn)
        QtTest.QTest.qWait(ALLOW)
        assert self.form.ui.runningLabel.text() == "RECORDING"
        QtTest.QTest.qWait(1000)
        qtbot.click(self.form.ui.stopBtn)
        QtTest.QTest.qWait(ALLOW)
        assert self.form.ui.runningLabel.text() == "OFF"

    def protocol_run(self, components, autoparams={}):
        self.form.ui.tabGroup.setCurrentIndex(1)

        QtGui.QApplication.processEvents()
        pv = self.form.ui.protocolView
        
        qtbot.drag(self.form.ui.stimulusChoices.builderLbl, pv)

        assert self.form.acqmodel.protocol_model().rowCount() == 1

        qtbot.doubleclick(pv, pv.model().index(0,1))
        QtTest.QTest.qWait(PAUSE)

        assert hasattr(pv, 'stimEditor')

        stimEditor = pv.stimEditor
        for comp in components:
            name = comp[0]
            vals = comp[1]
            qtbot.drag(stimEditor.ui.templateBox.getLabelByName(name), stimEditor.ui.trackview)
            self.set_paramters(name, vals)
            qtbot.keypress('enter')

        assert stimEditor.ui.trackview.model().componentCount() == len(components)
        # pause neccessary for stims to update their visual rects,
        # to allow the following code to work
        QtTest.QTest.qWait(PAUSE) 

        if len(components) == 2:
            qtbot.reorder_view(stimEditor.ui.trackview, (1,0), (0,1))
            assert stimEditor.ui.trackview.model().duration() == sum([x[1]['duration'] for x in components])/1000.

        qtbot.click(stimEditor.ui.parametizer.hideBtn)
        QtGui.QApplication.processEvents()
        QtTest.QTest.qWait(PAUSE)

        pztr = stimEditor.ui.parametizer.parametizer

        for i, param in enumerate(autoparams):
            qtbot.drag(pztr.addLbl,pztr.paramList)
            # just select first component
            QtTest.QTest.qWait(PAUSE)
            qtbot.click(stimEditor.ui.trackview, stimEditor.ui.trackview.model().index(0,0))
            # fill in auto  parameter
            for j, param_item in enumerate(param):
                # click the field
                qtbot.click(pztr.paramList, pztr.paramList.model().index(i,j))
                qtbot.type_msg(param_item)
                QtTest.QTest.qWait(PAUSE)

        qtbot.keypress('enter')
        QtGui.QApplication.processEvents()
        QtTest.QTest.qWait(PAUSE)
        # just use default tone settings, for now at least
        qtbot.click(stimEditor.ui.okBtn)

        # extract StimulusModel
        stim = self.form.acqmodel.protocol_model().test(0)
        assert stim.autoParams().nrows() == len(autoparams)
        
        # set the window size to stim len + 100ms
        qtbot.doubleclick(self.form.ui.windowszSpnbx)
        qtbot.type_msg(stim.duration()*1000+100)

        qtbot.click(self.form.ui.startBtn)
        QtTest.QTest.qWait(ALLOW)
        assert self.form.ui.runningLabel.text() == "RECORDING"

        # modal dialog will block qt methods in main thread
        qtbot.handle_modal_widget(wait=True, press_enter=False)

    def wait_until_done(self):
        while self.form.ui.runningLabel.text() == "RECORDING":
            QtTest.QTest.qWait(500)

        assert self.form.ui.runningLabel.text() == "OFF"

    def set_paramters(self, name, vals):
        # find an editor and set the parameters
        topWidgets = QtGui.QApplication.topLevelWidgets()
        editors = [w for w in topWidgets if isinstance(w, AbstractParameterWidget)]
        assert len(editors) == 1
        editor = editors[0]
        for field, val in vals.items():
            # input_pos = qttools.center(editor.inputWidgets[field])
            # robot.doubleclick(input_pos)
            # robot.type(str(val))
            qtbot.doubleclick(editor.inputWidgets[field])
            qtbot.type_msg(val)
            QtTest.QTest.qWait(PAUSE)

    def set_fake_calibration(self):
        manager = self.form.acqmodel
        # cheat and pretend we already did a calibration
        frange = [5000, 100000]
        cal_data_file = AcquisitionData(sample.calibration_filename(), filemode='r')
        calname = cal_data_file.calibration_list()[0]
        calibration_vector, calibration_freqs = cal_data_file.get_calibration(calname, reffreq=15000)
        manager.explorer.set_calibration(calibration_vector, calibration_freqs, frange, calname)
        manager.protocoler.set_calibration(calibration_vector, calibration_freqs, frange, calname)
        manager.charter.set_calibration(calibration_vector, calibration_freqs, frange, calname)
        manager.bs_calibrator.stash_calibration(calibration_vector, calibration_freqs, frange, calname)
        manager.tone_calibrator.stash_calibration(calibration_vector, calibration_freqs, frange, calname)

        # append a string so that we can tell if a new calibration with the same name is saved
        self.form.calvals['calname'] = calname + 'fake'
        self.form.calvals['use_calfile'] = True