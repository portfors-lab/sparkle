import os
import json
from PyQt4 import QtCore, QtGui

import audiolab.tools.systools as systools
from maincontrol_form import Ui_ControlWindow

INPUTSFNAME = "controlinputs.json"

class ControlWindow(QtGui.QMainWindow):
    """ Base class just to handle loading, saving, and validity of user inputs"""
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_ControlWindow()
        self.ui.setupUi(self)

    def verify_inputs(self):
        allgood = True
        if self.ui.tab_group.currentWidget().objectName() == 'tab_explore':
            if self.ui.explore_stim_type_cmbbx.currentText() == 'Vocalization':
                pass
            elif self.ui.explore_stim_type_cmbbx.currentText() == 'Tone':
                if self.ui.extone_dur_spnbx.value() > self.ui.windowsz_spnbx.value():
                    QtGui.QMessageBox.warning(self, "Invalid Input",
                        "Window size must equal or exceed stimulus length")
                    allgood = False
        elif self.ui.tab_group.currentWidget().objectName() == 'tab_tc':
            pass
        elif self.ui.tab_group.currentWidget().objectName() == 'tab_chart':
            pass
        elif self.ui.tab_group.currentWidget().objectName() == 'tab_experiment':
            pass
        return allgood
        
    def save_inputs(self):
        # save current inputs to file for loading next time
        appdir = systools.get_appdir()
        if not os.path.isdir(appdir):
            os.makedirs(appdir)
        fname = os.path.join(appdir, INPUTSFNAME)

        savedict = {}
        savedict['wavrootdir'] = self.ui.wavrootdir_lnedt.text()
        savedict['threshold'] = self.ui.thresh_lnedt.text()
        savedict['binsz'] = self.ui.binsz_lnedt.text()
        savedict['aisr'] = self.ui.aisr_spnbx.value()
        savedict['tscale'] = self.tscale
        savedict['fscale'] = self.fscale
        savedict['savefolder'] = self.savefolder
        savedict['savename'] = self.savename
        savedict['saveformat'] = self.saveformat
        savedict['extone_freq'] = self.ui.extone_freq_spnbx.value()
        savedict['extone_db'] = self.ui.extone_db_spnbx.value()
        savedict['windowsz'] = self.ui.windowsz_spnbx.value()
        with open(fname, 'w') as jf:
            json.dump(savedict, jf)

    def load_inputs(self):
        inputsfname = os.path.join(systools.get_appdir(), INPUTSFNAME)
        try:
            with open(inputsfname, 'r') as jf:
                inputsdict = json.load(jf)
        except:
            print "problem loading app data"
            inputsdict = {}
        
        # set default values
        homefolder = os.path.join(os.path.expanduser("~"), "audiolab_data")

        self.wavrootdir = inputsdict.get('wavrootdir', os.path.expanduser('~'))
        self.ui.thresh_lnedt.setText(inputsdict.get('threshold', '0.5'))
        self.ui.aisr_spnbx.setValue(inputsdict.get('aisr', 100))
        self.ui.windowsz_spnbx.setValue(inputsdict.get('windowsz', 100))
        self.ui.binsz_lnedt.setText(inputsdict.get('binsz', '5'))        
        self.tscale = inputsdict.get('tscale', 0.001)
        self.fscale = inputsdict.get('fscale', 1000)
        self.savefolder = inputsdict.get('savefolder', homefolder)
        self.savename = inputsdict.get('savename', "untitled")
        self.saveformat = inputsdict.get('saveformat', 'hdf5')
        self.ui.extone_freq_spnbx.setValue(inputsdict.get('extone_freq', 5))
        self.ui.extone_db_spnbx.setValue(inputsdict.get('extone_db', 60))

        self.ui.wavrootdir_lnedt.setText(self.wavrootdir)
