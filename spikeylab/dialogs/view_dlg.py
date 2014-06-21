from PyQt4 import QtGui, QtCore

from viewdialog_form import Ui_ViewSettingsDialog

from spikeylab.stim.types import get_stimuli_models

class ViewSettingsDialog(QtGui.QDialog):
    def __init__(self, defaultVals=None):
        QtGui.QDialog.__init__(self, None)
        self.ui = Ui_ViewSettingsDialog()
        self.ui.setupUi(self)

        stimuli = get_stimuli_models()
        comp_states = [stim().stateDict() for stim in stimuli if stim.protocol]

        self.ui.detailWidget.setComponents(comp_states)
        if defaultVals is not None:
            self.ui.fontszSpnbx.setValue(defaultVals['fontsz'])
            self.ui.detailWidget.setCheckedDetails(defaultVals['display_attributes'])

    def values(self):
        result = {}
        result['fontsz'] = self.ui.fontszSpnbx.value()
        result['display_attributes'] = self.ui.detailWidget.getCheckedDetails()
        return result