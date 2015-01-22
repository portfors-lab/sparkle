import os
import json
import logging

import yaml
from QtWrapper import QtCore, QtGui

import spikeylab.tools.systools as systools
from spikeylab.tools.util import convert2native
from spikeylab.gui.stim.abstract_editor import AbstractEditorWidget
from spikeylab.gui.stim.components.qcomponents import wrapComponent
from spikeylab.stim.abstract_component import AbstractStimulusComponent
from spikeylab.gui.stim.stimulusview import StimulusView
from spikeylab.gui.stim.auto_parameter_view import SmartDelegate
from main_control_form import Ui_ControlWindow
from spikeylab.tools.systools import get_src_directory
from spikeylab.gui.stim.smart_spinbox import SmartSpinBox
from spikeylab.gui.plotting.pyqtgraph_widgets import SpecWidget

with open(os.path.join(get_src_directory(),'settings.conf'), 'r') as yf:
    config = yaml.load(yf)
USE_ATTEN = config['use_attenuator']
MPHONE_CALDB = config['microphone_calibration_db']

class ControlWindow(QtGui.QMainWindow):
    """ Base class just to handle loading, saving, and validity of user inputs"""
    def __init__(self, inputsFilename, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
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
        self.timeInputs = [self.ui.windowszSpnbx, self.ui.binszSpnbx]
        self.frequencyInputs = [self.ui.aisrSpnbx]
            
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

    def verifyInputs(self, mode):
        """Goes through and checks all stimuli and input settings are valid
        and consistent. Prompts user with a message if there is a condition
        that would prevent acquisition.

        :param mode: The mode of acquisition trying to be run. Options are
            'chart', or anthing else ('explore', 'protocol', 'calibration')
        :type mode: str
        :returns: bool -- Whether all inputs and stimuli are valid
        """
        if mode == 'chart':
            if self.ui.aisrSpnbx.value()*self.fscale > 100000:
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
                failmsg = calibration_stimulus.verifyExpanded(samplerate=self.ui.aisrSpnbx.value())
                if failmsg:
                    failmsg = failmsg.replace('Generation', 'Recording')
                    QtGui.QMessageBox.warning(self, "Invalid Input", failmsg)
                    return False
            if USE_ATTEN and not self.acqmodel.attenuator_connection():
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
        savedict['threshold'] = self.ui.threshSpnbx.value()
        savedict['binsz'] = self.ui.binszSpnbx.value()
        savedict['aisr'] = self.ui.aisrSpnbx.value()
        savedict['tscale'] = self.tscale
        savedict['fscale'] = self.fscale
        savedict['saveformat'] = self.saveformat
        savedict['ex_nreps'] = self.ui.exploreStimEditor.repCount()
        savedict['reprate'] = self.ui.reprateSpnbx.value()
        savedict['windowsz'] = self.ui.windowszSpnbx.value()
        savedict['raster_bounds'] = self.display.spiketracePlot.getRasterBounds()
        savedict['specargs'] = self.specArgs
        savedict['viewSettings'] = self.viewSettings
        savedict['calvals'] = self.calvals
        savedict['calparams'] = self.acqmodel.calibration_template()
        savedict['calreps'] = self.ui.calibrationWidget.ui.nrepsSpnbx.value()
        savedict['mphonesens'] = self.ui.mphoneSensSpnbx.value()
        savedict['mphonedb'] = self.ui.mphoneDBSpnbx.value()

        # parameter settings -- save all tracks present
        savedict['explorestims'] = self.ui.exploreStimEditor.saveTemplate()

        # filter out and non-native python types that are not json serializable
        savedict = convert2native(savedict)
        with open(fname, 'w') as jf:
            json.dump(savedict, jf)

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
            logger.exception("Unable to load app data")
            inputsdict = {}

        self.ui.threshSpnbx.setValue(inputsdict.get('threshold', 0.5))
        self.stashedAisr = inputsdict.get('aisr', 100000)
        self.ui.aisrSpnbx.setValue(self.stashedAisr)
        self.ui.windowszSpnbx.setValue(inputsdict.get('windowsz', 0.1))
        self.ui.binszSpnbx.setValue(inputsdict.get('binsz', 0.005))        
        self.saveformat = inputsdict.get('saveformat', 'hdf5')
        self.ui.exploreStimEditor.setReps((inputsdict.get('ex_nreps', 5)))
        self.ui.reprateSpnbx.setValue(inputsdict.get('reprate', 1))
        self.display.spiketracePlot.setRasterBounds(inputsdict.get('raster_bounds', (0.5,1)))
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

        # self.ui.aosrSpnbx.setValue(self.acqmodel.explore_genrate()/self.fscale)

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

