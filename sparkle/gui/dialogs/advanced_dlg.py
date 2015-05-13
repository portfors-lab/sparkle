from advanced_dlg_form import Ui_AdvancedOptionsDialog
from sparkle.QtWrapper import QtCore, QtGui
from sparkle.acq.daq_tasks import get_devices

class AdvancedOptionsDialog(QtGui.QDialog):
    def __init__(self, options):
        super(AdvancedOptionsDialog, self).__init__()
        self.ui = Ui_AdvancedOptionsDialog()
        self.ui.setupUi(self)

        # populate from devices on the system
        devices = get_devices()
        self.ui.deviceCmbx.addItems(devices)
        if options['device_name'] in devices:
            selected_index = devices.index(options['device_name'])
            if selected_index is not None:
                self.ui.deviceCmbx.setCurrentIndex(selected_index)

        self.ui.speakerMaxVSpnbx.setValue(options['max_voltage'])      
        self.ui.squareMaxVSpnbx.setValue(options['device_max_voltage'])

        self.ui.V2ASpnbx.setValue(options['volt_amp_conversion'])

        self.ui.attenOnRadio.setChecked(options['use_attenuator'])

        # tooltips
        self.ui.deviceCmbx.setToolTip("Name of Data Acquisition card to use")
        self.ui.speakerMaxVSpnbx.setToolTip("Maximum voltage that should be delivered to amplifier/speakers")
        self.ui.squareMaxVSpnbx.setToolTip("Maximum voltage that should be output from the DAQ ever (used for square wave max amplitude)")
        self.ui.V2ASpnbx.setToolTip("conversion factor to apply to plot when set to amps, to convert signal from volts")

    def getValues(self):
        options = {}
        options['device_name'] = str(self.ui.deviceCmbx.currentText())
        options['max_voltage'] = self.ui.speakerMaxVSpnbx.value()
        options['device_max_voltage'] = self.ui.squareMaxVSpnbx.value()
        options['volt_amp_conversion'] = self.ui.V2ASpnbx.value()
        options['use_attenuator'] = self.ui.attenOnRadio.isChecked()
        return options

