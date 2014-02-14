from spikeylab.main.control import MainWindow

import sys 
import time, os, glob
import json

import h5py
from nose.tools import assert_in, assert_equal

from PyQt4.QtGui import QApplication 
from PyQt4.QtTest import QTest 
from PyQt4.QtCore import Qt

import test.sample as sample

app = None
def setUp():
    global app
    app = QApplication(sys.argv)

def tearDown():
    global app
    app.exit(0)

class TestSpikey():
    def setUp(self):
        self.form = MainWindow()
        self.tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), u"tmp")
        self.form.savefolder = self.tempfolder

    def tearDown(self):
        self.form.close()
        # delete all data files in temp folder -- this will also clear out past
        # test runs that produced errors and did not delete their files
        files = glob.glob(self.tempfolder + os.sep + '[a-zA-Z0-9_]*.hdf5')
        for f in files:
            os.remove(f)

    def test_tone_explore_defaults(self):
        """The defaults should combine to be a viable set-up"""
        self.form.ui.tab_group.setCurrentIndex(0)
        stimuli = [self.form.ui.explore_stim_type_cmbbx.itemText(i).lower() for i in xrange(self.form.ui.explore_stim_type_cmbbx.count())]
        tone_idx = stimuli.index('pure tone')
        self.form.ui.explore_stim_type_cmbbx.setCurrentIndex(tone_idx)

        QTest.mouseClick(self.form.ui.start_btn, Qt.LeftButton)
        assert self.form.ui.running_label.text() == "RECORDING"
        time.sleep(1)
        QTest.mouseClick(self.form.ui.stop_btn, Qt.LeftButton)
        assert self.form.ui.running_label.text() == "OFF"
        time.sleep(1) #gives program a chance to stash data

        # not really a great check
        files = glob.glob(self.tempfolder + os.sep + '[a-zA-Z0-9_]*.hdf5')
        print 'files', files
        assert len(files) == 1

    def test_vocal_explore(self):
        """We set a sample wav file ourselves"""
        self.form.ui.tab_group.setCurrentIndex(0)
        stimuli = [self.form.ui.explore_stim_type_cmbbx.itemText(i).lower() for i in xrange(self.form.ui.explore_stim_type_cmbbx.count())]
        tone_idx = stimuli.index('vocalization')
        self.form.ui.explore_stim_type_cmbbx.setCurrentIndex(tone_idx)

        # We are going to cheat and set the vocal file directly
        self.form.exvocal.current_wav_file = sample.samplewav()
        QTest.mouseClick(self.form.ui.start_btn, Qt.LeftButton)
        assert self.form.ui.running_label.text() == "RECORDING"
        time.sleep(1)
        QTest.mouseClick(self.form.ui.stop_btn, Qt.LeftButton)
        assert self.form.ui.running_label.text() == "OFF"
        time.sleep(1) #gives program a chance to stash data

        # not really a great check
        files = glob.glob(self.tempfolder + os.sep + '[a-zA-Z0-9_]*.hdf5')
        assert len(files) == 1

    def test_save_calibration(self):
        self.form.ui.tab_group.setCurrentIndex(2)
        self.form.ui.reprate_spnbx.setValue(4)
        self.form.ui.calibration_widget.ui.savecal_ckbx.setChecked(True)
        QTest.mouseClick(self.form.ui.start_btn, Qt.LeftButton)

        timeout = 30
        start = time.time()
        while self.form.ui.running_label.text() == "RECORDING" and (time.time()-start) < timeout:
            time.sleep(1)
            QApplication.processEvents()
            
        assert self.form.ui.running_label.text() == "OFF"

        # check that calibration file was saved
        assert self.form.calvals['use_calfile'] == True
        fname = self.form.calvals['calfile']

        # now check saved data
        hfile = h5py.File(fname, 'r')
        peaks = hfile['fft_peaks']
        stim = json.loads(hfile.attrs['stim'])
        cal_vector = hfile['calibration_intensities']
        print 'attr keys:', hfile.attrs.keys()

        # make sure displayed counts jive with saved file
        nfreqs = int(self.form.ui.calibration_widget.ui.curve_widget.ui.freq_nsteps_lbl.text())
        ndbs = int(self.form.ui.calibration_widget.ui.curve_widget.ui.db_nsteps_lbl.text())
        ntraces = nfreqs*ndbs
        nreps = self.form.ui.calibration_widget.ui.curve_widget.ui.nreps_spnbx.value()
        assert_in('components', stim[0])
        assert_equal(stim[0]['samplerate_da'], hfile.attrs['samplerate_ad'])
        assert_equal(peaks.shape,(ntraces,nreps))
        assert cal_vector.shape == (nfreqs,) 

        hfile.close()

    def test_no_save_calibration(self):
        self.form.ui.tab_group.setCurrentIndex(2)
        self.form.ui.aisr_spnbx.setValue(400) # should be kHz
        self.form.ui.reprate_spnbx.setValue(4)
        self.form.ui.calibration_widget.ui.savecal_ckbx.setChecked(False)
        original_calfile = self.form.calvals['calfile'] #may be None

        QTest.mouseClick(self.form.ui.start_btn, Qt.LeftButton)

        timeout = 30
        start = time.time()
        while self.form.ui.running_label.text() == "RECORDING" and (time.time()-start) < timeout:
            time.sleep(1)
            QApplication.processEvents()
            
        assert self.form.ui.running_label.text() == "OFF"

        # make sure there is not calibration file present
        assert self.form.calvals['calfile'] == original_calfile

        files = glob.glob(self.tempfolder + os.sep + 'calibration*.hdf5')
        print 'files', files
        assert len(files) == 0

    def test_abort_calibration(self):
        self.form.ui.tab_group.setCurrentIndex(2)
        self.form.ui.aisr_spnbx.setValue(400) # should be kHz
        self.form.ui.reprate_spnbx.setValue(4)
        self.form.ui.calibration_widget.ui.savecal_ckbx.setChecked(True)
        original_calfile = self.form.calvals['calfile'] #may be None

        QTest.mouseClick(self.form.ui.start_btn, Qt.LeftButton)
        assert self.form.ui.running_label.text() == "RECORDING"
        time.sleep(1)
        QTest.mouseClick(self.form.ui.stop_btn, Qt.LeftButton)
        time.sleep(1) #gives program a chance to gracefully stop
        QApplication.processEvents()
        assert self.form.ui.running_label.text() == "OFF"

        # make sure there is not calibration file present
        assert self.form.calvals['calfile'] == original_calfile

        files = glob.glob(self.tempfolder + os.sep + 'calibration*.hdf5')
        print 'files', files
        assert len(files) == 0

    # def test_verify_no_tests(self):
    #     self.form.ui.tab_group.setCurrentIndex(1)
    #     QTest.mouseClick(self.form.ui.start_btn, Qt.LeftButton)

    #     # how do I acknowldge and dismiss dialog?
    #     QTest.keyPress(self.form, Qt.Key_Enter)