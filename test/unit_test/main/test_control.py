from spikeylab.main.control import MainWindow

import sys 
import time
from PyQt4.QtGui import QApplication 
from PyQt4.QtTest import QTest 
from PyQt4.QtCore import Qt

import test.sample as sample

class TestSpikey():
    def setUp(self):
        self.app = QApplication(sys.argv) 
        self.form = MainWindow()
        self.tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), u"tmp")
        self.form.savefolder = self.tempfolder

    def tearDown(self):
        self.form.close()

    def test_tone_explore_defaults(self):
        """The defaults should combine to be a viable set-up"""
        self.form.ui.tab_group.setCurrentIndex(0)
        stimuli = [self.form.ui.explore_stim_type_cmbbx.itemText(i).lower() for i in xrange(self.form.ui.explore_stim_type_cmbbx.count())]
        tone_idx = stimuli.index('pure tone')
        self.form.ui.explore_stim_type_cmbbx.setCurrentIndex(tone_idx)

        QTest.mouseClick(self.form.ui.start_btn, Qt.LeftButton)
        assert self.form.ui.running_label.text() == "RUNNING"
        time.sleep(1)
        QTest.mouseClick(self.form.ui.stop_btn, Qt.LeftButton)
        assert self.form.ui.running_label.text() == "OFF"
        time.sleep(1) #gives program a chance to stash data

    def test_vocal_explore(self):
        """We set a sample wav file ourselves"""
        self.form.ui.tab_group.setCurrentIndex(0)
        stimuli = [self.form.ui.explore_stim_type_cmbbx.itemText(i).lower() for i in xrange(self.form.ui.explore_stim_type_cmbbx.count())]
        tone_idx = stimuli.index('vocalization')
        self.form.ui.explore_stim_type_cmbbx.setCurrentIndex(tone_idx)

        # We are going to cheat and set the vocal file directly
        self.form.exvocal.current_wav_file = sample.samplewav()
        QTest.mouseClick(self.form.ui.start_btn, Qt.LeftButton)
        assert self.form.ui.running_label.text() == "RUNNING"
        time.sleep(1)
        QTest.mouseClick(self.form.ui.stop_btn, Qt.LeftButton)
        assert self.form.ui.running_label.text() == "OFF"
        time.sleep(1) #gives program a chance to stash data

