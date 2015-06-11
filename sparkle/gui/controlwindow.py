import gc
import json
import logging
import os

import yaml

import sparkle.tools.systools as systools
from main_control_form import Ui_ControlWindow
from sparkle.QtWrapper import QtCore, QtGui
from sparkle.acq.daq_tasks import get_ai_chans, get_ao_chans, get_devices
from sparkle.gui.plotting.pyqtgraph_widgets import SpecWidget
from sparkle.gui.stim.abstract_editor import AbstractEditorWidget
from sparkle.gui.stim.auto_parameter_view import SmartDelegate
from sparkle.gui.stim.components.qcomponents import wrapComponent
from sparkle.gui.stim.smart_spinbox import SmartSpinBox
from sparkle.gui.stim.stimulusview import StimulusView
from sparkle.stim.stimulus_model import StimulusModel
from sparkle.stim.abstract_component import AbstractStimulusComponent
from sparkle.stim.types.stimuli_classes import Vocalization
from sparkle.tools.util import convert2native

with open(os.path.join(systools.get_src_directory(),'settings.conf'), 'r') as yf:
    config = yaml.load(yf)
MPHONE_CALDB = config['microphone_calibration_db']

class ControlWindow(QtGui.QMainWindow):
    """ Base class just to handle loading, saving, and validity of user inputs"""
    def __init__(self, inputsFilename):
        super(ControlWindow, self).__init__()
        self.ui = Ui_ControlWindow()
        self.ui.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # get references to the different plot displays, for easier access
        self.calibrationDisplay = self.ui.plotDock.displays['calibration']
        self.extendedDisplay = self.ui.plotDock.displays['calexp']
        self.scrollplot = self.ui.plotDock.displays['chart']
        self.display = self.ui.plotDock.displays['standard']
        # show default display
        self.ui.plotDock.switchDisplay('standard')

        # make a list of which widgets should be updated when scales are changed
        self.timeInputs = [self.ui.windowszSpnbx, self.ui.binszSpnbx, self.ui.psthStartField, self.ui.psthStopField]
        self.frequencyInputs = [self.ui.aifsSpnbx]
            
        self.ui.exploreStimEditor.setModel(self.acqmodel.explore_stimulus())
        self.ui.exploreStimEditor.addComponentEditor()
        
        # Allow items from the the procotol view to be thrown in trash located
        # on different widget
        self.ui.protocolView.installEventFilter(self.ui.stimulusChoices.trash())
        # load user inputs save from last time GUI was ran
        self.loadInputs(inputsFilename)
        self.inputsFilename = inputsFilename

        # Add available calibration stimuli options to GUI
        # Order matters, in the acquisition manager is hardcoded to expect
        # calibration tone curve at index 2 :(
        for calstim in self.acqmodel.bs_calibrator.get_stims()[::-1]: #tsk
            self.ui.calibrationWidget.addOption(wrapComponent(calstim))
        
        try:
            # reload previous window geometry
            settings = QtCore.QSettings("audiolab")
            if settings is not None:
                self.restoreGeometry(settings.value("geometry").toByteArray())
                self.restoreState(settings.value("windowState").toByteArray())
            else:
                logger = logging.getLogger('main')
                logger.warning('Unable to restore QSettings for audiolab')
            # self.ui.psth.restoreGeometry(settings.value("psth_dock/geometry"))

            self.ui.protocolProgressBar.setStyleSheet("QProgressBar { text-align: center; }")
            self.ui.protocolProgressBar.setMinimum(0)
        except Exception as e:
            logger = logging.getLogger('main')
            logger.exception("Error Initializing main GUI")

        # connect drag label signals
        for label in self.ui.stimulusChoices.labels():
            label.dragActive.connect(self.ui.protocolView.showBorder)

        # make sure garbage collection ALWAYS happens in GUI thread,
        # UI elements collected outside of main thread can crash the program
        self.garbage_timer = QtCore.QTimer(self)
        self.garbage_timer.timeout.connect(gc.collect)
        gc.disable()
        self.garbage_timer.start(5000)

    def verifyInputs(self, mode):
        """Goes through and checks all stimuli and input settings are valid
        and consistent. Prompts user with a message if there is a condition
        that would prevent acquisition.

        :param mode: The mode of acquisition trying to be run. Options are
            'chart', or anthing else ('explore', 'protocol', 'calibration')
        :type mode: str
        :returns: bool -- Whether all inputs and stimuli are valid
        """
        if len(self._aichans) < 1:
            failmsg = "Must have at least one input channel selected"
            QtGui.QMessageBox.warning(self, "Invalid Setting", failmsg)
            return False
        if mode == 'chart':
            if self.ui.aifsSpnbx.value()*self.fscale > 100000:
                QtGui.QMessageBox.warning(self, "Invalid Input", "Recording samplerate cannot exceed 100kHz for chart acquisition")
                return False
        elif mode is not None:
            # if (1./self.ui.reprateSpnbx.value()) < self.ui.windowszSpnbx.value()*self.tscale + 0.05:
            #     QtGui.QMessageBox.warning(self, "Invalid Input", "A minimum of 50ms time between repetitions required. Current interval {}, required {}".format((1./self.ui.reprateSpnbx.value()), self.ui.windowszSpnbx.value()*self.tscale + 0.05))
            #     return False
            if self.ui.tabGroup.currentWidget().objectName() == 'tabExplore':
                # each widget should be in charge of putting its own stimulus together
                self.ui.exploreStimEditor.saveToObject()
                failmsg = self.ui.exploreStimEditor.verify(self.ui.windowszSpnbx.value())
                if failmsg:
                    QtGui.QMessageBox.warning(self, "Invalid Input", failmsg)
                    return False
                # if selectedStim.intensity() > self.calvals['caldb']:
                #     QtGui.QMessageBox.warning(self, "Invalid Input",
                #             "Intensity must be below calibrated maximum {}dB SPL".format(self.calvals['caldb']))
                #     return False
            elif self.ui.tabGroup.currentWidget().objectName() == 'tabProtocol':
                protocol_model = self.acqmodel.protocol_model()
                # protocol delegates to each test to verify itself and report
                failure = protocol_model.verify(float(self.ui.windowszSpnbx.value()))
                if failure:
                    QtGui.QMessageBox.warning(self, "Invalid Input", failure)
                    return False
            elif self.ui.tabGroup.currentWidget().objectName() == 'tabCalibrate':
                if len(self._aichans) > 1:
                    failmsg = "Speaker calibration only supported for single channel, currently {} channels selected; select 1 input channel.".format(len(self._aichans))
                    QtGui.QMessageBox.warning(self, "Invalid Setting", failmsg)
                    return False
                # get what stimulus is about to be presented
                if self.ui.calibrationWidget.ui.savecalCkbx.isChecked() or not self.ui.calibrationWidget.currentSelection() == 'Tone Curve':
                    calibration_stimulus = self.acqmodel.calibration_stimulus('noise')
                    self.ui.calibrationWidget.saveToObject()
                else:
                    calibration_stimulus = self.acqmodel.calibration_stimulus('tone')

                failmsg = calibration_stimulus.verify(float(self.ui.windowszSpnbx.value()))
                if failmsg:
                    QtGui.QMessageBox.warning(self, "Invalid Input", failmsg)
                    return False
                # also check that the recording samplerate is high enough in this case
                failmsg = calibration_stimulus.verifyExpanded(samplerate=self.ui.aifsSpnbx.value())
                if failmsg:
                    failmsg = failmsg.replace('Generation', 'Recording')
                    QtGui.QMessageBox.warning(self, "Invalid Input", failmsg)
                    return False
            if self.advanced_options['use_attenuator'] and not self.acqmodel.attenuator_connection():
                failmsg = "Error Connection to attenuator, make sure it it turned on and connected, and try again"
                QtGui.QMessageBox.warning(self, "Connection Error", failmsg)
                return False
        return True

    def updateUnitLabels(self, tscale, fscale):
        """When the GUI unit scale changes, it is neccessary to update
        the unit labels on all fields throughout the GUI. This handles
        The main window, and also notifys other windows to update

        Only supports for conversion between two values :
            
            * seconds and miliseconds for time
            * Hz and kHz for frequency

        :param tscale: Time scale to update to either 's' or 'ms'
        :type tscale: str
        :param fscale: Frequency scale to update to either 'Hz' or 'kHz'
        :type fscale: str
        """
        AbstractEditorWidget.updateScales(tscale, fscale)
        SmartDelegate.updateScales(tscale, fscale)

        # purges stored label references from deleted parent widgets
        AbstractEditorWidget.purgeDeletedWidgets()
            
        self.tscale = tscale

        # updates labels for components
        # add the list of all time unit labels out there to our update
        # list here
        time_inputs = self.timeInputs + AbstractEditorWidget.tunit_fields

        # now go through our list of labels and fields and scale/update
        for field in time_inputs:
            field.setScale(tscale)

        self.fscale = fscale

        # add the list of all frequency unit labels out there to our update
        # list here
        frequency_inputs = self.frequencyInputs + AbstractEditorWidget.funit_fields

        # now go through our list of labels and fields and scale/update
        for field in frequency_inputs:
            field.setScale(fscale)

    def reset_device_channels(self):
        """Updates the input channel selection boxes based on the current
        device name stored in this object"""
        # clear boxes first
        self.ui.aochanBox.clear()
        devname = self.advanced_options['device_name']
        device_list = get_devices()
        if devname in device_list:
            cnames = get_ao_chans(devname)
            self.ui.aochanBox.addItems(cnames)
            cnames = get_ai_chans(devname)
            # filter list for channels that are present in current device
            self._aichans = [chan for chan in self._aichans if chan in cnames]
            self._aichan_details = {chan: deets for chan, deets in self._aichan_details.items() if chan in cnames}
        elif devname == '' and len(device_list) > 0:
            devname = device_list[0]
            cnames = get_ao_chans(devname)
            self.ui.aochanBox.addItems(cnames)
            self.advanced_options['device_name'] = devname
            self._aichans = []
            self._aichan_details = {}
        else:
            self._aichans = []
            self._aichan_details = {}

        self.ui.chanNumLbl.setText(str(len(self._aichans)))
        # remove all plots and re-add from new list
        self.display.removeResponsePlot(*self.display.responseNameList())
        self.display.addResponsePlot(*self._aichans)
        # update details on plots
        for name, deets in self._aichan_details.items():
            self.display.setThreshold(deets['threshold'], name)
            self.display.setRasterBounds(deets['raster_bounds'], name)
            self.display.setAbs(deets['abs'], name)

        # can't find a function in DAQmx that gets the trigger
        # channel names, so add manually
        self.ui.trigchanBox.addItems(['/'+devname+'/PFI0', '/'+devname+'/PFI1'])

    def saveInputs(self, fname):
        """Save the values in the input fields so they can be loaded
        next time the GUI is run

        :param fname: file path of location to store values at
        :type fname: str
        """
        # save current inputs to file for loading next time
        if not fname:
            return
            
        appdir = systools.get_appdir()
        if not os.path.isdir(appdir):
            os.makedirs(appdir)
        fname = os.path.join(appdir, fname)

        savedict = {}
        savedict['binsz'] = self.ui.binszSpnbx.value()
        savedict['aifs'] = self.ui.aifsSpnbx.value()
        savedict['tscale'] = self.tscale
        savedict['fscale'] = self.fscale
        savedict['saveformat'] = self.saveformat
        savedict['ex_nreps'] = self.ui.exploreStimEditor.repCount()
        savedict['reprate'] = self.ui.reprateSpnbx.value()
        savedict['windowsz'] = self.ui.windowszSpnbx.value()
        savedict['specargs'] = self.specArgs
        savedict['viewSettings'] = self.viewSettings
        savedict['calvals'] = self.calvals
        savedict['calparams'] = self.acqmodel.calibration_template()
        savedict['calreps'] = self.ui.calibrationWidget.ui.nrepsSpnbx.value()
        savedict['mphonesens'] = self.ui.mphoneSensSpnbx.value()
        savedict['mphonedb'] = self.ui.mphoneDBSpnbx.value()
        savedict['vocalpaths'] = Vocalization.paths
        savedict['aichans'] = self._aichans
        savedict['aichan_details'] = self._aichan_details

        # parameter settings -- save all tracks present
        savedict['explorestims'] = self.ui.exploreStimEditor.saveTemplate()

        savedict['advanced_options'] = self.advanced_options
        savedict['stim_view_defaults'] = StimulusView.getDefaults()

        # filter out and non-native python types that are not json serializable
        savedict = convert2native(savedict)
        try:
            with open(fname, 'w') as jf:
                json.dump(savedict, jf)
        except:
            logger = logging.getLogger('main')
            logger.exception("Unable to save app data to file: {}".format(fname))

    def loadInputs(self, fname):
        """Load previsouly saved input values, and load them to GUI widgets

        :param fname: file path where stashed input values are stored
        :type fname: str
        """
        inputsfname = os.path.join(systools.get_appdir(), fname)
        try:
            with open(inputsfname, 'r') as jf:
                inputsdict = json.load(jf)
        except:
            logger = logging.getLogger('main')
            logger.warning("Unable to load app data from file: {}".format(inputsfname))
            inputsdict = {}

        # self.display.spiketracePlot.setThreshold(inputsdict.get('threshold', 0.5))
        self._thesholds = inputsdict.get('threshold', {})
        self.stashedAisr = inputsdict.get('aifs', 100000)
        self.ui.aifsSpnbx.setValue(self.stashedAisr)
        self.ui.windowszSpnbx.setValue(inputsdict.get('windowsz', 0.1))
        self.ui.binszSpnbx.setValue(inputsdict.get('binsz', 0.005))        
        self.saveformat = inputsdict.get('saveformat', 'hdf5')
        self.ui.exploreStimEditor.setReps((inputsdict.get('ex_nreps', 5)))
        self.ui.reprateSpnbx.setValue(inputsdict.get('reprate', 1))
        # self.display.spiketracePlot.setRasterBounds(inputsdict.get('raster_bounds', (0.5,1)))
        self.specArgs = inputsdict.get('specargs',{u'nfft':512, u'window':u'hanning', u'overlap':90, 'colormap':{'lut':None, 'state':None, 'levels':None}})
        # self.display.setSpecArgs(**self.specArgs)  
        SpecWidget.setSpecArgs(**self.specArgs)
        self.viewSettings = inputsdict.get('viewSettings', {'fontsz': 10, 'display_attributes':{}})
        self.ui.stimDetails.setDisplayAttributes(self.viewSettings['display_attributes'])
        font = QtGui.QFont()
        font.setPointSize(self.viewSettings['fontsz'])
        QtGui.QApplication.setFont(font)
        self.ui.calibrationWidget.ui.nrepsSpnbx.setValue(inputsdict.get('calreps', 5))
        self.calvals = inputsdict.get('calvals', {'calf':20000, 'caldb':100, 
                                      'calv':0.1, 'use_calfile':False, 
                                      'frange':(5000, 1e5), 'calname': ''})
        self.calvals['use_calfile'] = False
        self.calvals['calname'] = ''
        self.ui.refDbSpnbx.setValue(self.calvals['caldb'])
        self.ui.mphoneSensSpnbx.setValue(inputsdict.get('mphonesens', 0.004))
        self.ui.mphoneDBSpnbx.setValue(MPHONE_CALDB)
        # self.ui.mphoneDBSpnbx.setValue(inputsdict.get('mphonedb', 94))
        Vocalization.paths = inputsdict.get('vocalpaths', [])

        # load the previous sessions scaling
        self.tscale = inputsdict.get('tscale', SmartSpinBox.MilliSeconds)
        self.fscale = inputsdict.get('fscale', SmartSpinBox.kHz)
        try:
            self.updateUnitLabels(self.tscale, self.fscale)
        except:
            self.tscale = 'ms'
            self.fscale = 'kHz'
            self.updateUnitLabels(self.tscale, self.fscale)

        cal_template = inputsdict.get('calparams', None)
        if cal_template is not None:
            try:
                self.acqmodel.load_calibration_template(cal_template)
            except:
                logger = logging.getLogger('main')
                logger.exception("Unable to load previous calibration settings")
        else:
            logger = logging.getLogger('main')
            logger.debug('No saved calibration stimului inputs')

        if 'explorestims' in inputsdict:
            self.ui.exploreStimEditor.loadTemplate(inputsdict['explorestims'])
        else:
            logger = logging.getLogger('main')
            logger.debug('No saved explore stimului inputs')

        # set defaults then merge
        self.advanced_options = {'device_name':'', 
                                 'max_voltage':1.5,
                                 'device_max_voltage': 10.0,
                                 'volt_amp_conversion': 0.1,
                                 'use_attenuator': False }
        if 'advanced_options' in inputsdict:
            self.advanced_options.update(inputsdict['advanced_options'])
        StimulusModel.setMaxVoltage(self.advanced_options['max_voltage'], self.advanced_options['device_max_voltage'])
        self.display.setAmpConversionFactor(self.advanced_options['volt_amp_conversion'])
        if self.advanced_options['use_attenuator']:
            self.acqmodel.attenuator_connection(True)
        else:
            self.acqmodel.attenuator_connection(False)
        self._aichans = inputsdict.get('aichans', [])
        self._aichan_details = inputsdict.get('aichan_details', {})
        for name, deets in self._aichan_details.items():
            # make sure all field as present in details for each channel
            self._aichan_details[name]['threshold'] = deets.get('threshold', 5)
            self._aichan_details[name]['polarity'] = deets.get('polarity', 1)
            self._aichan_details[name]['raster_bounds'] = deets.get('raster_bounds', (0.5,0.9))
            self._aichan_details[name]['abs'] = deets.get('abs', True)

        self.reset_device_channels()

        stim_defaults = inputsdict.get('stim_view_defaults', {})
        for name, state in stim_defaults.items():
            StimulusView.updateDefaults(name, state)

    def closeEvent(self, event):
        """Closes listening threads and saves GUI data for later use.

        Re-implemented from :qtdoc:`QWidget`
        """
        self.acqmodel.stop_listening() # close listener threads
        self.saveInputs(self.inputsFilename)

        # save GUI size
        settings = QtCore.QSettings("audiolab")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        logger = logging.getLogger('main')
        logger.info('All user settings saved')

        self.garbage_timer.stop()
        gc.enable()
