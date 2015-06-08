import gc
import glob
import json
import logging
import os
import re
import StringIO

import h5py
from nose.tools import assert_equal, assert_in

import qtbot
import test.sample as sample
from sparkle.acq.daq_tasks import get_devices
from sparkle.QtWrapper import QtCore, QtGui, QtTest
from sparkle.data.open import open_acqdata
from sparkle.gui.main_control import MainWindow
from sparkle.gui.stim.abstract_component_editor import AbstractComponentWidget
from sparkle.tools.systools import rand_id

PAUSE = 200
ALLOW = 15

# this should match wha
DEFAULT_TIME_SCALAR = 0.001

class TestMainSetup():
    def setUp(self):
        self.tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), u"tmp")

        log = logging.getLogger('main')
        log.setLevel(logging.DEBUG)
        self.stream = StringIO.StringIO()
        self.handler = logging.StreamHandler(self.stream)
        log.addHandler(self.handler)

    def tearDown(self):
        files = glob.glob(self.tempfolder + os.sep + '[a-zA-Z0-9_]*.hdf5')
        for f in files:
            os.remove(f)
        sample.reset_input_file()

    def test_bad_inputs_file(self):
        fname = os.path.join(self.tempfolder, 'testdatafile.hdf5')
        inputsfile = sample.badinputs()
        self.form = MainWindow(datafile=fname, filemode='w-', inputsFilename=inputsfile)
        self.form.ui.plotDock.close()
        self.form.close()
        QtTest.QTest.qWait(ALLOW)

        # check for any errors
        log = self.stream.getvalue()
        assert 'PROGRAM LOADED' in log

