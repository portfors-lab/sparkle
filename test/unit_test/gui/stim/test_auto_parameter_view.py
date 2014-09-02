from PyQt4 import QtCore, QtGui

from spikeylab.stim.auto_parameter_model import AutoParameterModel
from spikeylab.gui.stim.qauto_parameter_model import QAutoParameterModel
from spikeylab.gui.stim.auto_parameter_view import AutoParameterTableView

import qtbot

class TestAutoParameterView():

    def setUp(self):
        self.view = AutoParameterTableView()
        model = AutoParameterModel()
        self.qmodel = QAutoParameterModel(model)
        self.view.setModel(self.qmodel)
        self.view.show()
        self.view.resize(600,300)

    def test_drag_nowhere(self):
        self.qmodel.insertRows(0, 1)
        qtbot.drag(self.view, self.view, src_index=self.qmodel.index(0,1))

        assert self.qmodel.rowCount() == 1

    def test_drag_miss(self):
        self.qmodel.insertRows(0, 1)
        qtbot.drag(self.view, self.view, dest_index=self.qmodel.index(0,1))

        assert self.qmodel.rowCount() == 1
        # I don't know how to test that the view isn't drawing extra rows
