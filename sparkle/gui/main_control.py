import logging
import os, sys
import time
import threading
import traceback
import inspect

import numpy as np
import yaml

from controlwindow import ControlWindow
from sparkle.QtWrapper import QtCore, QtGui
from sparkle.acq.daq_tasks import get_ai_chans
from sparkle.gui.dialogs import CalibrationDialog, CellCommentDialog, \
    SavingDialog, ScaleDialog, SpecDialog, ViewSettingsDialog, \
    VocalPathDialog, ChannelDialog, AdvancedOptionsDialog
from sparkle.gui.load_frame import LoadFrame
from sparkle.gui.plotting.pyqtgraph_widgets import ProgressWidget, \
    SimplePlotWidget, SpecWidget
from sparkle.gui.qprotocol import QProtocolTabelModel
from sparkle.gui.stim.qstimulus import QStimulusModel
from sparkle.gui.wait_widget import WaitWidget
from sparkle.run.acquisition_manager import AcquisitionManager
from sparkle.stim.stimulus_model import StimulusModel
from sparkle.stim.types.stimuli_classes import Vocalization
from sparkle.tools import spikestats
from sparkle.tools.audiotools import audioread, calc_db, calc_spectrum, \
    calc_summed_db, rms, signal_amplitude, sum_db
from sparkle.tools.qsignals import ProtocolSignals
from sparkle.tools.systools import get_src_directory
from sparkle.tools.uihandler import assign_uihandler_slot
from sparkle.tools.util import clearLayout

RED = QtGui.QPalette()
RED.setColor(QtGui.QPalette.Foreground,QtCore.Qt.red)
GREEN = QtGui.QPalette()
GREEN.setColor(QtGui.QPalette.Foreground,QtCore.Qt.darkGreen)
GREEN.setColor(QtGui.QPalette.Background,QtCore.Qt.green)
BLACK = QtGui.QPalette()
BLACK.setColor(QtGui.QPalette.Foreground,QtCore.Qt.black)

GREENSS = "QLabel { background-color : limegreen; color : darkgreen; }"
REDSS = "QLabel { background-color : transparent; color : red; }"

with open(os.path.join(get_src_directory(),'settings.conf'), 'r') as yf:
    config = yaml.load(yf)
REFFREQ = config['reference_frequency']
REFVOLTAGE = config['reference_voltage']


