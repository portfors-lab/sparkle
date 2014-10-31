from QtWrapper import QtCore, QtGui, QtTest

from spikeylab.gui.data_review import QDataReviewer
from spikeylab.data.dataobjects import AcquisitionData

from test import sample

class TestDataReviewer():
    def setUp(self):
        self.ui = QDataReviewer()
        self.datafile = AcquisitionData(sample.datafile(), filemode='r')
        self.ui.setDataObject(self.datafile)
        self.ui.setDisplayAttributes({'Vocalization': [u'Vocalization', u'risefall', u'intensity', u'file', u'duration', 'start_s'], 'silence': [u'silence', u'duration', u'risefall', u'intensity'], 'Pure Tone': [u'Pure Tone', u'duration', u'risefall', u'intensity', u'frequency']})
        self.ui.show()
        self.treeroot = self.ui.datatree.model().index(0,0)

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

    def test_show_calibration_stims(self):
        group = self.ui.datatree.model().index(0,0, self.treeroot)
        self.ui.datatree.expand(group)
        self.ui.datatree.selectionModel().select(self.ui.datatree.model().index(2,0, group), QtGui.QItemSelectionModel.Select)
        assert self.ui.tracetable.rowCount() > 0
        self.ui.datatree.selectionModel().select(self.ui.datatree.model().index(1,0, group), QtGui.QItemSelectionModel.Select)
        assert self.ui.tracetable.rowCount() > 0
