import qtbot
from sparkle.QtWrapper import QtCore, QtGui, QtTest
from sparkle.gui.stim.auto_parameter_view import AutoParameterTableView
from sparkle.gui.stim.qauto_parameter_model import QAutoParameterModel
from sparkle.stim.auto_parameter_model import AutoParameterModel

ALLOW = 100

class TestAutoParameterView():

    def setUp(self):
        self.view = AutoParameterTableView()
        model = AutoParameterModel()
        self.qmodel = QAutoParameterModel(model)
        self.view.setModel(self.qmodel)
        self.view.show()
        self.view.resize(600,300)

    def tearDown(self):
        self.view.close()

    def xtest_drag_nowhere(self):
        self.qmodel.insertRows(0, 1)
        QtTest.QTest.qWait(ALLOW)
        # QtTest.QTest.qWait(10000)

        # for some reason this fires a childRemoved event, and an extra
        # row gets added for automated testing only
        qtbot.drag(self.view, self.view, src_index=self.qmodel.index(0,1))
        QtTest.QTest.qWait(ALLOW)

        # check that the view isn't adding/drawing extra rows
        assert self.qmodel.rowCount() == 1

    def test_drag_miss(self):
        self.qmodel.insertRows(0, 1)
        QtTest.QTest.qWait(ALLOW)
        qtbot.drag(self.view, self.view, dest_index=self.qmodel.index(0,1))
        QtTest.QTest.qWait(ALLOW)

        assert self.qmodel.rowCount() == 1
