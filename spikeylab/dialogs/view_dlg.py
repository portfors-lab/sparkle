from PyQt4 import QtGui, QtCore

from viewdialog_form import Ui_ViewSettingsDialog

from spikeylab.stim.types import get_stimuli_models

class ViewSettingsDialog(QtGui.QDialog):
    def __init__(self, default_vals=None):
        QtGui.QDialog.__init__(self, None)
        self.ui = Ui_ViewSettingsDialog()
        self.ui.setupUi(self)

        stimuli = get_stimuli_models()
        comp_states = [stim().stateDict() for stim in stimuli if stim.protocol]

        self.ui.detail_widget.set_components(comp_states)
        if default_vals is not None:
            self.ui.fontsz_spnbx.setValue(default_vals['fontsz'])
            self.ui.detail_widget.set_checked_details(default_vals['display_attributes'])

    def values(self):
        result = {}
        result['fontsz'] = self.ui.fontsz_spnbx.value()
        result['display_attributes'] = self.ui.detail_widget.get_checked_details()
        return result