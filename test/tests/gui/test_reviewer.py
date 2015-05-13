import unittest

from sparkle.QtWrapper import QtCore, QtGui, QtTest
from sparkle.data.open import open_acqdata
from sparkle.gui.data_review import QDataReviewer
from test import sample

PAUSE = 200
ALLOW = 15

class TestDataReviewer():
    def setUp(self):
        self.ui = QDataReviewer()
        self.datafile = open_acqdata(sample.datafile(), filemode='r')
        self.ui.setDataObject(self.datafile)
        self.ui.show()
        self.treeroot = self.ui.datatree.model().index(0,0)
        QtTest.QTest.qWait(ALLOW)

    def tearDown(self):
        self.ui.close()

    def test_select_file(self):
        self.ui.datatree.selectionModel().select(self.treeroot, QtGui.QItemSelectionModel.Select)
        assert self.ui.attrtxt.toPlainText() != ''

    def test_select_group(self):
        self.ui.datatree.selectionModel().select(self.ui.datatree.model().index(0,0, self.treeroot), QtGui.QItemSelectionModel.Select)
        assert self.ui.attrtxt.toPlainText() != ''

    def test_select_dataset(self):
        # third entry is a protocol run
        group = self.ui.datatree.model().index(2,0, self.treeroot)
        self.ui.datatree.expand(group)
        self.ui.datatree.selectionModel().select(self.ui.datatree.model().index(0,0, group), QtGui.QItemSelectionModel.Select)
        assert self.ui.attrtxt.toPlainText() != ''
        assert self.ui.tracetable.rowCount() > 0

    def test_show_calibration_stims_from_tree(self):
        group = self.ui.datatree.model().index(0,0, self.treeroot)
        self.ui.datatree.expand(group)

        self.ui.datatree.selectionModel().select(self.ui.datatree.model().index(2,0, group), QtGui.QItemSelectionModel.Select)
        assert self.ui.tracetable.rowCount() > 0
        self.ui.datatree.selectionModel().select(self.ui.datatree.model().index(1,0, group), QtGui.QItemSelectionModel.Select)
        assert self.ui.tracetable.rowCount() > 0

    def test_show_calibration_stims_from_table(self):
        self.ui.datatable.setCurrentCell(3,0)
        assert self.ui.tracetable.rowCount() == 23
        self.ui.datatable.setCurrentCell(1,0)
        assert self.ui.tracetable.rowCount() == 1

    def test_display_test_attributes(self):
        self.ui.datatable.setCurrentCell(3,0)

        text = self.ui.attrtxt.toPlainText()
        # check some things we know about the sample data
        assert "testtype : Tuning Curve" in text
        assert "mode : finite" in text
        # includes parent group attributes
        assert "comment : for science!" in text
        assert "samplerate_ad : 20000.0" in text

        # check calculated attributes
        text = self.ui.derivedtxt.toPlainText()
        assert "Dataset dimensions : (23, 3, 2000)" in text
        assert "Recording window duration : 0.1 s" in text

    def test_scroll_reps(self):
        self.ui.datatable.setCurrentCell(3,0)
        self.ui.tracetable.setCurrentCell(0,0)

        assert self.ui.current_rep_num == 0
        assert self.ui.current_trace_num == 0
        assert self.ui.tracetable.currentRow() == 0

        self.ui.nextRep()

        assert self.ui.current_rep_num == 1
        assert self.ui.current_trace_num == 0
        assert self.ui.tracetable.currentRow() == 0

        self.ui.nextRep()
        self.ui.nextRep()

        assert self.ui.current_rep_num == 0
        assert self.ui.current_trace_num == 1
        assert self.ui.tracetable.currentRow() == 1

        self.ui.prevRep()

        assert self.ui.current_rep_num == 2
        assert self.ui.current_trace_num == 0
        assert self.ui.tracetable.currentRow() == 0

        self.ui.prevRep()

        assert self.ui.current_rep_num == 1
        assert self.ui.current_trace_num == 0
        assert self.ui.tracetable.currentRow() == 0

    def test_scroll_stays_in_data_bounds(self):

        self.ui.datatable.setCurrentCell(3,0)
        self.ui.tracetable.setCurrentCell(0,0)

        assert self.ui.current_rep_num == 0
        assert self.ui.current_trace_num == 0
        assert self.ui.tracetable.currentRow() == 0

        self.ui.prevRep()

        assert self.ui.current_rep_num == 0
        assert self.ui.current_trace_num == 0
        assert self.ui.tracetable.currentRow() == 0

        self.ui.tracetable.setCurrentCell(22,0)

        self.ui.nextRep()
        self.ui.nextRep()
        self.ui.nextRep()
        self.ui.nextRep()

        assert self.ui.current_rep_num == 2
        assert self.ui.current_trace_num == 22
        assert self.ui.tracetable.currentRow() == 22

    def test_skip_to_first_last_rep(self):
        self.ui.datatable.setCurrentCell(3,0)
        self.ui.tracetable.setCurrentCell(1,0)

        assert self.ui.current_rep_num == 0
        assert self.ui.current_trace_num == 1
        assert self.ui.tracetable.currentRow() == 1

        self.ui.lastRep()

        assert self.ui.current_rep_num == 2
        assert self.ui.current_trace_num == 1
        assert self.ui.tracetable.currentRow() == 1

        self.ui.firstRep()

        assert self.ui.current_rep_num == 0
        assert self.ui.current_trace_num == 1
        assert self.ui.tracetable.currentRow() == 1

    def test_play_trace(self):
        self.ui.datatable.setCurrentCell(3,0)
        self.ui.tracetable.setCurrentCell(1,0)

        wait_time = 3*200 + 50

        self.ui.playTrace()
        QtTest.QTest.qWait(wait_time)

        assert self.ui.current_rep_num == 2
        assert self.ui.current_trace_num == 1
        assert self.ui.tracetable.currentRow() == 1

        assert str(self.ui.playTraceButton.text()) == 'play'
        assert self.ui.playTraceButton.isEnabled()
        assert self.ui.playTestButton.isEnabled()

    def test_play_test(self):
        self.ui.datatable.setCurrentCell(3,0)
        self.ui.tracetable.setCurrentCell(1,0)

        wait_time = 3*200*23 + 50

        self.ui.playTest()
        QtTest.QTest.qWait(wait_time)

        assert self.ui.current_rep_num == 2
        assert self.ui.current_trace_num == 22
        assert self.ui.tracetable.currentRow() == 22

        assert str(self.ui.playTestButton.text()) == 'play all'
        assert self.ui.playTraceButton.isEnabled()
        assert self.ui.playTestButton.isEnabled()
