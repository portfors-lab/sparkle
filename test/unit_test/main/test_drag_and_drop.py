from spikeylab.main.control import MainWindow
from spikeylab.stim.factory import BuilderFactory, TCFactory
from spikeylab.stim.auto_parameter_view import AddLabel
from spikeylab.main.drag_label import DragLabel
from spikeylab.stim.types.stimuli_classes import PureTone
from spikeylab.data.dataobjects import AcquisitionData
from spikeylab.stim.abstract_parameters import AbstractParameterWidget
from test.util import robot, qttools

import sys 
import time, os, glob
import json
import threading

import h5py
from nose.tools import assert_in, assert_equal

from PyQt4 import QtGui, QtCore, QtTest

import test.sample as sample

PAUSE = 200
ALLOW = 15

app = None
def setUp():
    global app
    app = QtGui.QApplication(sys.argv)

def tearDown():
    global app
    app.exit(0)

class TestDragNDrop():
    def setUp(self):
        self.tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), u"tmp")
        fname = os.path.join(self.tempfolder, 'testdatafile.hdf5')
        self.form = MainWindow(datafile=fname, filemode='w')
        self.form.ui.reprateSpnbx.setValue(10)
        self.form.show()
        # so that the data display doesn't get in the way of out
        # mouse movements
        self.form.ui.plotDock.close()
        self.form.showMaximized()

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
        # We are going to cheat and set the vocal folders directly
        fpath = sample.samplewav()
        parentdir, fname = os.path.split(fpath)
        self.form.exvocal.setRootDirs(parentdir, parentdir)
        QtTest.QTest.qWait(PAUSE)    
        QtTest.QTest.qWait(ALLOW)
        idx = self.form.exvocal.filemodel.index(fpath)
        print 'idx of vocal file', idx.row()
        pos = qttools.center(self.form.exvocal.filelistView.visualRect(idx), self.form.exvocal.filelistView.viewport())
        print 'pos of file', pos
        robot.click(pos)
        # self.form.exvocal.currentWavFile = fname
        QtTest.QTest.qWait(PAUSE)    

        self.explore_run('vocalization')

    def test_save_calibration(self):
        """Defaults should be viable"""
        self.form.ui.tabGroup.setCurrentIndex(2)
        robot.click(qttools.hotspot(self.form.ui.calibrationWidget.ui.savecalCkbx))
        QtTest.QTest.qWait(ALLOW)
        
        robot.click(qttools.center(self.form.ui.startBtn))
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
        stim = json.loads(hfile[calname].attrs['stim'])
        cal_vector = hfile[calname]['calibration_intensities']

        # make sure displayed counts jive with saved file
        nreps = self.form.ui.calibrationWidget.ui.nrepsSpnbx.value()
        assert_in('components', stim[0])
        assert_equal(stim[0]['samplerate_da'], hfile[calname].attrs['samplerate_ad'])

        npts = (self.form.ui.aisrSpnbx.value()*self.form.fscale)*(self.form.ui.windowszSpnbx.value()*self.form.tscale)
        print 'data shape', signals.shape, (nreps, npts)
        assert_equal(signals.shape,(nreps, npts))
        assert cal_vector.shape == ((npts/2+1),)
        hfile.close()

    def test_apply_calibration(self):
        self.run_all_apply_cal(True)

    def test_apply_calibration_nocal(self):
        self.run_all_apply_cal(False)

    def run_all_apply_cal(self, withcal):
        self.form.ui.tabGroup.setCurrentIndex(2)
        robot.click(qttools.hotspot(self.form.ui.calibrationWidget.ui.applycalCkbx))
        QtTest.QTest.qWait(ALLOW)
        
        # test for each option available
        for i in range(self.form.ui.calibrationWidget.ui.calTypeCmbbx.count()):
            self.run_apply_cal(withcal)
            robot.move(qttools.center(self.form.ui.calibrationWidget.ui.calTypeCmbbx))
            robot.mousewheel(-1)
            QtTest.QTest.qWait(100)

    def run_apply_cal(self, withcal):
        if withcal:
            self.set_fake_calibration()
            assert self.form.calvals['calname'] != ''

        calname = self.form.calvals['calname']
        assert self.form.calvals['use_calfile'] == withcal

        robot.click(qttools.center(self.form.ui.startBtn))
        QtTest.QTest.qWait(ALLOW)
        assert self.form.ui.runningLabel.text() == "RECORDING"

        self.wait_until_done()

        # make sure no calibration is present
        assert self.form.calvals['use_calfile'] == withcal
        assert self.form.calvals['calname'] == calname

    def test_tuning_curve(self):
        
        self.setup_tc()

        assert self.form.acqmodel.protocol_model().rowCount() == 1

        robot.click(qttools.center(self.form.ui.startBtn))
        QtTest.QTest.qWait(ALLOW)
        assert self.form.ui.runningLabel.text() == "RECORDING"

        # modal dialog will block qt methods in main thread
        dialogthread = threading.Thread(target=self.close_modal)
        dialogthread.start()

        self.wait_until_done()

    def xtest_chart(self):
        # doesnt work, will fix it when I get back to chart dev
        self.setup_tc()

        assert self.form.acqmodel.protocol_model().rowCount() == 1
        robot.move(qttools.center(self.form.ui.modeCmbx))
        robot.mousewheel(-1)
        QtTest.QTest.qWait(100)

        robot.click(qttools.center(self.form.ui.startBtn))
        QtTest.QTest.qWait(ALLOW)
        assert self.form.ui.runningLabel.text() == "RECORDING"
        assert self.form.ui.stopBtn.isEnabled()

        # modal dialog will block qt methods in main thread
        dialogthread = threading.Thread(target=self.close_modal)
        dialogthread.start()

        self.wait_until_done()
        assert not self.form.ui.stopBtn.isEnabled()

    def setup_tc(self):
        self.form.ui.tabGroup.setCurrentIndex(1)
        QtGui.QApplication.processEvents()
        pv = self.form.ui.protocolView
        
        label_pos = qttools.center(self.form.ui.stimulusChoices.tcLbl)
        protocol_pos = qttools.center(pv)

        self.drag(label_pos, protocol_pos)

    def test_saved_stim(self):
        self.form.ui.tabGroup.setCurrentIndex(1)
        QtGui.QApplication.processEvents()
        pv = self.form.ui.protocolView
        
        label_pos = qttools.center(self.form.ui.stimulusChoices.templateLbl)
        protocol_pos = qttools.center(pv)

        # modal dialog will block qt methods in main thread
        dialogthread = threading.Thread(target=self.handle_file_dialog, args=(sample.test_template(),))
        dialogthread.start()

        self.drag(label_pos, protocol_pos)

        robot.click(qttools.center(self.form.ui.startBtn))
        QtTest.QTest.qWait(ALLOW)
        assert self.form.ui.runningLabel.text() == "RECORDING"

        # modal dialog will block qt methods in main thread
        dialogthread = threading.Thread(target=self.close_modal)
        dialogthread.start()

        self.wait_until_done()

    def handle_file_dialog(self, fpath):
        dialogs = []
        folder, name = os.path.split(fpath)
        while len(dialogs) == 0:
            print 'searching'
            topWidgets = QtGui.QApplication.topLevelWidgets()
            dialogs = [w for w in topWidgets if isinstance(w, QtGui.QDialog)]
            time.sleep(1)
        # print 'found dialogs', dialogs
        # don't know why but dialog doesn't register as a QFileDialog
        # dialogs[0].setDirectory(folder)
        # dialogs[0].selectFile(name)
        robot.type(fpath)
        robot.keypress('enter')

    def test_tone_protocol(self):
        self.protocol_run([('pure tone',{'duration': 10, 'frequency': 22}), ('silence',{'duration': 15})])

    def test_auto_parameter_protocol(self):
        self.protocol_run([('pure tone',{'duration': 66, 'frequency': 22}), ('pure tone',{'duration': 33})],
            [['duration', 10, 50, 10]])

    def explore_run(self, comptype):
        self.form.ui.tabGroup.setCurrentIndex(0)
        stimuli = [self.form.ui.exploreStimTypeCmbbx.itemText(i).lower() for i in xrange(self.form.ui.exploreStimTypeCmbbx.count())]
        tone_idx = stimuli.index(comptype)
        # robot.click(qttools.center(self.form.ui.exploreStimTypeCmbbx))
        robot.move(qttools.center(self.form.ui.exploreStimTypeCmbbx))
        # scroll the mouse the number of ticks equal to it's index
        QtTest.QTest.qWait(1000)
        # neccessary to space out mouse wheel increments
        for i in range(tone_idx):
            robot.mousewheel(-1)
            QtTest.QTest.qWait(100)

        robot.click(qttools.center(self.form.ui.startBtn))
        QtTest.QTest.qWait(ALLOW)
        assert self.form.ui.runningLabel.text() == "RECORDING"
        QtTest.QTest.qWait(1000)
        robot.click(qttools.center(self.form.ui.stopBtn))
        QtTest.QTest.qWait(ALLOW)
        assert self.form.ui.runningLabel.text() == "OFF"

    def protocol_run(self, components, autoparams={}):
        self.form.ui.tabGroup.setCurrentIndex(1)

        QtGui.QApplication.processEvents()
        pv = self.form.ui.protocolView
        
        label_pos = qttools.center(self.form.ui.stimulusChoices.builderLbl)
        protocol_pos = qttools.center(pv)

        self.drag(label_pos, protocol_pos)

        assert self.form.acqmodel.protocol_model().rowCount() == 1

        item_pos = qttools.center(pv.visualRect(pv.model().index(0,1)), pv.viewport())
        robot.doubleclick(item_pos)
        QtTest.QTest.qWait(PAUSE)

        assert hasattr(pv, 'stimEditor')

        stimEditor = pv.stimEditor
        track_pos = qttools.center(stimEditor.ui.trackview)
        for comp in components:
            name = comp[0]
            vals = comp[1]
            tone_label_pos = qttools.center(stimEditor.ui.templateBox.getLabelByName(name))
            self.drag(tone_label_pos, track_pos)
            self.set_paramters(name, vals)
            robot.keypress('enter')

        assert stimEditor.ui.trackview.model().componentCount() == len(components)
        # pause neccessary for stims to update their visual rects,
        # to allow the following code to work
        QtTest.QTest.qWait(PAUSE) 

        if len(components) == 2:
            # line one up behind the other.. could make more robust my investigating row and column count
            pos0 = qttools.center(stimEditor.ui.trackview.visualRect(stimEditor.ui.trackview.model().index(0,0)),stimEditor.ui.trackview.viewport())
            comp0len = stimEditor.ui.trackview.visualRect(stimEditor.ui.trackview.model().index(0,0)).width()
            pos0 = (pos0[0]+(comp0len/2)+15, pos0[1])
            pos1 = qttools.center(stimEditor.ui.trackview.visualRect(stimEditor.ui.trackview.model().index(1,0)),stimEditor.ui.trackview.viewport())
            self.drag(pos1,pos0)
            assert stimEditor.ui.trackview.model().duration() == sum([x[1]['duration'] for x in components])/1000.


        robot.click(qttools.center(stimEditor.ui.parametizer.hideBtn))
        QtGui.QApplication.processEvents()
        pztr = stimEditor.ui.parametizer.parametizer

        for i, param in enumerate(autoparams):
            add_pos = qttools.center(pztr.addLbl)
            list_pos = qttools.center(pztr.paramList)
            self.drag(add_pos, list_pos)
            # just select first component
            QtTest.QTest.qWait(PAUSE)
            robot.click(qttools.center(stimEditor.ui.trackview.visualRect(stimEditor.ui.trackview.model().index(0,0)),stimEditor.ui.trackview.viewport()))
            # fill in auto  parameter
            for j, param_item in enumerate(param):
                # click the field
                robot.click(qttools.center(pztr.paramList.visualRect(pztr.paramList.model().index(i,j)), pztr.paramList.viewport()))
                robot.type(str(param_item))
                QtTest.QTest.qWait(PAUSE)

        QtGui.QApplication.processEvents()
        QtTest.QTest.qWait(PAUSE)
        # just use default tone settings, for now at least
        robot.click(qttools.center(stimEditor.ui.okBtn))

        # extract StimulusModel
        stim = self.form.acqmodel.protocol_model().data(self.form.acqmodel.protocol_model().index(0,0), QtCore.Qt.UserRole)
        assert stim.autoParams().rowCount() == len(autoparams)
        
        # set the window size to stim len + 100ms
        robot.doubleclick(qttools.center(self.form.ui.windowszSpnbx))
        robot.type(str(stim.duration()*1000+100))

        robot.click(qttools.center(self.form.ui.startBtn))
        QtTest.QTest.qWait(ALLOW)
        assert self.form.ui.runningLabel.text() == "RECORDING"

        # modal dialog will block qt methods in main thread
        dialogthread = threading.Thread(target=self.close_modal)
        dialogthread.start()

        self.wait_until_done()

    def wait_until_done(self):
        while self.form.ui.runningLabel.text() == "RECORDING":
            QtTest.QTest.qWait(500)

        assert self.form.ui.runningLabel.text() == "OFF"

    def drag(self, source, dest):
        dragthread = threading.Thread(target=robot.mousedrag, args=(source, dest))
        dragthread.start()
        while dragthread.is_alive():
            QtTest.QTest.qWait(500)

    def close_modal(self):
        dialogs = []
        while len(dialogs) == 0:
            topWidgets = QtGui.QApplication.topLevelWidgets()
            dialogs = [w for w in topWidgets if isinstance(w, QtGui.QDialog)]
            time.sleep(1)
        robot.click(qttools.center(dialogs[0].ui.okBtn))

    def set_paramters(self, name, vals):
        # find an editor and set the parameters
        topWidgets = QtGui.QApplication.topLevelWidgets()
        editors = [w for w in topWidgets if isinstance(w, AbstractParameterWidget)]
        assert len(editors) == 1
        editor = editors[0]
        for field, val in vals.items():
            input_pos = qttools.center(editor.inputWidgets[field])
            robot.doubleclick(input_pos)
            robot.type(str(val))
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