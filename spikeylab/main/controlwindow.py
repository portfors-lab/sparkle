import os
import json
from PyQt4 import QtCore, QtGui

import spikeylab.tools.systools as systools
from spikeylab.main.window_accessories import MaximizableTitleBar
from spikeylab.stim.abstract_editor import AbstractEditorWidget
from spikeylab.stim.abstract_stimulus import AbstractStimulusComponent
from spikeylab.plotting.custom_plots import SpecWidget
from spikeylab.plotting.calibration_display import CalibrationDisplay
from maincontrol_form import Ui_ControlWindow

class ControlWindow(QtGui.QMainWindow):
    """ Base class just to handle loading, saving, and validity of user inputs"""
    def __init__(self, inputs_filename, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_ControlWindow()
        self.ui.setupUi(self)

        self.calibration_display = CalibrationDisplay()
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
            # each widget should be in charge of putting its own stimulus together
            stim_index = self.ui.explore_stim_type_cmbbx.currentIndex()
            stim_widget = self.ui.parameter_stack.widget(stim_index)
            stim_widget.saveToObject()
            selected_stim = self.explore_stimuli[stim_index]
            failmsg = selected_stim.verify(samplerate=self.ui.aosr_spnbx.value()*self.fscale)
            if failmsg:
                allgood = False
                QtGui.QMessageBox.warning(self, "Invalid Input", failmsg)
            if selected_stim.duration() > self.ui.windowsz_spnbx.value()*self.tscale:
                allgood=False
                QtGui.QMessageBox.warning(self, "Invalid Input",
                        "Window size must equal or exceed stimulus length")
        elif self.ui.tab_group.currentWidget().objectName() == 'tab_protocol':
            failure = self.acqmodel.protocol_model.verify(float(self.ui.windowsz_spnbx.value())*self.tscale)
            if failure:
                allgood=False
                QtGui.QMessageBox.warning(self, "Invalid Input", failure)
        elif self.ui.tab_group.currentWidget().objectName() == 'tab_calibrate':
            failure = self.acqmodel.calibration_stimulus.verify(float(self.ui.windowsz_spnbx.value())*self.tscale)
            if failure:
                allgood=False
                QtGui.QMessageBox.warning(self, "Invalid Input", failure)
        if self.current_mode == 'windowed':
            pass
        else:
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
                    field.setMinimum(1)
                for lbl in self.time_labels:
                    lbl.setText(u'ms')
            elif self.tscale == 1:
                for field in self.time_inputs:
                    field.setDecimals(3)
                    field.setMinimum(0.001)
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
            self.calibration_display.set_fscale(self.fscale)

            if self.fscale == 1000:
                for field in self.frequency_inputs:
                    field.setDecimals(3)
                    field.setMinimum(0.001)
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
                    field.setMinimum(1)
                for lbl in self.frequency_labels:
                    lbl.setText(u'Hz')
            else:
                print self.fscale
                raise Exception(u"Invalid frequency scale")
            
    def save_inputs(self, fname):
        # save current inputs to file for loading next time
        if not fname:
            return
            
        appdir = systools.get_appdir()
        if not os.path.isdir(appdir):
            os.makedirs(appdir)
        fname = os.path.join(appdir, fname)

        savedict = {}
        savedict['wavrootdir'] = self.exvocal.getTreeRoot()
        savedict['filelistdir'] = self.exvocal.getListRoot()
        savedict['threshold'] = self.ui.thresh_spnbx.value()
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
        savedict['calvals'] = self.calvals

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
        self.ui.thresh_spnbx.setValue(inputsdict.get('threshold', 0.5))
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
        self.ui.display.set_spec_args(**self.spec_args)        
        self.calvals = inputsdict.get('calvals', {'calf':20000, 'caldb':100, 'calv':0.1,'calfile':'', 'use_calfile':False})
        self.acqmodel.set_params(**self.calvals)
        if self.calvals['use_calfile']:
            self.acqmodel.set_calibration(self.calvals['calfile'])
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