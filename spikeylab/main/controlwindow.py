import os
import json
from PyQt4 import QtCore, QtGui

from spikeylab.main.window_accessories import MaximizableTitleBar
import spikeylab.tools.systools as systools
from maincontrol_form import Ui_ControlWindow
from spikeylab.stim.abstract_editor import AbstractEditorWidget
from spikeylab.stim.abstract_stimulus import AbstractStimulusComponent
from spikeylab.plotting.custom_plots import SpecWidget

class ControlWindow(QtGui.QMainWindow):
    """ Base class just to handle loading, saving, and validity of user inputs"""
    def __init__(self, inputs_filename, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_ControlWindow()
        self.ui.setupUi(self)

        # make a list of which widgets should be updated when scales are changed
        self.time_inputs = [self.ui.windowsz_spnbx, self.ui.binsz_spnbx]
        self.frequency_inputs = [self.ui.aisr_spnbx, self.ui.aosr_spnbx]
        self.time_labels = [self.ui.tunit_lbl, self.ui.tunit_lbl_2]
        self.frequency_labels = [self.ui.funit_lbl, self.ui.funit_lbl_2]

        self.ui.protocolView.installEventFilter(self.ui.stimulus_choices.trash())
        self.ui.plot_dock.setTitleBarWidget(MaximizableTitleBar(self.ui.plot_dock))
        self.load_inputs(inputs_filename)
        self.inputs_filename = inputs_filename

        # hack so that original values use correct multiplications
        # AbstractEditorWidget().
        for stim in self.explore_stimuli:
            self.ui.parameter_stack.addWidget(stim.showEditor())
            self.ui.explore_stim_type_cmbbx.addItem(stim.name)

        try:
            settings = QtCore.QSettings("audiolab")
            self.restoreGeometry(settings.value("geometry"))
            self.restoreState(settings.value("windowState"))
            # self.ui.psth.restoreGeometry(settings.value("psth_dock/geometry"))

        except Exception as e:
            print e

    def verify_inputs(self):
        allgood = True
        if self.ui.tab_group.currentWidget().objectName() == 'tab_explore':
            if self.ui.explore_stim_type_cmbbx.currentText() == 'Vocalization':
                pass
            elif self.ui.explore_stim_type_cmbbx.currentText() == 'Tone':
                extone = self.ui.parameter_stack.widget_for_name('Tone')
                if extone.durationValue() > self.ui.windowsz_spnbx.value():
                    QtGui.QMessageBox.warning(self, "Invalid Input",
                        "Window size must equal or exceed stimulus length")
                    allgood = False
                if extone.freq_spnbx.value() > (self.ui.aosr_spnbx.value()/2):
                    QtGui.QMessageBox.warning(self, "Invalid Input",
                        "Generation sample rate must be at least twice the stimulus frequency")
                    allgood=False
        elif self.ui.tab_group.currentWidget().objectName() == 'tab_tc':
            pass
        elif self.ui.tab_group.currentWidget().objectName() == 'tab_chart':
            pass
        elif self.ui.tab_group.currentWidget().objectName() == 'tab_experiment':
            pass
        return allgood

    def update_unit_labels(self, tscale, fscale, setup=False):

        if tscale != self.tscale:
            self.tscale = tscale
            # bad!
            AbstractEditorWidget().setTScale(self.tscale, setup=setup)
            AbstractStimulusComponent().update_tscale(self.tscale)

            self.ui.display.set_tscale(self.tscale)
            
            if self.tscale == 0.001:
                for field in self.time_inputs:
                    field.setMaximum(3000)
                    if not setup:
                        field.setValue(field.value()/0.001)
                    field.setDecimals(0)
                for lbl in self.time_labels:
                    lbl.setText(u'ms')
            elif self.tscale == 1:
                for field in self.time_inputs:
                    field.setDecimals(3)
                    if not setup:
                        field.setValue(field.value()*0.001)
                    field.setMaximum(3)
                for lbl in self.time_labels:
                    lbl.setText(u's')
            else:
                print self.tscale
                raise Exception(u"Invalid time scale")

        if fscale != self.fscale:
            self.fscale = fscale
            AbstractEditorWidget().setFScale(self.fscale, setup=setup)
            AbstractStimulusComponent().update_fscale(self.fscale)

            self.ui.display.set_fscale(self.fscale)

            if self.fscale == 1000:
                for field in self.frequency_inputs:
                    field.setDecimals(3)
                    if not setup:
                        field.setValue(field.value()/1000)
                    field.setMaximum(500)
                for lbl in self.frequency_labels:
                    lbl.setText(u'kHz')

            elif self.fscale == 1:
                for field in self.frequency_inputs:
                    field.setMaximum(500000)
                    if not setup:
                        field.setValue(field.value()*1000)
                    field.setDecimals(0)
                for lbl in self.frequency_labels:
                    lbl.setText(u'Hz')
            else:
                print self.fscale
                raise Exception(u"Invalid frequency scale")
            
    def save_inputs(self, fname):
        # save current inputs to file for loading next time
        appdir = systools.get_appdir()
        if not os.path.isdir(appdir):
            os.makedirs(appdir)
        fname = os.path.join(appdir, fname)

        savedict = {}
        savedict['wavrootdir'] = self.exvocal.getTreeRoot()
        savedict['filelistdir'] = self.exvocal.getListRoot()
        savedict['threshold'] = self.ui.thresh_lnedt.text()
        savedict['binsz'] = self.ui.binsz_spnbx.value()
        savedict['aisr'] = self.ui.aisr_spnbx.value()
        savedict['tscale'] = self.tscale
        savedict['fscale'] = self.fscale
        savedict['savefolder'] = self.savefolder
        savedict['savename'] = self.savename
        savedict['saveformat'] = self.saveformat
        savedict['ex_nreps'] = self.ui.ex_nreps_spnbx.value()
        savedict['reprate'] = self.ui.reprate_spnbx.value()
        savedict['aosr'] = self.ui.aosr_spnbx.value()
        savedict['windowsz'] = self.ui.windowsz_spnbx.value()
        savedict['raster_bounds'] = self.ui.display.spiketrace_plot.get_raster_bounds()
        savedict['specargs'] = self.spec_args

        # parameter settings
        for stim in self.explore_stimuli:
            editor = self.ui.parameter_stack.widget_for_name(stim.name)
            editor.saveToObject()
            savedict[stim.name] = stim.stateDict()

        with open(fname, 'w') as jf:
            json.dump(savedict, jf)

    def load_inputs(self, fname):
        inputsfname = os.path.join(systools.get_appdir(), fname)
        try:
            with open(inputsfname, 'r') as jf:
                inputsdict = json.load(jf)
        except:
            print "problem loading app data"
            inputsdict = {}
        
        # set default values
        homefolder = os.path.join(os.path.expanduser("~"), "audiolab_data")

        self.wavrootdir = inputsdict.get('wavrootdir', os.path.expanduser('~'))
        self.filelistdir = inputsdict.get('filelistdir', self.wavrootdir)
        self.ui.thresh_lnedt.setText(str(inputsdict.get('threshold', '0.5')))
        self.ui.aisr_spnbx.setValue(inputsdict.get('aisr', 100))
        self.ui.windowsz_spnbx.setValue(inputsdict.get('windowsz', 100))
        self.ui.binsz_spnbx.setValue(inputsdict.get('binsz', 5))        
        self.savefolder = inputsdict.get('savefolder', homefolder)
        self.savename = inputsdict.get('savename', "untitled")
        self.saveformat = inputsdict.get('saveformat', 'hdf5')
        self.ui.ex_nreps_spnbx.setValue(inputsdict.get('ex_nreps', 5))
        self.ui.reprate_spnbx.setValue(inputsdict.get('reprate', 1))
        self.ui.aosr_spnbx.setValue(inputsdict.get('aosr', 100))
        self.ui.display.spiketrace_plot.set_raster_bounds(inputsdict.get('raster_bounds', (0.5,1)))
        self.spec_args = inputsdict.get('specargs',{u'nfft':512, u'window':u'hanning', u'overlap':90, 'colormap':'jet'})
        SpecWidget().set_spec_args(**self.spec_args)

        tscale = inputsdict.get('tscale', 0.001)
        fscale = inputsdict.get('fscale', 1000)

        self.tscale = 0
        self.fscale = 0
        self.update_unit_labels(tscale, fscale, setup=True)

        for stim in self.explore_stimuli:
            try:
                stim.loadState(inputsdict[stim.name])

            except KeyError:
                print 'Unable to load saved inputs for', stim.__class__


    def closeEvent(self, event):
        self.save_inputs(self.inputs_filename)

        # save GUI size
        settings = QtCore.QSettings("audiolab")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        print 'All user settings saved'
        # settings.setValue("psth_dock/state", self.ui.psth.saveGeometry())