def log_handle(func):
    def handle(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except Exception, e:
            msg = str(e) + '\nTraceback:\n\n'
            tb = traceback.format_tb(sys.exc_info()[2])
            for line in tb:
                msg += line
            logger = logging.getLogger('main')
            logger.exception(msg)
            raise

    return handle

def decorate_all_methods(decorator):
    def decorate(cls):
        for name, meth in inspect.getmembers(cls, inspect.ismethod):
            if '__' not in name:
                setattr(cls, name, decorator(getattr(cls, name)))
        return cls
    return decorate

@decorate_all_methods(log_handle)
class MainWindow(ControlWindow):
    """Main GUI for the application. Run the main fucntion of this file"""
    _polarity = 1
    fileLoaded = QtCore.Signal(str)
    def __init__(self, inputsFilename='', datafile=None, filemode='w-', hidetabs=False):
        # set up model and stimlui first, 
        # as saved configuration relies on this
        self.acqmodel = AcquisitionManager()
        if datafile is not None:
            self.acqmodel.load_data_file(datafile, filemode)
            fname = os.path.basename(self.acqmodel.current_data_file())
        else:
            fname = None

        super(MainWindow, self).__init__(inputsFilename)

        if datafile is not None:
            self.ui.reviewer.setDataObject(self.acqmodel.datafile)
            self.ui.dataFileLbl.setText(fname)

        self.ui.cellIDLbl.setText(str(self.acqmodel.current_cellid))

        self.ui.startBtn.clicked.connect(self.onStart)
        self.ui.stopBtn.clicked.connect(self.onStop)
        self.ui.startChartBtn.clicked.connect(self.onStartChart)
        self.ui.stopChartBtn.clicked.connect(self.onStopChart)

        self.ui.runningLabel.setStyleSheet(REDSS)

        self.applyCalibration = False
        self.calpeak = None

        self.liveLock = QtCore.QMutex()

        self.display.thresholdUpdated.connect(self.updateThresh)
        self.display.colormapChanged.connect(self.relayCMapChange)
        self.display.polarityInverted.connect(self.setPolarity)
        self.display.rasterBoundsUpdated.connect(self.updateRasterBounds)
        self.display.absUpdated.connect(self.updateAbsThreshold)

        self.ui.protocolView.setModel(QProtocolTabelModel(self.acqmodel.protocol_model()))
        self.ui.calibrationWidget.setCurveModel(QStimulusModel(self.acqmodel.calibration_stimulus('tone')))

        self.signals = ProtocolSignals()
        self.signals.response_collected.connect(self.displayResponse)
        self.signals.response_collected.connect(self.processResponse)
        self.signals.calibration_response_collected.connect(self.displayCalibrationResponse)
        self.signals.average_response.connect(self.displayDbResult)
        self.signals.stim_generated.connect(self.displayStim)
        self.signals.warning.connect(self.setStatusMsg)
        self.signals.ncollected.connect(self.updateChart)
        self.signals.current_trace.connect(self.reportProgress)
        self.signals.current_rep.connect(self.reportRep)
        self.signals.group_finished.connect(self.onGroupDone)
        self.signals.tuning_curve_started.connect(self.spawnTuningCurve)
        self.signals.tuning_curve_response.connect(self.displayTuningCurve)
        self.signals.over_voltage.connect(self.reportOverV)
        for name, signal in self.signals.iteritems():
            self.acqmodel.set_queue_callback(name, signal.emit)
        self.acqmodel.start_listening()

        self.ui.windowszSpnbx.valueChanged.connect(self.setCalibrationDuration)

        self.activeOperation = None

        self.setCalibrationDuration()

        # always start in windowed mode
        self.modeToggled('Windowed')
        self.prevTab = str(self.ui.tabGroup.tabText(self.ui.tabGroup.currentIndex())).lower()
        # always show plots on load
        self.ui.plotDock.setVisible(True)
        self.ui.psthDock.setVisible(True)

        self.ui.stopBtn.setEnabled(False)
        self.ui.stopChartBtn.setEnabled(False)

        logger = logging.getLogger('main')
        assign_uihandler_slot(logger, self.ui.logTxedt.appendHtml)


        self.calvals['calf'] = REFFREQ
        self.calvals['calv'] = REFVOLTAGE
        if self.fscale == 'kHz':
            scalar = 1000
        elif self.fscale == 'Hz':
            scalar = 1
        self.ui.refToneLbl.setText("Intensity of {}{} Tone at {}V".format(REFFREQ/scalar, self.fscale, REFVOLTAGE))
        self.acqmodel.set(**self.calvals)
        self.acqmodel.set_calibration(None, self.calvals['calf'], self.calvals['frange'])
        self.calpeak = None
        self.ui.tabGroup.setCurrentIndex(0)
        
        #updates the microphone calibration in the acquisition model
        self.updateMicrophoneCalibration(0) # arg is place holder

        # connect data reviewer to data display
        self.ui.reviewer.reviewDataSelected.connect(self.displayOldData)
        self.ui.reviewer.testSelected.connect(self.displayOldProgressPlot)

        # connect file load dialog to update ui
        self.fileLoaded.connect(self.updateDataFileStuffs)

        if hidetabs:
            print "Hiding search and calibrate operations"
            for tabIndex in reversed(range(self.ui.tabGroup.count())):
                txt = str(self.ui.tabGroup.tabText(tabIndex)).lower()
                if txt == 'calibration' or txt == 'explore':
                    self.ui.tabGroup.removeTab(tabIndex)

            self.ui.reviewLbl.setText(' - REVIEW MODE')
            self.ui.startBtn.setEnabled(False)

        # hide trigger channel - not currently supported, maybe later
        self.ui.trigCkbx.setVisible(False)
        self.ui.trigchanBox.setVisible(False)
        # also hide chart ability, until that is working
        self.ui.label_17.setVisible(False)
        self.ui.modeCmbx.setVisible(False)

        logger.info("PROGRAM LOADED -- waiting for user")

    def addInputChannel(self):
        newChannelCmbx = QtGui.QComboBox()
        cnames = get_ai_chans(DEVNAME.encode())
        newChannelCmbx.addItems(cnames)

        newThreshField = QtGui.QDoubleSpinBox()
        newThreshField.setSuffix('V')
        
        self.inChanCmbxs

    def connectUpdatable(self, connect):
        if connect:
            self.ui.startBtn.clicked.disconnect()
            self.ui.startBtn.clicked.connect(self.onUpdate)
            self.ui.binszSpnbx.valueChanged.connect(self.onUpdate)
            self.ui.windowszSpnbx.valueChanged.disconnect()
            self.ui.windowszSpnbx.valueChanged.connect(self.onUpdate)
            self.ui.exploreStimEditor.valueChanged.connect(self.onUpdate)
            self.ui.actionSet_Scale.setEnabled(False)
            self.ui.actionSave_Options.setEnabled(False)
            self.ui.actionSet_Calibration.setEnabled(False)
            self.ui.trigCkbx.stateChanged.connect(self.onUpdate)
            self.ui.trigchanBox.currentIndexChanged.connect(self.onUpdate)
        else:
            try:
                self.ui.binszSpnbx.valueChanged.disconnect()
                self.ui.exploreStimEditor.valueChanged.disconnect()
                # this should be connected when search ISN'T running
                self.ui.windowszSpnbx.valueChanged.disconnect()
                self.ui.windowszSpnbx.valueChanged.connect(self.setCalibrationDuration)
                self.ui.startBtn.clicked.disconnect()
                self.ui.startBtn.clicked.connect(self.onStart)
                self.ui.actionSet_Scale.setEnabled(True)
                self.ui.actionSave_Options.setEnabled(True)
                self.ui.actionSet_Calibration.setEnabled(True)
                self.ui.trigCkbx.stateChanged.disconnect()
                self.ui.trigchanBox.currentIndexChanged.disconnect()

            except TypeError:
                # disconnecting already disconnected signals throws TypeError
                pass

    def onStart(self, calTone=False):
        # set plot axis to appropriate limits
        # first time set up data file
        if not self.verifyInputs('windowed'):
            return

        # disable the components we don't want changed amid generation
        self.ui.aochanBox.setEnabled(False)
        self.ui.aifsSpnbx.setEnabled(False)
        reprate = self.ui.reprateSpnbx.setEnabled(False)
        self.ui.stopBtn.setEnabled(True)
        self.plotProgress = False
        self.ui.protocolProgressBar.setValue(0)

        self.acqmodel.set(reprate=self.ui.reprateSpnbx.value())

        if self.currentMode == 'windowed':
            self.ui.aichanBtn.setEnabled(False)
            self.ui.runningLabel.setText(u"RECORDING")
            self.ui.runningLabel.setStyleSheet(GREENSS)

        if calTone:
            return
        elif self.ui.tabGroup.currentWidget().objectName() == 'tabExplore':
            self.runExplore()
        elif self.ui.tabGroup.currentWidget().objectName() == 'tabProtocol':
            self.runProtocol()
        elif self.ui.tabGroup.currentWidget().objectName() == 'tabCalibrate':
            self.runCalibration()
        else: 
            raise Exception("unrecognized tab selection")

    def onStartChart(self):
        if not self.verifyInputs('chart'):
            return

        self.runChart()
        self.ui.runningLabel.setText(u"RECORDING")
        self.ui.runningLabel.setStyleSheet(GREENSS)
        self.ui.startChartBtn.setEnabled(False)
        self.ui.aichanBtn.setEnabled(False)
        self.ui.aifsSpnbx.setEnabled(False)
        self.ui.stopChartBtn.setEnabled(True)
        self.ui.windowszSpnbx.valueChanged.connect(self.updateScollingWindowsize)

    def onUpdate(self, foo=None):
        if not self.verifyInputs(self.activeOperation):
            return

        aochan = str(self.ui.aochanBox.currentText())
        acq_rate = self.ui.aifsSpnbx.value()

        winsz = float(self.ui.windowszSpnbx.value())
        binsz = float(self.ui.binszSpnbx.value())

        nbins = np.ceil(winsz/binsz)
        bin_centers = (np.arange(nbins)*binsz)+(binsz/2)
        self.ui.psth.setBins(bin_centers)
        self.ui.psthStopField.setMaximum(winsz)
        self.ui.psthStartField.setMaximum(winsz)
        if self.ui.trigCkbx.isChecked():
            trigger = str(self.ui.trigchanBox.currentText())
        else:
            trigger = None
        self.acqmodel.set(aochan=aochan, aichan=self._aichans, acqtime=winsz,
                          aifs=acq_rate, binsz=binsz, trigger=trigger)
        self.binsz = binsz

        self.display.setXlimits((0,winsz))

        self.nreps = None
        if self.ui.tabGroup.currentWidget().objectName() == 'tabExplore':
            nreps = self.ui.exploreStimEditor.repCount()
            self.acqmodel.reset_explore_stim()
            self.display.setNreps(nreps)
            self.nreps = nreps
        elif self.ui.tabGroup.currentWidget().objectName() == 'tabProtocol':
            nreps = self.acqmodel.protocol_reps()
            self.display.setNreps(nreps)
            self.nreps = nreps
        if self.currentMode == 'chart':
            return winsz, acq_rate
            
    def onStop(self, foo=False):
        self.acqmodel.halt() # stops generation, and acquisition if linked
        if self.currentMode == 'windowed':
            self.activeOperation = None
            self.liveLock.unlock()
            self.ui.runningLabel.setText(u"OFF")
            self.ui.runningLabel.setStyleSheet(REDSS)
            self.ui.aichanBtn.setEnabled(True)
            self.connectUpdatable(False)
        self.ui.startBtn.setEnabled(True)
        self.ui.stopBtn.setText("Stop")
        self.ui.startBtn.setText('Start')
        self.ui.stopBtn.clicked.disconnect()
        self.ui.stopBtn.clicked.connect(self.onStop)

        if str(self.ui.tabGroup.tabText(self.ui.tabGroup.currentIndex())).lower() != 'calibration':
            self.ui.aifsSpnbx.setEnabled(True)
        else:
            self.ui.startBtn.setText('Calibrate Speaker')
        self.ui.aochanBox.setEnabled(True)
        reprate = self.ui.reprateSpnbx.setEnabled(True)
        self.ui.stopBtn.setEnabled(False)
        self.ui.protocolProgressBar.setStyleSheet("QProgressBar { text-align: center; } QProgressBar::chunk {background-color: grey; width: 10px; margin-top: 1px; margin-bottom: 1px}")

    def stopCalTone(self):
        self.onStop()
        self.ui.calToneBtn.setText('Start')
        self.ui.calToneBtn.clicked.disconnect()
        self.ui.calToneBtn.clicked.connect(self.playCalTone)

    def onStopChart(self):
        self.acqmodel.stop_chart()
        self.ui.startChartBtn.setEnabled(True)
        self.activeOperation = None
        self.liveLock.unlock()
        self.ui.runningLabel.setText(u"OFF")
        self.ui.runningLabel.setStyleSheet(REDSS)
        self.ui.aichanBtn.setEnabled(True)
        self.ui.aifsSpnbx.setEnabled(True)
        self.ui.stopChartBtn.setEnabled(False)
        self.ui.windowszSpnbx.valueChanged.disconnect()
        self.ui.windowszSpnbx.valueChanged.connect(self.setCalibrationDuration)

    def onGroupDone(self, halted):
        if self.activeOperation == 'calibration':
            #maybe don't call this at all if save is false?
            save = self.ui.calibrationWidget.saveChecked() and not halted
            if save:
                calname, db = self.acqmodel.process_calibration(save)
                ww = self.showWait()
                self.ui.refDbSpnbx.setValue(db)
                self.acqmodel.set_calibration(calname, self.calvals['calf'], self.calvals['frange'])
                self.calvals['calname'] = calname
                self.calvals['use_calfile'] = True
                attenuations, freqs = self.acqmodel.current_calibration()
                self.ui.currentCalLbl.setText(calname)
                self.pw = SimplePlotWidget(freqs, attenuations, parent=self)
                self.pw.setWindowFlags(QtCore.Qt.Window)
                self.pw.setLabels('Frequency', 'Attenuation', 'Calibration Curve', xunits='Hz', yunits='dB')
                ww.close()
                self.pw.show()
        elif self.activeOperation == 'caltone':
            mphone_sens = self.acqmodel.process_mphone_calibration()
            self.ui.mphoneSensSpnbx.setValue(mphone_sens)
        elif self.currentMode == 'windowed':
            cellbox = CellCommentDialog(cellid=self.acqmodel.current_cellid)
            cellbox.setComment(self.ui.commentTxtEdt.toPlainText())
            if cellbox.exec_():
                comment = str(cellbox.comment())
                self.acqmodel.set_group_comment(comment)
            else:
                # save empty comment
                self.acqmodel.set_group_comment('')
            self.ui.commentTxtEdt.clear()

        self.onStop()

        # add group to review data tree
        self.ui.reviewer.update()

    def runChart(self):
        winsz, acq_rate = self.onUpdate()
        # change plot to scrolling plot
        self.scrollplot.setWindowSize(winsz)
        self.scrollplot.setSr(acq_rate)
        self.ui.plotDock.switchDisplay('chart')

        # self.activeOperation = 'chart'
        self.acqmodel.start_chart()

    def updateScollingWindowsize(self):
        winsz = float(self.ui.windowszSpnbx.value())
        self.scrollplot.setWindowSize(winsz)

    def updateChart(self, stimData, responseData):
        self.scrollplot.appendData(stimData, responseData)

    def runExplore(self):
        self.ui.startBtn.setText('Update')
        
        self.connectUpdatable(True)

        self.activeOperation = 'explore'
        self.ui.plotDock.switchDisplay('standard')
        reprate = self.ui.reprateSpnbx.value()
        interval = (1/reprate)*1000

        self.onUpdate()            
        self.acqmodel.run_explore(interval)

    def runProtocol(self):
        self.display.updateSpec(None)

        self.ui.startBtn.setEnabled(False)
        self.ui.stopBtn.setText("Abort")
        self.activeOperation = 'protocol'
        self.ui.plotDock.switchDisplay('standard')

        reprate = self.ui.reprateSpnbx.value()
        interval = (1/reprate)*1000
        
        self.onUpdate()
        if self.currentMode == 'windowed':
            self.acqmodel.setup_protocol(interval)

            # reset style sheet of progress bar
            self.ui.protocolProgressBar.setStyleSheet("QProgressBar { text-align: center; }")
            self.ui.protocolProgressBar.setMaximum(self.acqmodel.protocol_total_count())

            if self.acqmodel.current_cellid == 0:
                # first acquisition, don't ask if it's a new cell
                self.acqmodel.increment_cellid()
            else:
                answer = QtGui.QMessageBox.question(self, 'Cell ID', 'New cell?',
                                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                if answer == QtGui.QMessageBox.Yes:
                    self.acqmodel.increment_cellid()
            self.ui.cellIDLbl.setText(str(self.acqmodel.current_cellid))
            
            self.acqmodel.run_protocol()
        else:
            self.acqmodel.run_chart_protocol(interval)

    def runCalibration(self):
        winsz = float(self.ui.windowszSpnbx.value())
        self.acqmodel.set_calibration_duration(winsz)
        
        self.ui.startBtn.setEnabled(False)
        self.ui.stopBtn.setText("Abort")
        self.activeOperation = 'calibration'

        self.ui.stopBtn.clicked.disconnect()
        self.ui.stopBtn.clicked.connect(self.acqmodel.halt)
        
        self.acqmodel.set_calibration_reps(self.ui.calibrationWidget.ui.nrepsSpnbx.value())

        if self.ui.calibrationWidget.ui.applycalCkbx.isChecked():
            stim_index = self.ui.calibrationWidget.currentIndex()
            self.acqmodel.set_calibration_by_index(stim_index)
            self.ui.calibrationWidget.saveToObject()
            total_presentations = self.acqmodel.calibration_total_count()
        else:
            # Always use noise on saving calibration.
            # BEWARE: Hardcoded to index 1... this could change?!
            self.acqmodel.set_calibration_by_index(1)
            total_presentations = self.ui.calibrationWidget.ui.nrepsSpnbx.value() * 2

        if self.ui.calibrationWidget.ui.applycalCkbx.isChecked() and self.ui.calibrationWidget.isToneCal():
            frequencies, intensities = self.acqmodel.calibration_range()
            self.livecurve = ProgressWidget(list(intensities), (frequencies[0], frequencies[-1]))
            self.livecurve.setLabels('calibration')
            self.ui.progressDock.setWidget(self.livecurve)
            self.ui.plotDock.switchDisplay('calibration')
        else:
            self.ui.plotDock.switchDisplay('calexp')

        reprate = self.ui.reprateSpnbx.value()
        interval = (1/reprate)*1000

        self.onUpdate()

        # reset style sheet of progress bar
        self.ui.protocolProgressBar.setStyleSheet("QProgressBar { text-align: center; }")
        self.ui.protocolProgressBar.setMaximum(total_presentations)

        self.acqmodel.run_calibration(interval, self.ui.calibrationWidget.ui.applycalCkbx.isChecked())

    def mphoneCalibrate(self):
        self.onStart(True)

        self.display.updateSpec(None)

        self.ui.startBtn.setEnabled(False)
        self.activeOperation = 'caltone'

        reprate = self.ui.reprateSpnbx.value()
        interval = (1/reprate)*1000
        
        self.onUpdate()

        # reset style sheet of progress bar
        self.ui.protocolProgressBar.setStyleSheet("QProgressBar { text-align: center; }")
        self.ui.protocolProgressBar.setMaximum(self.acqmodel.mphone_calibration_reps())

        self.acqmodel.run_mphone_calibration(interval)

    def displayResponse(self, times, response, test_num, trace_num, rep_num, trace_info={}):
        assert len(times) != len(response), "times and response not equal"
        assert len(self._aichans) == response.shape[0], 'number of channels does not agree with data dimensions'
        # print 'response signal', response.shape

        fs = self.ui.aifsSpnbx.value()
            
        for chan, name in enumerate(self._aichans):
            channel_data = response[chan,:]
            # convert voltage amplitudes into dB SPL    
            # amp = signal_amplitude(channel_data, fs)
            mphonesens = self.ui.mphoneSensSpnbx.value()
            mphonedb = self.ui.mphoneDBSpnbx.value()
            amp_signal = calc_db(np.amax(channel_data), mphonesens, mphonedb)
            amp_signal_rms = calc_db(rms(channel_data, fs), mphonesens, mphonedb)

            freq, signal_fft = calc_spectrum(channel_data, fs)
            idx = np.where((freq > 5000) & (freq < 100000))
            summed_db0 = calc_summed_db(signal_fft[idx], mphonesens, mphonedb)
            spectrum = calc_db(signal_fft, mphonesens, mphonedb)
            spectrum[0] = 0
            summed_db1 = sum_db(spectrum[idx])
            peakspl = np.amax(spectrum)
            clearLayout(self.ui.splLayout)
            self.ui.splLayout.addWidget(QtGui.QLabel("summed spectrum 1 step"), 0,0)    
            self.ui.splLayout.addWidget(QtGui.QLabel("{:5.1f}".format(summed_db0)), 0,1)
            self.ui.splLayout.addWidget(QtGui.QLabel("summed spectrum db first"), 1,0)    
            self.ui.splLayout.addWidget(QtGui.QLabel("{:5.1f}".format(summed_db1)), 1,1)
            self.ui.splLayout.addWidget(QtGui.QLabel("Peak spectrum"), 2,0)    
            self.ui.splLayout.addWidget(QtGui.QLabel("{:5.1f}".format(peakspl)), 2,1)
            self.ui.splLayout.addWidget(QtGui.QLabel("Max signal (peak)"), 3,0)    
            self.ui.splLayout.addWidget(QtGui.QLabel("{:5.1f}".format(amp_signal)), 3,1)
            self.ui.splLayout.addWidget(QtGui.QLabel("Max signal (rms)"), 4,0)    
            self.ui.splLayout.addWidget(QtGui.QLabel("{:5.1f}".format(amp_signal_rms)), 4,1)

            if self.ui.plotDock.current() == 'standard':
                self.display.updateSpiketrace(times, channel_data, name)
            elif self.ui.plotDock.current() == 'calexp':
                self.extendedDisplay.updateSignal(times, channel_data, plot='response')
                self.extendedDisplay.updateFft(freq, spectrum, plot='response')
                self.extendedDisplay.updateSpec(channel_data, fs, plot='response')

    def displayCalibrationResponse(self, spectrum, freqs, amp):
        mphonesens = self.ui.mphoneSensSpnbx.value()
        mphonedb = self.ui.mphoneDBSpnbx.value()
        masterdb = calc_db(amp, mphonesens, mphonedb)
        spectrum = calc_db(spectrum, mphonesens, mphonedb)
        spectrum[0] = 0
        peakspl = np.amax(spectrum)

        self.calibrationDisplay.updateInFft(freqs, spectrum)

    def displayDbResult(self, f, db, resultdb):
        try:
            self.livecurve.setPoint(f,db,resultdb)
        except:
            print u"WARNING : Problem drawing to calibration plot"
            raise

    def processResponse(self, times, response, test_num, trace_num, rep_num, extra_info={}):
        """Calculate spike times from raw response data"""
        if self.activeOperation == 'calibration' or self.activeOperation == 'caltone' or \
                (self.activeOperation is None and self.ui.tabGroup.currentWidget().objectName() == 'tabCalibrate'):
            # all this is only meaningful for spike recordings
            return

        # not actually guaranteed to happen in order :/
        if rep_num == 0:
            # reset
            self.spike_counts = []
            self.spike_latencies = []
            self.spike_rates = []
            self.ui.psth.clearData()
            self.display.clearRaster()

        fs = 1./(times[1] - times[0])
        count, latency, rate, response_bins = self.do_spike_stats(response, fs)
        # bad news if this changes mid protocol, bin centers are only updated
        # at start of protocol
        binsz = float(self.ui.binszSpnbx.value())
        for chan, name in enumerate(self._aichans):
            if len(response_bins[chan]) > 0:
                bin_times = (np.array(response_bins[chan])*binsz)+(binsz/2)
                self.display.addRasterPoints(bin_times, rep_num, name)
                self.ui.psth.appendData(response_bins[chan], rep_num)

            self.spike_counts.append(count[chan])
            self.spike_latencies.append(latency[chan])
            self.spike_rates.append(rate[chan])

            # sum over ALL channels and reps
            if rep_num == self.nreps - 1 and chan == len(self._aichans)-1:
                total_spikes = sum(self.spike_counts)
                avg_count = np.mean(self.spike_counts)
                avg_latency = np.nanmean(self.spike_latencies)
                avg_rate = np.mean(self.spike_rates)
                self.traceDone(total_spikes, avg_count, avg_latency, avg_rate)
                if 'f' in extra_info:
                    self.displayTuningCurve(extra_info['f'], extra_info['db'], avg_count)
                elif 'all traces' in extra_info:
                    self.displayTuningCurve(trace_num, 'all traces', avg_count)
            
    def do_spike_stats(self, response, fs):
        winsz = float(response.shape[-1])/fs

         # use time subwindow of trace, specified by user
        start_time = self.ui.psthStartField.value()
        if self.ui.psthMaxBox.isChecked():
            stop_time = winsz
        else:
            stop_time = self.ui.psthStopField.value()
        start_index = int(fs*start_time)
        stop_index = int(fs*stop_time)  
        subwinsz = stop_time - start_time

        binsz = float(self.ui.binszSpnbx.value())
        # number of bins to shift spike counts by since we are cropping first part of data
        binshift = int(np.ceil(start_time/binsz))

        count, latency, rate, response_bins = [],[],[],[]
        for chan, name in enumerate(self._aichans):

            # invert polarity affects spike counting
            channel_data = response[chan,:] * self._aichan_details[name]['polarity']
            threshold = self._aichan_details[name]['threshold']
            useabs = self._aichan_details[name]['abs']
            spike_times = spikestats.spike_times(channel_data[start_index:stop_index], threshold, fs, useabs)
            
            count.append(len(spike_times))
            if len(spike_times) > 0:
                latency.append(spike_times[0])
            else:
                latency.append(np.nan)
            rate.append(spikestats.firing_rate(spike_times, subwinsz))

            response_bins.append(spikestats.bin_spikes(spike_times, binsz) + binshift)

        return count, latency, rate, response_bins

    def spawnTuningCurve(self, frequencies, intensities, plotType):
        self.livecurve = ProgressWidget(intensities, (frequencies[0], frequencies[-1]))
        self.livecurve.setLabels(plotType)

        # self.livecurve.show()
        self.ui.progressDock.setWidget(self.livecurve)
        self.plotProgress = True

    def displayTuningCurve(self, f, db, spikeCount):
        if self.plotProgress:
            self.livecurve.setPoint(f, db, spikeCount)

    def displayRaster(self, bins, repnum):
        # convert to times for raster
        if repnum == 0:
            self.ui.psth.clearData()
            self.display.clearRaster()
        if len(bins) > 0:
            binsz = self.binsz
            bin_times = (np.array(bins)*binsz)+(binsz/2)
            self.display.addRasterPoints(bin_times, repnum)
            self.ui.psth.appendData(bins, repnum)
            
    def displayStim(self, signal, fs):
        # self.ui.aofsSpnbx.setValue(fs/self.fscale)
        freq, spectrum = calc_spectrum(signal, fs)
        # spectrum = spectrum / np.sqrt(2)
        spectrum = calc_db(spectrum, self.calvals['calv']) + self.calvals['caldb']
        # print 'spec max', np.amax(spectrum)
        timevals = np.arange(len(signal)).astype(float)/fs
        if self.activeOperation == 'calibration':
            if self.ui.plotDock.current() == 'calexp':
                self.extendedDisplay.updateSignal(timevals, signal, plot='stim')
                self.extendedDisplay.updateFft(freq, spectrum, plot='stim')
                self.extendedDisplay.updateSpec(signal, fs, plot='stim')
            else:
                self.calibrationDisplay.updateOutFft(freq, spectrum)
        else:
            if self.ui.plotDock.current() == 'standard':
                pass
                self.display.updateSignal(timevals, signal)
                self.display.updateFft(freq, spectrum)
                self.display.updateSpec(signal, fs)
            elif self.ui.plotDock.current() == 'calexp':
                self.extendedDisplay.updateSignal(timevals, signal, plot='stim')
                self.extendedDisplay.updateFft(freq, spectrum, plot='stim')
                self.extendedDisplay.updateSpec(signal, fs, plot='stim')
                # this actually auto ranges the response plots, but we only
                # need to do this when the stim changes
                self.extendedDisplay.autoRange()

    def reportProgress(self, itest, itrace, stimInfo):
        # print 'progress', stimInfo
        self.ui.stimDetails.setTestNum(itest)
        self.ui.stimDetails.setTraceNum(itrace)
        self.ui.stimDetails.setDoc(stimInfo)

    def reportRep(self, irep):
        # print 'Rep {}/{}'.format(self.ui.protocolProgressBar.value(), self.ui.protocolProgressBar.maximum())
        self.ui.stimDetails.setRepNum(irep)
        self.ui.protocolProgressBar.setValue(self.ui.protocolProgressBar.value() + 1)

    def reportOverV(self, overdb):
        if overdb > 0:
            pal = RED
        else:
            pal = BLACK
        if self.activeOperation == 'calibration':
            self.ui.overAttenLbl_2.setNum(overdb)
            self.ui.overAttenLbl_2.setPalette(pal)
        elif self.activeOperation == 'explore':
            self.ui.overAttenLbl.setNum(overdb)
            self.ui.overAttenLbl.setPalette(pal)

    def traceDone(self, totalSpikes, avgCount, avgLatency, avgRate):
        self.ui.spikeTotalLbl.setText(str(totalSpikes))
        self.ui.spikeAvgLbl.setText(str(avgCount))
        self.ui.spikeLatencyLbl.setText(str(avgLatency*1000))
        self.ui.spikeRateLbl.setText(str(avgRate))

    def displayOldData(self, path, tracenum, repnum=0):
        if self.activeOperation is None:
            # requires use of AcquisitionData API
            path = str(path)
            if '/' in path:
                group_path = os.path.dirname(path)
            else:
                group_path = path

            group_info = dict(self.acqmodel.datafile.get_info(group_path))
            aifs = group_info['samplerate_ad']

            if repnum == -1:
                showall = True
                response = self.acqmodel.datafile.get_data(path, (tracenum,))
                repnum = response.shape[0] -1
                if len(response.shape) == 2:
                    # backwards compatibility: reshape old data to have channel dimension
                    response = response.reshape((response.shape[0], 1, response.shape[1]))
            else:
                showall = False
                response = self.acqmodel.datafile.get_data(path, (tracenum, repnum))
                if len(response.shape) == 1:
                    # backwards compatibility: reshape old data to have channel dimension
                    response = response.reshape((1, response.shape[0]))
            npoints = response.shape[-1]            
            nchans = response.shape[-2]

            winsz = float(npoints)/aifs
            times = np.linspace(0, winsz, npoints)

            # plot response signal
            self.ui.plotDock.switchDisplay('standard')
            self.display.setXlimits((0,winsz))

            if len(self._aichans) != nchans:
                cnames = get_ai_chans(self.advanced_options['device_name'])
                self.setNewChannels(cnames[:nchans])

            for chan, name in enumerate(self._aichans):
                if len(response.shape) == 3:
                    # overlay plot
                    self.display.updateSpiketrace(times, response[:,chan,:], name)
                else:
                    self.display.updateSpiketrace(times, response[chan,:], name)

            stimuli = self.acqmodel.datafile.get_trace_stim(path)

            stimulus = stimuli[tracenum]

            # show the stimulus details
            self.reportProgress(-1, tracenum, stimulus)
            self.reportRep(repnum)

            # need to also recreate the stim
            if repnum == 0:
                # assume user must first access the first presentation
                # before being able to browse through reps

                # recreate stim signal
                stim_signal = StimulusModel.signalFromDoc(stimulus, self.calvals['calv'], self.calvals['caldb'])
                fs = stimulus['samplerate_da']
                timevals = np.arange(len(stim_signal)).astype(float)/fs
                freq, spectrum = calc_spectrum(stim_signal, fs)
                spectrum = calc_db(spectrum, self.calvals['calv']) + self.calvals['caldb']
                self.display.updateSignal(timevals, stim_signal)
                self.display.updateFft(freq, spectrum)
                self.display.updateSpec(stim_signal, fs)

            self.ui.psth.clearData()
            self.display.clearRaster()

            # recreate PSTH for current threshold and current rep
            tracedata = self.acqmodel.datafile.get_data(path, (tracenum,))
            if len(tracedata.shape) == 2:
                # backwards compatibility: reshape old data to have channel dimension
                tracedata = tracedata.reshape((tracedata.shape[0], 1, tracedata.shape[1]))

            self.display.setNreps(tracedata.shape[0])

            binsz = float(self.ui.binszSpnbx.value())
            winsz = float(tracedata.shape[-1])/aifs
            # set the max of the PSTH subwindow to the size of this data
            self.ui.psthStopField.setMaximum(winsz)
            self.ui.psthStartField.setMaximum(winsz)

            nbins = np.ceil(winsz/binsz)
            bin_centers = (np.arange(nbins)*binsz)+(binsz/2)
            self.ui.psth.setBins(bin_centers)

            # because we can scroll forwards or backwards, re-do entire plot every time 
            spike_counts = []
            spike_latencies = []
            spike_rates = []
            for irep in range(repnum+1):
                count, latency, rate, response_bins = self.do_spike_stats(tracedata[irep], aifs)
                spike_counts.extend(count)
                spike_latencies.extend(latency)
                spike_rates.extend(rate)
                for chan, name in enumerate(self._aichans):
                    # build raster for current rep in trace
                    bin_times = (np.array(response_bins[chan])*binsz)+(binsz/2)
                    self.display.addRasterPoints(bin_times, irep, name)
                    self.ui.psth.appendData(response_bins[chan])

            total_spikes = sum(spike_counts)
            avg_count = np.mean(spike_counts)
            avg_latency = sum(spike_latencies)/len(spike_latencies)
            avg_rate = sum(spike_rates)/len(spike_rates)

            # update UI
            self.traceDone(total_spikes, avg_count, avg_latency, avg_rate)

    def displayOldProgressPlot(self, path):
        if self.activeOperation is None:
            path = str(path)
            if '/' in path:
                group_path = os.path.dirname(path)
            else:
                group_path = path
            testdata = self.acqmodel.datafile.get_data(path)
            test_info = dict(self.acqmodel.datafile.get_info(path))
            comp_info = self.acqmodel.datafile.get_trace_stim(path)
            group_info = dict(self.acqmodel.datafile.get_info(group_path))
            aifs = group_info['samplerate_ad']
            if test_info['testtype'] == 'Tuning Curve':
                # we need to harvest the intensities out of the component doc
                intensities = []
                frequencies = []
                for comp in comp_info[1:]:
                    # only a single tone present in stims... or a delay component before it
                    intensities.append(comp['components'][-1]['intensity'])
                    frequencies.append(comp['components'][-1]['frequency'])
                intensities = list(set(intensities))
                frequencies = list(set(frequencies))
                intensities.sort() #got out of order?
                frequencies.sort()
                xlabels = frequencies
                groups = intensities
                plottype = 'tuning'
            else:
                xlabels = range(testdata.shape[0])
                groups = ['all traces']
                plottype = 'other'

            if len(testdata.shape) == 3:
                # backwards compatibility: reshape old data to have channel dimension
                testdata = testdata.reshape((testdata.shape[0], testdata.shape[1], 1, testdata.shape[-1]))
            nchans = testdata.shape[-2]

            if len(self._aichans) != nchans:
                cnames = get_ai_chans(self.advanced_options['device_name'])
                self.setNewChannels(cnames[:nchans])

            thresholds = [self._aichan_details[chan]['threshold'] for chan in self._aichans]
            useabs = [self._aichan_details[chan]['abs'] for chan in self._aichans]
            # a not-so-live curve
            self.comatosecurve = ProgressWidget.loadCurve(testdata, groups, thresholds, useabs, aifs, xlabels)
            self.comatosecurve.setLabels(plottype)
            self.ui.progressDock.setWidget(self.comatosecurve)

    def launchSaveDlg(self):
        dlg = SavingDialog(defaultFile = self.acqmodel.current_data_file())
        if dlg.exec_():
            fname, fmode = dlg.getfile()
            # loading a file may take a while... background to seprate thread,
            # and display a window asking the user to wait
            self.lf = LoadFrame(x=self.x() + (self.width()/2), y=self.y() + (self.height()/2))
            QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            QtGui.QApplication.processEvents()
            load_thread = threading.Thread(target=self.loadDataFile,
                                           args=(fname, fmode))
            load_thread.start()
        else:
            # return value only used for testing
            load_thread = None
        dlg.deleteLater()
        return load_thread

    def loadDataFile(self, fname, fmode):
        # meant to be run in thread only by save dialog call

        # this is really dumb, but processEvents doesn't cut it for getting
        # the patience ("Loading") window to appear, so we sleep for a bit
        time.sleep(0.1)
        self.acqmodel.load_data_file(fname, fmode)
        self.fileLoaded.emit(fname)

    def updateDataFileStuffs(self, fname):
        # this is meant to be called only my fileLoaded signal!!!
        # calibration clears on data file load
        self.ui.currentCalLbl.setText('None')
        fname = os.path.basename(str(fname))
        self.ui.dataFileLbl.setText(fname)
        self.ui.reviewer.setDataObject(self.acqmodel.datafile)
        self.ui.cellIDLbl.setText(str(self.acqmodel.current_cellid))
        self.lf.close()
        self.lf.deleteLater()
        self.lf = None
        QtGui.QApplication.restoreOverrideCursor()

    def launchCalibrationDlg(self):
        dlg = CalibrationDialog(defaultVals = self.calvals, fscale=self.fscale, datafile=self.acqmodel.datafile)
        if dlg.exec_():
            results = dlg.values()
            self.acqmodel.set(**results)
            if results['use_calfile']:
                ww = self.showWait()
                self.acqmodel.set_calibration(results['calname'], self.calvals['calf'], results['frange'])
                self.ui.currentCalLbl.setText(results['calname'])
                ww.close()
            else:
                self.ui.currentCalLbl.setText('None')
                self.acqmodel.set_calibration(None)
            for key, val in results.items():
                self.calvals[key] = val
        dlg.deleteLater()
        
    def launchScaleDlg(self):
        field_vals = {u'fscale' : self.fscale, u'tscale' : self.tscale}
        dlg = ScaleDialog(defaultVals=field_vals)
        if dlg.exec_():
            fscale, tscale = dlg.values()
            self.updateUnitLabels(tscale, fscale)
        dlg.deleteLater()

    def launchSpecgramDlg(self):
        dlg = SpecDialog(defaultVals=self.specArgs)
        if dlg.exec_():
            argdict = dlg.values()
            SpecWidget.setSpecArgs(**self.specArgs)
            QtGui.QApplication.processEvents()
            self.specArgs = argdict
        dlg.deleteLater()

    def launchViewDlg(self):
        dlg = ViewSettingsDialog(self.viewSettings)
        if dlg.exec_():
            self.viewSettings = dlg.values()
            self.ui.stimDetails.setDisplayAttributes(self.viewSettings['display_attributes'])
            font = QtGui.QFont()
            font.setPointSize(self.viewSettings['fontsz'])
            QtGui.QApplication.setFont(font)
        dlg.deleteLater()

    def launchCellDlg(self):
        cid = QtGui.QInputDialog.getInt(self, "Cell ID", "Enter the ID number of the current cell:", self.acqmodel.current_cellid)
        self.acqmodel.current_cellid = cid[0]

    def launchChannelDlg(self):
        dlg = ChannelDialog(self.advanced_options['device_name'])
        dlg.setSelectedChannels(self._aichans)
        if dlg.exec_():
            cnames = dlg.getSelectedChannels()
            self.ui.chanNumLbl.setText(str(len(cnames)))
            self.setNewChannels(cnames)
        dlg.deleteLater()

    def setNewChannels(self, cnames):
        self._aichans = cnames
        # remove channels no longer present
        self._aichan_details = {chan: deets for chan, deets in self._aichan_details.items() if chan in cnames}
        for name in cnames:
            # add new channels
            self._aichan_details[name] = self._aichan_details.get(name, {'threshold': 5, 'polarity': 1, 'raster_bounds':(0.5,0.9), 'abs': True})

        # remove all plots and re-add from new list
        self.display.removeResponsePlot(*self.display.responseNameList())
        self.display.addResponsePlot(*self._aichans)
        # update details on plots
        for name, deets in self._aichan_details.items():
            self.display.setThreshold(deets['threshold'], name)
            self.display.setRasterBounds(deets['raster_bounds'], name)
            self.display.setAbs(deets['abs'], name)
        
    def launchVocalPaths(self):
        dlg = VocalPathDialog(Vocalization.paths)
        if dlg.exec_():
            Vocalization.paths = dlg.paths()
        dlg.deleteLater()

    def launchAdvancedDlg(self):
        dlg = AdvancedOptionsDialog(self.advanced_options)
        if dlg.exec_():
            self.advanced_options = dlg.getValues()
            StimulusModel.setMaxVoltage(self.advanced_options['max_voltage'], self.advanced_options['device_max_voltage'])
            self.display.setAmpConversionFactor(self.advanced_options['volt_amp_conversion'])
            if self.advanced_options['use_attenuator']:
                # could check for return value here? It will try
                # to re-connect every time start is pressed anyway
                self.acqmodel.attenuator_connection(True)
            else:
                self.acqmodel.attenuator_connection(False)
            self.reset_device_channels()
        dlg.deleteLater()

    def recordingSelected(self, modelIndex):
        """ On double click of wav file, load into display """
        # display spectrogram of file
        spath = self.exvocal.currentWavFile

        fs, audio_signal = audioread(spath)
        self.displayStim(audio_signal, fs)

        if self.ui.tabGroup.currentWidget().objectName() == 'tabExplore':
            winsz = float(self.ui.windowszSpnbx.value())

            self.display.setXlimits((0,winsz))
        self.selectedWavFile = spath
        self.onUpdate()

    def relayCMapChange(self, cmap):
        # self.exvocal.update_colormap()
        self.specArgs['colormap'] = cmap

    def setCalibrationDuration(self, foo=None):
        winsz = float(self.ui.windowszSpnbx.value())
        self.ui.calibrationWidget.setDuration(winsz)

    def updateThresh(self, thresh, chan_name):
        self._aichan_details[str(chan_name)]['threshold'] = thresh
        self.reloadReview()

    def setPolarity(self, pol, chan_name):
        self._aichan_details[str(chan_name)]['polarity'] = pol
        self.reloadReview()

    def updateRasterBounds(self, lims, chan_name):
        self._aichan_details[str(chan_name)]['raster_bounds'] = lims

    def updateAbsThreshold(self, absval, chan_name):
        self._aichan_details[str(chan_name)]['abs'] = absval

    def reloadReview(self):
        # reload data, if user is currently reviewing stuffz
        if self.activeOperation is None:
            path, trace_num, rep_num = self.ui.reviewer.currentDataPath()
            if trace_num is not None:
                self.displayOldData(path, trace_num, rep_num)
                self.displayOldProgressPlot(path)

    def tabChanged(self, tabIndex):
        if str(self.ui.tabGroup.tabText(tabIndex)).lower() == 'calibration':
            self.stashedAisr = self.ui.aifsSpnbx.value()
            self.ui.aifsSpnbx.setValue(self.acqmodel.calibration_genrate())
            self.ui.aifsSpnbx.setEnabled(False)
            self.setCalibrationDuration()
            self.ui.startBtn.setText('Calibrate Speaker')
        elif self.prevTab == 'calibration':
            self.ui.aifsSpnbx.setEnabled(True)
            self.ui.aifsSpnbx.setValue(self.stashedAisr)
            self.ui.startBtn.setText('Start')
        
        if str(self.ui.tabGroup.tabText(tabIndex)).lower() == 'review' and self.activeOperation != 'explore':
            self.ui.startBtn.setEnabled(False)
        elif self.activeOperation is None or str(self.ui.tabGroup.tabText(tabIndex)).lower() == 'explore':
            self.ui.startBtn.setEnabled(True)

        self.prevTab = str(self.ui.tabGroup.tabText(tabIndex)).lower()

    def modeToggled(self, mode):
        self.currentMode = str(mode).lower()
        if self.currentMode == "windowed":
            self.ui.startChartBtn.hide()
            self.ui.stopChartBtn.hide()
        elif self.currentMode == "chart":
            self.ui.stopChartBtn.show()
            self.ui.startChartBtn.show()
        else:
            raise Exception('unknown acquisition mode '+mode)

    def updateMicrophoneCalibration(self, x):
        mphonesens = self.ui.mphoneSensSpnbx.value()
        mphonedb = self.ui.mphoneDBSpnbx.value()
        self.acqmodel.set_mphone_calibration(mphonesens, mphonedb)

    def saveExploreToggled(self, save):
        self.saveExplore = save

    def clearProtocol(self):
        self.ui.protocolView.model().clearTests()

    def updateCalDb(self, val):
        self.calvals['caldb'] = self.ui.refDbSpnbx.value()
        self.acqmodel.set(caldb=self.calvals['caldb'])

    def setStatusMsg(self, status):
        self.statusBar().showMessage(status)

    def setTriggerEnable(self, text):
        if text == 'Windowed':
            self.ui.trigchanBox.setEnabled(True)
            self.ui.trigCkbx.setEnabled(True)
        else:
            self.ui.trigchanBox.setEnabled(False)
            self.ui.trigCkbx.setEnabled(False)

    def showWait(self):
        screenPos = self.geometry()
        ww = WaitWidget()
        ww.show()
        waitPos = QtCore.QRect(screenPos.x() + screenPos.width()/2 - ww.width()/2,
            screenPos.y() + screenPos.height()/2 - ww.height()/2, 
            ww.width(), ww.height())
        ww.setGeometry(waitPos)
        QtGui.QApplication.processEvents()
        return ww

    def closeEvent(self,event):
        # stop any tasks that may be running
        lf = LoadFrame("Saving Stuff and Things", x=self.x() + (self.width()/2), y=self.y() + (self.height()/2))
        QtGui.QApplication.processEvents()
        self.onStop()
        self.acqmodel.close_data()
        super(MainWindow, self).closeEvent(event)
        lf.close()
        lf.deleteLater()
