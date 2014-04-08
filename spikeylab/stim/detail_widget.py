from PyQt4 import QtGui

from spikeylab.stim.detail_form import Ui_StimDetailWidget

class StimDetailWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self)
        self.ui = Ui_StimDetailWidget()
        self.ui.setupUi(self)

    def set_test_num(self, num):
        self.ui.test_num.setNum(num+1)

    def set_trace_num(self, num):
        self.ui.trace_num.setNum(num+1)

    def set_rep_num(self, num):
        self.ui.rep_num.setNum(num+1)

    def set_doc(self, doc):
        self.ui.over_atten.setNum(doc['overloaded_attenuation'])
        # also set composite stim type
        self.ui.trace_type.setText(doc['testtype'])

        self.ui.component_details.clear_doc()
        self.ui.component_details.set_doc(doc['components'])

    def set_display_attributes(self, attrs):
        self.ui.component_details.set_display_table(attrs)