class TestMainUI():
    def setUp(self):
        self.tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), u"tmp")
        fname = os.path.join(self.tempfolder, 'testdatafile' +rand_id()+'.hdf5')
        self.form = MainWindow(datafile=fname, filemode='w-')
        self.form.ui.reprateSpnbx.setValue(10)
        # set AI chan w/o dialog
        devname = get_devices()[0]
        self.form.advanced_options['device_name'] = devname
        self.form._aichans = [devname+'/ai0']
        self.form._aichan_details = {devname+'/ai0': {'threshold': 5, 'polarity': 1, 'raster_bounds':(0.5,0.9), 'abs': True}}
        self.form.reset_device_channels()
        self.form.show()
        # so that the data display doesn't get in the way of out
        # mouse movements
        self.form.ui.plotDock.setFloating(False)
        self.form.showMaximized()
        # shrink font size so whole interface fits on 14" screen
        font = QtGui.QFont()
        font.setPointSize(8)
        QtGui.QApplication.setFont(font)
        QtGui.QApplication.processEvents()

        log = logging.getLogger('main')
        log.setLevel(logging.DEBUG)
        self.stream = StringIO.StringIO()
        self.handler = logging.StreamHandler(self.stream)
        log.addHandler(self.handler)

    def tearDown(self):
        QtGui.QApplication.processEvents()
        if self.form.isVisible():
            self.form.close()
        QtGui.QApplication.closeAllWindows()

        # delete all data files in temp folder -- this will also clear out past
        # test runs that produced errors and did not delete their files
        files = glob.glob(self.tempfolder + os.sep + '[a-zA-Z0-9_]*.hdf5')
        for f in files:
            os.remove(f)

        # check for any errors
        errlog = self.stream.getvalue()
        assert "Error:" not in errlog
        assert "Exception:" not in errlog
        log = logging.getLogger('main')
        log.removeHandler(self.handler)
        self.handler.close()

        # in a effort to improve test isolation, 
        # manually garbage collect after each test
        gc.collect()

    # =====================================
    # Test explore functions
    # =====================================

    def test_tone_explore_defaults(self):
        """The defaults should combine to be a viable set-up"""
        self.explore_run('pure tone')

    def test_vocal_explore(self):
        self.explore_run('vocalization')

    def test_explore_multichannel(self):
        devname = get_devices()[0]
        self.form._aichans = [devname+'/ai0', devname+'/ai1']
        self.form._aichan_details = {devname+'/ai0': {'threshold': 5, 'polarity': 1, 'raster_bounds':(0.5,0.9), 'abs': True},
                                     devname+'/ai1': {'threshold': 5, 'polarity': 1, 'raster_bounds':(0.5,0.9), 'abs': True}}
        self.form.reset_device_channels()
        QtTest.QTest.qWait(ALLOW)
        assert self.form.display.responsePlotCount() == 2
        self.explore_run('pure tone')

        # test setting things on the plots
        for chan in self.form._aichans:
            self.form.display.responsePlots[chan].invertPolarity(True)
            QtTest.QTest.qWait(ALLOW)
            assert self.form._aichan_details[chan]['polarity'] == -1

    # =====================================
    # Test calibration functions
    # ===================================== 

    def test_save_calibration(self):
        """Defaults should be viable"""
        self.form.ui.tabGroup.setCurrentIndex(2)

        qtbot.click(self.form.ui.calibrationWidget.ui.savecalCkbx)
        QtTest.QTest.qWait(ALLOW)

        self.start_acq()

        self.wait_until_done()

        assert self.form.calvals['use_calfile'] == True
        fname = self.form.acqmodel.datafile.filename
        calname = self.form.acqmodel.datafile.calibration_list()[0]

        assert self.form.calvals['calname'] is not None

        # close the UI, and the datafile also closes
        self.form.close()
        # give it a chance to clean up
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

        npts = (self.form.ui.aifsSpnbx.value()*1000)*(self.form.ui.windowszSpnbx.value()*DEFAULT_TIME_SCALAR)
        # print 'data shape', signals.shape, (nreps, npts)
        assert_equal(signals.shape,(nreps, npts))
        assert cal_vector.shape == ((npts/2+1),)
        hfile.close()

    def test_apply_calibration(self):
        self.run_all_apply_cal(True)

    def test_apply_calibration_nocal(self):
        self.run_all_apply_cal(False)

    def test_mphone_calibration(self):
        self.form.ui.tabGroup.setCurrentIndex(2)
        qtbot.click(self.form.ui.mphoneCalBtn)

        QtTest.QTest.qWait(ALLOW)
        self.wait_until_done()

        print self.form.ui.mphoneSensSpnbx.value()
        # doesn't equal default value
        assert self.form.ui.mphoneSensSpnbx.value() != 0.004

    # =====================================
    # Test protocol functions
    # =====================================

    def test_tuning_curve(self):
        
        self.setup_tc()

        assert self.form.acqmodel.protocol_model().rowCount() == 1
        
        self.start_acq()

        # modal dialog will block qt methods in main thread
        qtbot.handle_modal_widget(wait=True)

    def xtest_chart(self):
        # doesnt work, will fix it when I get back to chart dev
        self.setup_tc()

        assert self.form.acqmodel.protocol_model().rowCount() == 1
        qtbot.move(self.form.ui.modeCmbx)
        qtbot.wheel(-1)
        QtTest.QTest.qWait(100)

        self.start_acq()

        assert self.form.ui.stopBtn.isEnabled()

        # modal dialog will block qt methods in main thread
        # qtbot.handle_modal_widget(wait=True, press_enter=False)
        qtbot.handle_modal_widget(wait=True)

        assert not self.form.ui.stopBtn.isEnabled()

    def test_saved_stim(self):
        self.form.ui.tabGroup.setCurrentIndex(1)
        QtGui.QApplication.processEvents()
        pv = self.form.ui.protocolView
        

        # modal dialog will block qt methods in main thread
        # qtbot.handle_modal_widget(sample.test_template(), wait=False)
        qtbot.handle_modal_widget(wait=False, func=msg_enter, args=(sample.test_template(),))

        qtbot.drag(self.form.ui.stimulusChoices.templateLbl, pv)

        QtTest.QTest.qWait(ALLOW)
        self.start_acq()

        # modal dialog will block qt methods in main thread
        # qtbot.handle_modal_widget(wait=True, press_enter=False)
        qtbot.handle_modal_widget(wait=True)

    def test_tone_protocol(self):
        self.protocol_run([('pure tone',{'duration': 10, 'frequency': 22}), ('silence',{'duration': 15})])

    def test_auto_parameter_protocol(self):
        self.protocol_run([('pure tone',{'duration': 66, 'frequency': 22}), ('pure tone',{'duration': 33})],
            [['duration', 10, 50, 10]])

    def test_tone_protocol_multichannel(self):
        devname = get_devices()[0]
        self.form._aichans = [devname+'/ai0', devname+'/ai1']
        self.form._aichan_details = {devname+'/ai0': {'threshold': 5, 'polarity': 1, 'raster_bounds':(0.5,0.9), 'abs': True},
                                     devname+'/ai1': {'threshold': 5, 'polarity': 1, 'raster_bounds':(0.5,0.9), 'abs': True}}
        self.form.reset_device_channels()
        QtTest.QTest.qWait(ALLOW)
        assert self.form.display.responsePlotCount() == 2
        self.protocol_run([('pure tone',{'duration': 10, 'frequency': 22}), ('silence',{'duration': 15})])

    def xtest_stim_detail_sharing(self):
        # disabled... took away this feature.
        # set a value on an explore stimulus
        self.explore_setup('pure tone')

        val = 33
        editor = self.form.ui.exploreStimEditor.ui.trackStack.widget(0).widgetForName('Pure Tone')
        editor.inputWidgets['intensity'].setValue(val)

        # get it to save by running
        self.explore_run()

        # check that a stim component in builder now has the value as 
        # default
        self.form.ui.tabGroup.setCurrentIndex(1)
        stimEditor = self.add_builder_tone()

        stimModel = stimEditor.ui.trackview.model()
        tone = stimModel.data(stimModel.index(0,0))
        print tone.intensity(), val
        assert tone.intensity() == val

        qtbot.click(stimEditor.ui.okBtn)

    def test_reedit_custom_stim(self):
        self.form.ui.tabGroup.setCurrentIndex(1)
        pv = self.form.ui.protocolView

        stimEditor = self.add_builder_tone()
        QtTest.QTest.qWait(ALLOW)
        # edit the same tone again
        qtbot.doubleclick(stimEditor.ui.trackview, stimEditor.ui.trackview.model().index(0,0))
        QtTest.QTest.qWait(ALLOW)
        # change something -- default is duration
        val = 22
        qtbot.type_msg(str(val))
        QtTest.QTest.qWait(ALLOW)

        qtbot.keypress('enter')
        QtTest.QTest.qWait(ALLOW)
        
        stimModel = stimEditor.ui.trackview.model()
        tone = stimModel.data(stimModel.index(0,0))
        # assumes default ms scale
        assert tone.duration() == val*DEFAULT_TIME_SCALAR

        # close editor
        qtbot.click(stimEditor.ui.okBtn)
        QtTest.QTest.qWait(ALLOW)

        # re-open builder, make sure everything is as left it
        qtbot.doubleclick(pv, pv.model().index(0,1))
        QtTest.QTest.qWait(ALLOW*2)
        # need to get new reference to editor -- different instance
        QtGui.QApplication.processEvents()
        stimEditor = pv.stimEditor

        qtbot.doubleclick(stimEditor.ui.trackview, stimEditor.ui.trackview.model().index(0,0))
        QtTest.QTest.qWait(PAUSE)

        # assert the same value as we last set
        tone = stimModel.data(stimModel.index(0,0))
        assert tone.duration() == val*DEFAULT_TIME_SCALAR

        # set a new value to make sure no errors occured
        val = 11
        qtbot.type_msg(str(val))
        QtTest.QTest.qWait(ALLOW*3)
        qtbot.keypress('enter')
        QtTest.QTest.qWait(ALLOW)

        tone = stimModel.data(stimModel.index(0,0), role=QtCore.Qt.UserRole+1)
        assert tone.duration() == val*DEFAULT_TIME_SCALAR

        qtbot.click(stimEditor.ui.okBtn)

    def test_abort_protocol(self):

        self.setup_tc()

        assert self.form.acqmodel.protocol_model().rowCount() == 1

        self.start_acq()

        # make sure we still get a comment box
        t = qtbot.handle_modal_widget(wait=False, func=assert_not_none)

        qtbot.click(self.form.ui.stopBtn)
        
        while t.is_alive():
            QtTest.QTest.qWait(500)

    def test_reorder_protocol(self):
        # I was recieving a pickling error from wrapping the 
        # stimulus components
        self.form.ui.tabGroup.setCurrentIndex(1)
        stimEditor = self.add_builder_tone()
        QtTest.QTest.qWait(ALLOW)
        qtbot.click(stimEditor.ui.okBtn)
        QtTest.QTest.qWait(ALLOW)
        self.setup_tc()

        # now drag the builder to the top
        pv = self.form.ui.protocolView
        qtbot.drag_view(pv, (0,1), (1,1))
        stims = pv.model().stimulusList()
        print stims[1].stimType()
        assert stims[1].stimType() == 'Custom'

    def test_reorder_protocol_multivocal(self):
        # I was recieving a pickling error from wrapping the 
        # stimulus components -- later again with vocal autoparams
        self.form.ui.tabGroup.setCurrentIndex(1)
        stimEditor = self.add_edit_builder()

        qtbot.drag(stimEditor.ui.templateBox.getLabelByName('Vocalization'),
                   stimEditor.ui.trackview)
        QtTest.QTest.qWait(ALLOW)
        vocal_editor = QtGui.QApplication.activeModalWidget()
        fpath = sample.samplewav()
        parentdir, fname = os.path.split(fpath)
        vocal_editor.setRootDirs(parentdir, parentdir)
        QtTest.QTest.qWait(ALLOW)
        QtTest.QTest.qWait(2000)
        qtbot.drag(vocal_editor.filelistView, vocal_editor.filelistView, 
                           vocal_editor.filelistView.model().index(fpath), 
                           vocal_editor.filelistView.model().index(sample.samplewav1()))
        QtTest.QTest.qWait(ALLOW)
        qtbot.keypress('enter')
        QtTest.QTest.qWait(PAUSE)

        qtbot.click(stimEditor.ui.okBtn)
        QtTest.QTest.qWait(ALLOW)

        # throw in a tuning curve too
        self.setup_tc()

        pv = self.form.ui.protocolView
        qtbot.drag_view(pv, (0,1), (1,1))
        QtTest.QTest.qWait(ALLOW)

        assert self.form.acqmodel.protocol_model().rowCount() == 2
        stims = self.form.acqmodel.protocol_model().allTests()
        assert stims[1].stimType() == 'Custom'
        assert stims[1].traceCount() > 1

    def test_edit_stim_after_start(self):
        stimEditor = self.add_builder_tone()

        qtbot.doubleclick(stimEditor.ui.trackview,stimEditor.ui.trackview.model().index(0,0))
        QtTest.QTest.qWait(ALLOW)
        qtbot.type_msg('20')
        qtbot.keypress('enter')
        QtTest.QTest.qWait(ALLOW)
        qtbot.click(stimEditor.ui.okBtn)
        QtTest.QTest.qWait(ALLOW)

        self.setup_tc()
        
        pv = self.form.ui.protocolView
        qtbot.drag(pv, pv, pv.model().index(0,4))
        QtTest.QTest.qWait(500)

        self.start_acq()

        QtTest.QTest.qWait(PAUSE)
        qtbot.doubleclick(pv, pv.model().index(1,1))
        QtTest.QTest.qWait(PAUSE)
        stimEditor = pv.stimEditor
        qtbot.doubleclick(stimEditor.ui.trackview,stimEditor.ui.trackview.model().index(0,0))
        QtTest.QTest.qWait(ALLOW)
        qtbot.type_msg('75')
        qtbot.keypress('enter')
        QtTest.QTest.qWait(ALLOW)
        qtbot.click(stimEditor.ui.okBtn)
        QtTest.QTest.qWait(ALLOW)

        qtbot.handle_modal_widget(wait=True)

        datafile = self.form.acqmodel.datafile
        stim_info = datafile.get_trace_stim('/segment_1/test_2')
        # first stim is control silence, other stim is our tone
        assert stim_info[1]['components'][0]['duration'] == 0.02

    # =====================================
    # Test review of loaded data
    # =====================================
    
    def test_load_data_and_review(self):
        self.form.lf = QtGui.QWidget()
        self.form.loadDataFile(sample.tutorialdata(), 'r')
        
        QtTest.QTest.qWait(PAUSE)

        assert self.form.ui.reviewer.datatable.rowCount() == 5
        
        # 3 should be the index of the first test (after calibration stuff)
        self.check_review_plotting(3,0)

    def test_load_data_and_review_backwards_compatable(self):
        # old data files do not have a channel dimension
        self.form.lf = QtGui.QWidget()
        self.form.loadDataFile(sample.datafile(), 'r')
        
        QtTest.QTest.qWait(PAUSE)

        assert self.form.ui.reviewer.datatable.rowCount() > 0
        
        # 3 should be the index of the first test (after calibration stuff)
        self.check_review_plotting(3,0)


    # =====================================
    # Test other UI stuffs
    # =====================================

    def test_undock_display(self):
        # set display to top tab
        self.form.tabifyDockWidget(self.form.ui.psthDock, self.form.ui.plotDock)
        QtTest.QTest.qWait(ALLOW)
        qtbot.drag(self.form.ui.plotDock.titleBarWidget(), self.form)
        # wait to make sure it doesn't crash
        QtTest.QTest.qWait(1000)

    # =====================================
    # helper functions
    # =====================================

    def setup_tc(self):
        self.form.ui.tabGroup.setCurrentIndex(1)
        QtGui.QApplication.processEvents()
        pv = self.form.ui.protocolView
        
        qtbot.drag(self.form.ui.stimulusChoices.tcLbl, pv)

    def add_builder_tone(self):
        stimEditor = self.add_edit_builder()

        qtbot.drag(stimEditor.ui.templateBox.getLabelByName('Pure Tone'),
                   stimEditor.ui.trackview)
        QtTest.QTest.qWait(PAUSE)
        qtbot.keypress('enter')
        QtTest.QTest.qWait(PAUSE)

        return stimEditor

    def explore_setup(self, comptype):
        self.form.ui.tabGroup.setCurrentIndex(0)
        stimuli = [str(self.form.ui.exploreStimEditor.ui.trackStack.widget(0).exploreStimTypeCmbbx.itemText(i)).lower() for i in xrange(self.form.ui.exploreStimEditor.ui.trackStack.widget(0).exploreStimTypeCmbbx.count())]
        stim_idx = stimuli.index(comptype)
        QtTest.QTest.qWait(ALLOW)
        qtbot.move(self.form.ui.exploreStimEditor.ui.trackStack.widget(0).exploreStimTypeCmbbx)

        # reset the box to the first item
        self.form.ui.exploreStimEditor.ui.trackStack.widget(0).exploreStimTypeCmbbx.setCurrentIndex(0)

        # scroll the mouse the number of ticks equal to it's index
        QtTest.QTest.qWait(PAUSE)
        qtbot.wheel(-1*stim_idx)

        if comptype == 'vocalization':
            # We are going to cheat and set the vocal folders directly
            fpath = sample.samplewav()
            parentdir, fname = os.path.split(fpath)
            editor = self.form.ui.exploreStimEditor.ui.trackStack.widget(0).widgetForName('Vocalization')
            editor.setRootDirs(parentdir, parentdir)
            QtTest.QTest.qWait(200) # needs longer allow
            idx = editor.filemodel.index(fpath)
            # print 'idx of vocal file', idx.row()
            qtbot.click(editor.filelistView, idx)
            QtTest.QTest.qWait(ALLOW)

    def explore_run(self, comptype=None):
        if comptype is not None:
            self.explore_setup(comptype)

        self.start_acq()

        QtTest.QTest.qWait(1000)

        # test ability to switch to off
        self.explore_setup('off')
        self.start_acq()
        QtTest.QTest.qWait(200)

        qtbot.click(self.form.ui.stopBtn)
        QtTest.QTest.qWait(ALLOW)
        assert self.form.ui.runningLabel.text() == "OFF"


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

        # connect signal to catch results
        self.results = []
        if self.form.ui.calibrationWidget.ui.calTypeCmbbx.currentText() == 'Tone Curve':
            self.form.signals.calibration_response_collected.connect(self.collect_cal_data)

        self.start_acq()

        self.wait_until_done()

        if self.form.ui.calibrationWidget.ui.calTypeCmbbx.currentText() == 'Tone Curve':
            nfreqsteps = int(self.form.ui.calibrationWidget.ui.curveWidget.ui.freqNstepsLbl.text())
            ndbsteps = int(self.form.ui.calibrationWidget.ui.curveWidget.ui.dbNstepsLbl.text())
            nreps = self.form.ui.calibrationWidget.ui.nrepsSpnbx.value()
            assert len(self.results) == nfreqsteps*ndbsteps*nreps
            self.form.signals.calibration_response_collected.disconnect(self.collect_cal_data)
           
        # make sure no calibration is present
        assert self.form.calvals['use_calfile'] == withcal
        assert self.form.calvals['calname'] == calname

        # also should not save data
        data_groups = self.form.acqmodel.datafile.keys()
        print 'keys', data_groups
        assert len(data_groups) == 0


    def collect_cal_data(self, spectrum, freq, vamp):
        self.results.append(spectrum)

    def add_edit_builder(self):
        # add a custom stimulus and opens its editor
        self.form.ui.tabGroup.setCurrentIndex(1)

        QtGui.QApplication.processEvents()
        pv = self.form.ui.protocolView
        
        qtbot.drag(self.form.ui.stimulusChoices.builderLbl, pv)

        assert self.form.acqmodel.protocol_model().rowCount() > 0

        qtbot.doubleclick(pv, pv.model().index(0,1))
        QtTest.QTest.qWait(PAUSE)

        assert hasattr(pv, 'stimEditor')

        return pv.stimEditor

    def setup_builder_components(self, components):

        stimEditor = self.add_edit_builder()

        for comp in components:
            name = comp[0]
            vals = comp[1]
            qtbot.drag(stimEditor.ui.templateBox.getLabelByName(name), stimEditor.ui.trackview)
            self.set_paramters(name, vals)
            qtbot.keypress('enter')
            QtTest.QTest.qWait(ALLOW)


        assert stimEditor.ui.trackview.model().componentCount() == len(components)
        # pause neccessary for stims to update their visual rects,
        # to allow the following code to work
        QtTest.QTest.qWait(PAUSE) 

        if len(components) == 2:
            qtbot.reorder_view(stimEditor.ui.trackview, (1,0), (0,1))
            print stimEditor.ui.trackview.model().duration(),  sum([x[1]['duration'] for x in components])/1000.
            assert stimEditor.ui.trackview.model().duration() == sum([x[1]['duration'] for x in components])/1000.

        return stimEditor

    def protocol_run(self, components, autoparams={}):
        stimEditor = self.setup_builder_components(components)

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

        stimEditor.ui.nrepsSpnbx.setValue(3)
        
        # just use default tone settings, for now at least
        qtbot.click(stimEditor.ui.okBtn)
        QtTest.QTest.qWait(ALLOW)

        # extract StimulusModel
        stim = self.form.acqmodel.protocol_model().test(0)
        assert stim.autoParams().nrows() == len(autoparams)
        
        # set the window size to stim len + 100ms
        qtbot.doubleclick(self.form.ui.windowszSpnbx)
        qtbot.type_msg(stim.duration()*1000+100)

        signals, docs, overloads = stim.expandedStim()
        # check the first two, make sure they are not the same
        if len(autoparams) > 0:
            key = autoparams[0][0]
            assert docs[0]['components'][0][key] != docs[1]['components'][0][key]

        self.start_acq()

        # modal dialog will block qt methods in main thread
        # qtbot.handle_modal_widget(wait=True, press_enter=False)
        qtbot.handle_modal_widget(wait=True)

        # check that data reviewer updated
        nrows = self.form.ui.reviewer.datatable.rowCount()
        assert nrows == 1
        assert 'segment_1/test_1' in str(self.form.ui.reviewer.datatable.item(0,0).text())

        # check that our saved data has the correct dimensions according
        # to current settings on the UI
        nchans = int(self.form.ui.chanNumLbl.text())
        nsamples = int(self.form.ui.aifsSpnbx.value() * self.form.ui.windowszSpnbx.value())
        # gross, reach into model to get # of reps and traces
        nreps = self.form.ui.protocolView.model().data(self.form.ui.protocolView.model().index(0,2,QtCore.QModelIndex()), QtCore.Qt.DisplayRole)
        ntraces = self.form.ui.protocolView.model().data(self.form.ui.protocolView.model().index(0,3,QtCore.QModelIndex()), QtCore.Qt.DisplayRole) + 1 #+1 for control
        assert self.form.acqmodel.datafile.get_data('segment_1/test_1').shape == (ntraces, nreps, nchans, nsamples)

        self.check_review_plotting(0,0)
        
        # clear data out of current plots, so we know that the review data is showing
        # not left-overs from acquisition
        self._aichans = []
        self.form.reset_device_channels()

        assert self.form.display.responsePlotCount() == nchans

    def check_review_plotting(self, row, col):
        # clear data out of current plots, so we know that the review data is showing
        # not left-overs from acquisition
        self._aichans = []
        self.form.reset_device_channels()

        # check that review data is browseable
        self.form.ui.tabGroup.setCurrentIndex(3)
        QtTest.QTest.qWait(ALLOW)
        qtbot.click(self.form.ui.reviewer.btngrp.button(1))
        QtTest.QTest.qWait(ALLOW)
        qtbot.click(self.form.ui.reviewer.datatable, self.form.ui.reviewer.datatable.model().index(row,col, QtCore.QModelIndex()))
        QtTest.QTest.qWait(ALLOW)

        test_info = self.form.ui.reviewer.derivedtxt.toPlainText()
        # pull out text dimension string from attributes text
        dim_match = re.search('Dataset dimensions : \(([\d, ]+)\)', test_info)
        assert dim_match is not None
        dims = [int(x) for x in dim_match.groups(0)[0].split(', ')]
        if len(dims) == 3:
            nchans = 1
        elif len(dims) == 4:
            nchans = dims[2]
        else:
            assert False, 'invalid number of data dimensions'

        nsamples = dims[-1]
        nreps = dims[1]

        assert self.form.ui.reviewer.tracetable.rowCount() > 0
        qtbot.click(self.form.ui.reviewer.tracetable, self.form.ui.reviewer.tracetable.model().index(0,0,QtCore.QModelIndex()))

        QtTest.QTest.qWait(ALLOW)
        assert self.form.display.responsePlotCount() == nchans

        # cheat, intimate knowledge of plot structure
        for plot in self.form.display.responsePlots.values():
            x, y = plot.tracePlot.getData()
            assert x.shape == (nsamples,)
            assert max(y) > 0

        # check overlay of spikes functionality
        qtbot.click(self.form.ui.reviewer.overlayButton)
        QtTest.QTest.qWait(ALLOW)

        for plot in self.form.display.responsePlots.values():
            assert len(plot.trace_stash) == nreps

    def wait_until_done(self):
        while self.form.ui.runningLabel.text() == "RECORDING":
            QtTest.QTest.qWait(500)

        assert self.form.ui.runningLabel.text() == "OFF"

    def set_paramters(self, name, vals):
        # find an editor and set the parameters
        topWidgets = QtGui.QApplication.topLevelWidgets()
        editors = [w for w in topWidgets if isinstance(w, AbstractComponentWidget)]
        assert len(editors) == 1
        editor = editors[0]
        QtTest.QTest.qWait(ALLOW)
        for field, val in vals.items():
            # input_pos = qttools.center(editor.inputWidgets[field])
            # robot.doubleclick(input_pos)
            # robot.type(str(val))
            # qtbot.doubleclick(editor.inputWidgets[field])
            qtbot.click(editor.inputWidgets[field])
            qtbot.key_combo('ctrl', 'a')
            QtTest.QTest.qWait(ALLOW)
            print 'attempting to enter', val
            qtbot.type_msg(val)
            QtTest.QTest.qWait(PAUSE)

    def set_fake_calibration(self):
        manager = self.form.acqmodel
        # cheat and pretend we already did a calibration
        frange = [5000, 100000]
        cal_data_file = open_acqdata(sample.calibration_filename(), filemode='r')
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

    def start_acq(self):
        qtbot.click(self.form.ui.startBtn)
        QtTest.QTest.qWait(ALLOW)
        assert self.form.ui.runningLabel.text() == "RECORDING"
        QtTest.QTest.qWait(PAUSE)
        log_msg = self.form.ui.logTxedt.toPlainText()
        assert 'Uncaught Exception' not in log_msg

def msg_enter(widget, msg):
    qtbot.type_msg(msg)
    qtbot.keypress('enter')

def assert_not_none(item):
    assert item is not None
    qtbot.click(item.ui.okBtn)
