import os
import json
import logging
from PyQt4 import QtCore, QtGui

import spikeylab.tools.systools as systools
from spikeylab.tools.util import convert2native
from spikeylab.stim.abstract_editor import AbstractEditorWidget
from spikeylab.stim.abstract_stimulus import AbstractStimulusComponent
from spikeylab.stim.stimulusview import StimulusView
from maincontrol_form import Ui_ControlWindow

class ControlWindow(QtGui.QMainWindow):
    """ Base class just to handle loading, saving, and validity of user inputs"""
    def __init__(self, inputs_filename, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_ControlWindow()
        self.ui.setupUi(self)

        self.calibration_display = self.ui.plot_dock.displays['calibration']
        self.extended_display = self.ui.plot_dock.displays['calexp']
        self.scrollplot = self.ui.plot_dock.displays['chart']
        self.display = self.ui.plot_dock.displays['standard']
        self.ui.plot_dock.switch_display('standard')
        # make a list of which widgets should be updated when scales are changed
        self.time_inputs = [self.ui.windowsz_spnbx, self.ui.binsz_spnbx]
        self.frequency_inputs = [self.ui.aisr_spnbx, self.ui.aosr_spnbx]
        self.time_labels = [self.ui.tunit_lbl, self.ui.tunit_lbl_2]
        self.frequency_labels = [self.ui.funit_lbl, self.ui.funit_lbl_2]

        self.ui.protocolView.installEventFilter(self.ui.stimulus_choices.trash())
        self.load_inputs(inputs_filename)
        self.inputs_filename = inputs_filename

        for calstim in self.acqmodel.bs_calibrator.get_stims()[::-1]: #tsk
            self.ui.calibration_widget.add_option(calstim)

        # keep a reference to a dummy stimulus view, to be able to update
        # default attributes in stimulus builder from explore components
        self.dummyview = StimulusView()
        for stim in self.explore_stimuli:
            editor = stim.showEditor()
            editor.attributes_saved.connect(self.dummyview.update_defaults)
            # intial from saved values
            self.dummyview.update_defaults(stim.__class__.__name__, stim.stateDict())
            self.ui.parameter_stack.addWidget(editor)
            self.ui.explore_stim_type_cmbbx.addItem(stim.name)

        try:
            settings = QtCore.QSettings("audiolab")
            if settings is not None:
                self.restoreGeometry(settings.value("geometry"))
                self.restoreState(settings.value("windowState"))
            else:
                logger = logging.getLogger('main')
                logger.warning('Unable to restore QSettings for audiolab')
            # self.ui.psth.restoreGeometry(settings.value("psth_dock/geometry"))

            self.ui.protocol_progress_bar.setStyleSheet("QProgressBar { text-align: center; }")
            self.ui.protocol_progress_bar.setMinimum(0)
        except Exception as e:
            logger = logging.getLogger('main')
            logger.exception("Error Initializing main GUI")

        # connect item models to trash can signal
        self.ui.stimulus_choices.trash().item_trashed.connect(self.ui.protocolView.purge_model)

    def verify_inputs(self, mode):
        if mode == 'chart':
            if self.ui.aisr_spnbx.value()*self.fscale > 100000:
                QtGui.QMessageBox.warning(self, "Invalid Input", "Recording samplerate cannot exceed 100kHz for chart acquisition")
                return False
        elif mode is not None:
            if self.ui.tab_group.currentWidget().objectName() == 'tab_explore':
                # each widget should be in charge of putting its own stimulus together
                stim_index = self.ui.explore_stim_type_cmbbx.currentIndex()
                stim_widget = self.ui.parameter_stack.widget(stim_index)
                stim_widget.saveToObject()
                selected_stim = self.explore_stimuli[stim_index]
                failmsg = selected_stim.verify(samplerate=self.ui.aosr_spnbx.value()*self.fscale)
                if failmsg:
                    QtGui.QMessageBox.warning(self, "Invalid Input", failmsg)
                    return False
                if selected_stim.duration() > self.ui.windowsz_spnbx.value()*self.tscale:
                    QtGui.QMessageBox.warning(self, "Invalid Input",
                            "Window size must equal or exceed stimulus length")
                    return False
                # if selected_stim.intensity() > self.calvals['caldb']:
                #     QtGui.QMessageBox.warning(self, "Invalid Input",
                #             "Intensity must be below calibrated maximum {}dB SPL".format(self.calvals['caldb']))
                #     return False
            elif self.ui.tab_group.currentWidget().objectName() == 'tab_protocol':
                protocol_model = self.acqmodel.protocol_model()
                failure = protocol_model.verify(float(self.ui.windowsz_spnbx.value())*self.tscale)
                if failure:
                    QtGui.QMessageBox.warning(self, "Invalid Input", failure)
                    return False
            elif self.ui.tab_group.currentWidget().objectName() == 'tab_calibrate':
                if self.ui.calibration_widget.ui.savecal_ckbx.isChecked() or not self.ui.calibration_widget.current_selection() == 'Tone Curve':
                    calibration_stimulus = self.acqmodel.calibration_stimulus('noise')
                    self.ui.calibration_widget.save_to_object()
                else:
                    calibration_stimulus = self.acqmodel.calibration_stimulus('tone')

                failmsg = calibration_stimulus.verify(float(self.ui.windowsz_spnbx.value())*self.tscale)
                if failmsg:
                    QtGui.QMessageBox.warning(self, "Invalid Input", failmsg)
                    return False
                # also check that the recording samplerate is high enough in this case
                failmsg = calibration_stimulus.verify_expanded(samplerate=self.ui.aisr_spnbx.value()*self.fscale)
                if failmsg:
                    failmsg = failmsg.replace('Generation', 'Recording')
                    QtGui.QMessageBox.warning(self, "Invalid Input", failmsg)
                    return False
            if not self.acqmodel.attenuator_connection():
                failmsg = "Error Connection to attenuator, make sure it it turned on and connected, and try again"
                QtGui.QMessageBox.warning(self, "Connection Error", failmsg)
                return False
        return True

    def update_unit_labels(self, tscale, fscale, setup=False):

        AbstractEditorWidget.scales = [tscale, fscale]

        if tscale != self.tscale:
            self.tscale = tscale

            AbstractStimulusComponent.update_tscale(self.tscale)
            AbstractEditorWidget.purge_deleted_widgets()
            time_inputs = self.time_inputs + AbstractEditorWidget.tunit_fields
            time_labels = self.time_labels + AbstractEditorWidget.tunit_labels

            self.display.set_tscale(self.tscale)
            
            if self.tscale == 0.001:
                for field in time_inputs:
                    field.setMaximum(3000)
                    if not setup:
                        field.setValue(field.value()/0.001)
                    field.setDecimals(0)
                    field.setMinimum(1)
                for lbl in time_labels:
                    lbl.setText(u'ms')
            elif self.tscale == 1:
                for field in time_inputs:
                    field.setDecimals(3)
                    field.setMinimum(0.001)
                    if not setup:
                        field.setValue(field.value()*0.001)
                    field.setMaximum(20)
                for lbl in time_labels:
                    lbl.setText(u's')
            else:
                print self.tscale
                raise Exception(u"Invalid time scale")

        if fscale != self.fscale:
            self.fscale = fscale

            AbstractStimulusComponent.update_fscale(self.fscale)
            frequency_inputs = self.frequency_inputs + AbstractEditorWidget.funit_fields
            frequency_labels = self.frequency_labels + AbstractEditorWidget.funit_labels

            self.display.set_fscale(self.fscale)
            self.calibration_display.set_fscale(self.fscale)

            if self.fscale == 1000:
                for field in frequency_inputs:
                    field.setDecimals(3)
                    field.setMinimum(0.001)
                    if not setup:
                        field.setValue(field.value()/1000)
                    field.setMaximum(500)
                for lbl in frequency_labels:
                    lbl.setText(u'kHz')

            elif self.fscale == 1:
                for field in frequency_inputs:
                    field.setMaximum(500000)
                    if not setup:
                        field.setValue(field.value()*1000)
                    field.setDecimals(0)
                    field.setMinimum(1)
                for lbl in frequency_labels:
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
        savedict['windowsz'] = self.ui.windowsz_spnbx.value()
        savedict['raster_bounds'] = self.display.spiketrace_plot.get_raster_bounds()
        savedict['specargs'] = self.spec_args
        savedict['view_settings'] = self.view_settings
        savedict['calvals'] = self.calvals
        savedict['calparams'] = self.acqmodel.calibration_template()
        savedict['calreps'] = self.ui.calibration_widget.ui.nreps_spnbx.value()

        # parameter settings
        for stim in self.explore_stimuli:
            editor = self.ui.parameter_stack.widget_for_name(stim.name)
            editor.saveToObject()
            savedict[stim.name] = stim.stateDict()

        savedict = convert2native(savedict)
        with open(fname, 'w') as jf:
            json.dump(savedict, jf)

    def load_inputs(self, fname):
        inputsfname = os.path.join(systools.get_appdir(), fname)
        try:
            with open(inputsfname, 'r') as jf:
                inputsdict = json.load(jf)
        except:
            logger = logging.getLogger('main')
            logger.exception("Unable to load app data")
            inputsdict = {}
        
        # set default values
        homefolder = os.path.join(os.path.expanduser("~"), "audiolab_data")

        self.ui.thresh_spnbx.setValue(inputsdict.get('threshold', 0.5))
        self.stashed_aisr = inputsdict.get('aisr', 100)
        self.ui.aisr_spnbx.setValue(self.stashed_aisr)
        self.ui.windowsz_spnbx.setValue(inputsdict.get('windowsz', 100))
        self.ui.binsz_spnbx.setValue(inputsdict.get('binsz', 5))        
        self.savefolder = inputsdict.get('savefolder', homefolder)
        self.savename = inputsdict.get('savename', "untitled")
        self.saveformat = inputsdict.get('saveformat', 'hdf5')
        self.ui.ex_nreps_spnbx.setValue(inputsdict.get('ex_nreps', 5))
        self.ui.reprate_spnbx.setValue(inputsdict.get('reprate', 1))
        self.display.spiketrace_plot.set_raster_bounds(inputsdict.get('raster_bounds', (0.5,1)))
        self.spec_args = inputsdict.get('specargs',{u'nfft':512, u'window':u'hanning', u'overlap':90, 'colormap':{'lut':None, 'state':None, 'levels':None}})
        self.display.set_spec_args(**self.spec_args)  
        self.view_settings = inputsdict.get('view_settings', {'fontsz': 10, 'display_attributes':{}})
        self.ui.stim_details.set_display_attributes(self.view_settings['display_attributes'])
        font = QtGui.QFont()
        font.setPointSize(self.view_settings['fontsz'])
        QtGui.QApplication.setFont(font)
        self.ui.calibration_widget.ui.nreps_spnbx.setValue(inputsdict.get('calreps', 5))
        self.calvals = inputsdict.get('calvals', {'calf':20000, 'caldb':100, 
                                      'calv':0.1, 'use_calfile':False, 
                                      'frange':(5000, 1e5), 'calname': ''})
        self.calvals['use_calfile'] = False
        self.calvals['calname'] = ''
        self.acqmodel.set_params(**self.calvals)
        self.acqmodel.set_calibration(None, self.calvals['calf'], self.calvals['frange'])
        tscale = inputsdict.get('tscale', 0.001)
        fscale = inputsdict.get('fscale', 1000)

        self.tscale = 0
        self.fscale = 0
        self.update_unit_labels(tscale, fscale, setup=True)

        cal_template = inputsdict.get('calparams', None)
        if cal_template is not None:
            self.acqmodel.load_calibration_template(cal_template)

        for stim in self.explore_stimuli:
            try:
                stim.loadState(inputsdict[stim.name])

            except KeyError:
                logger = logging.getLogger('main')
                logger.exception('Unable to load saved inputs for {}'.format(stim.__class__))

        self.ui.aosr_spnbx.setValue(self.acqmodel.explore_genrate()/self.fscale)

    def closeEvent(self, event):
        self.save_inputs(self.inputs_filename)

        # save GUI size
        settings = QtCore.QSettings("audiolab")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        logger = logging.getLogger('main')
        logger.info('All user settings saved')

