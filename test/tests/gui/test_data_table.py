import qtbot
from sparkle.QtWrapper import QtCore, QtGui, QtTest
from sparkle.data.open import open_acqdata
from sparkle.gui.stim_table import StimTable
from test import sample

PAUSE = 250
ALLOW = 20

class TestStimTable():
    def setUp(self):
        self.data = open_acqdata(sample.datafile(), filemode='r')
        self.table = StimTable()
        self.table.setData(self.data)
        self.table.show()
        QtTest.QTest.qWait(PAUSE)

    def tearDown(self):
        self.table.close()
        QtGui.QApplication.processEvents()

    def test_assert_load(self):
        assert self.table.rowCount() == 6
        assert self.table.item(3,0).text() == '/segment_1/test_1'

    def test_trace_table(self):
        qtbot.doubleclick(self.table, self.table.model().index(3,1))        
        QtTest.QTest.qWait(ALLOW)
        # validate some entries are correct

        # Tuning curve entry
        assert self.table.trace_table.rowCount() == 23
        assert self.table.trace_table.item(0,0).text() == 'silence'
        assert self.table.trace_table.item(1,0).text() == 'Pure Tone'
        assert str(self.table.trace_table.horizontalHeaderItem(0).text()) == 'type'
        headers = [str(self.table.trace_table.horizontalHeaderItem(i).text()) for i in range(self.table.trace_table.columnCount())]
        desired_headers = ['frequency', 'intensity', 'risefall', 'start', 'duration']
        print headers
        print desired_headers
        for field in desired_headers:
            assert field in headers

        self.table.trace_table.close()

        QtTest.QTest.qWait(PAUSE)
        # vocalization auto-test entry
        qtbot.doubleclick(self.table, self.table.model().index(4,1))        
        QtTest.QTest.qWait(PAUSE)

        assert self.table.trace_table.rowCount() == 10

        headers = [self.table.trace_table.horizontalHeaderItem(i).text() for i in range(self.table.trace_table.columnCount())]
        desired_headers = ['filename', 'intensity', 'risefall', 'start', 'duration']
        for field in desired_headers:
            assert field in headers

        self.table.trace_table.close()
