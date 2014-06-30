import spikeylab

import sys, os, yaml
import scipy.io.wavfile as wv
import numpy as np
import logging
import time
import getpass

from PyQt4 import QtCore, QtGui

from spikeylab.acq.daq_tasks import get_ao_chans, get_ai_chans

from spikeylab.dialogs import SavingDialog, ScaleDialog, SpecDialog, \
            ViewSettingsDialog, CalibrationDialog, CellCommentDialog
from spikeylab.main.acquisition_manager import AcquisitionManager
from spikeylab.tools.audiotools import calc_spectrum
from spikeylab.plotting.pyqtgraph_widgets import ProgressWidget
from spikeylab.plotting.pyqtgraph_widgets import SimplePlotWidget
from spikeylab.main.wait_widget import WaitWidget
from spikeylab.tools.systools import get_src_directory

from controlwindow import ControlWindow

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
MPHONE_SENSITIVITY = config['microphone_sensitivity']
DEVNAME = config['device_name']
REFFREQ = config['reference_frequency']
REFVOLTAGE = config['reference_voltage']

class MainWindow(ControlWindow):
    """Main GUI for the application"""
    def __init__(self, inputsFilename='', datafile=None, filemode='w-'):
        # set up model and stimlui first, 
        # as saved configuration relies on this
        self.acqmodel = AcquisitionManager()
        if datafile is not None:
            if filemode == 'w-':
                self.acqmodel.create_data_file(datafile)
            else:
                self.acqmodel.load_data_file(datafile)
            fname = os.path.basename(self.acqmodel.current_data_file())
        else:
            fname = None
            
        # get stimuli editor widgets
        self.exploreStimuli = self.acqmodel.stimuli_list()
        
        # auto generated code intialization
        ControlWindow.__init__(self, inputsFilename)
        
        self.ui.startBtn.clicked.connect(self.onStart)
        self.ui.stopBtn.clicked.connect(self.onStop)
        self.ui.startChartBtn.clicked.connect(self.onStartChart)
        self.ui.stopChartBtn.clicked.connect(self.onStopChart)

        cnames = get_ao_chans(DEVNAME.encode())
        self.ui.aochanBox.addItems(cnames)
        cnames = get_ai_chans(DEVNAME.encode())
        self.ui.aichanBox.addItems(cnames)

        self.ui.runningLabel.setStyleSheet(REDSS)

        self.applyCalibration = False
        self.calpeak = None

        self.liveLock = QtCore.QMutex()

        self.display.thresholdUpdated.connect(self.updateThresh)
        self.display.colormapChanged.connect(self.relayCMapChange)

        self.ui.protocolView.setModel(self.acqmodel.protocol_model())
        self.ui.calibrationWidget.setCurveModel(self.acqmodel.calibration_stimulus('tone'))

        self.acqmodel.signals.response_collected.connect(self.displayResponse)
        self.acqmodel.signals.calibration_response_collected.connect(self.displayCalibrationResponse)
        self.acqmodel.signals.average_response.connect(self.displayDbResult)
        self.acqmodel.signals.spikes_found.connect(self.displayRaster)
        self.acqmodel.signals.trace_finished.connect(self.traceDone)
        self.acqmodel.signals.stim_generated.connect(self.displayStim)
        self.acqmodel.signals.warning.connect(self.setStatusMsg)
        self.acqmodel.signals.ncollected.connect(self.updateChart)
        self.acqmodel.signals.current_trace.connect(self.reportProgress)
        self.acqmodel.signals.current_rep.connect(self.reportRep)
        self.acqmodel.signals.group_finished.connect(self.onGroupDone)
        self.acqmodel.signals.samplerateChanged.connect(self.updateGenerationRate)
        self.acqmodel.signals.tuning_curve_started.connect(self.spawnTuningCurve)
        self.acqmodel.signals.tuning_curve_response.connect(self.displayTuningCurve)
        self.acqmodel.signals.over_voltage.connect(self.reportOverV)

        self.ui.threshSpnbx.valueChanged.connect(self.setPlotThresh)        
        self.ui.windowszSpnbx.valueChanged.connect(self.setCalibrationDuration)
        self.ui.binszSpnbx.setKeyboardTracking(False)
        self.ui.windowszSpnbx.setKeyboardTracking(False)
        self.ui.exNrepsSpnbx.setKeyboardTracking(False)
        self.ui.threshSpnbx.setKeyboardTracking(False)

        self.activeOperation = None

        # update GUI to reflect loaded values
        self.setPlotThresh()
        self.setCalibrationDuration()

        # set up wav file directory finder paths
        self.exvocal = self.ui.parameterStack.widgetForName("Vocalization")
        self.exvocal.filelistView.doubleClicked.connect(self.wavfileSelected)
        self.selectedWavFile = self.exvocal.currentWavFile

        # always start in windowed mode
        self.modeToggled('Windowed')
        self.prevTab = self.ui.tabGroup.tabText(self.ui.tabGroup.currentIndex()).lower()
        # always show plots on load
        self.ui.plotDock.setVisible(True)
        self.ui.psthDock.setVisible(True)

        self.ui.stopBtn.setEnabled(False)
        self.ui.stopChartBtn.setEnabled(False)

        logger = logging.getLogger('main')
        handlers = logger.handlers
        # dig out the UI handler to assign text edit ... a better way?
        for h in handlers:
            if h.get_name() == 'ui':
                # h.signal.message.connect(self.ui.logTxedt.appendPlainText)
                h.signal.message.connect(self.ui.logTxedt.appendHtml)
                break

        logger.info("{} Program Started {}, user: {} {}".format('*'*8, time.strftime("%d-%m-%Y"), getpass.getuser(), '*'*8))
        self.ui.dataFileLbl.setText(fname)

        self.calvals['calf'] = REFFREQ
        self.calvals['calv'] = REFVOLTAGE
        if self.fscale == 1000:
            scale_lbl = 'kHz'
        elif self.fscale == 1:
            scale_lbl = 'Hz'
        self.ui.refToneLbl.setText("Intensity of {}{} Tone at {}V".format(REFFREQ, scale_lbl, REFVOLTAGE))
        self.acqmodel.set_cal_tone(REFFREQ, REFVOLTAGE, self.calvals['caldb'])
        self.calpeak = None
        self.ui.tabGroup.setCurrentIndex(0)

    # def update_ui_log(self, message):
    #     self.ui.logTxedt.appendPlainText(message)

    def connectUpdatable(self, connect):
        if connect:
            self.ui.startBtn.clicked.disconnect()
            self.ui.startBtn.clicked.connect(self.onUpdate)
            self.ui.binszSpnbx.valueChanged.connect(self.onUpdate)
            self.ui.windowszSpnbx.valueChanged.connect(self.onUpdate)
            self.ui.exNrepsSpnbx.valueChanged.connect(self.onUpdate)
            for editor in self.ui.parameterStack.widgets():
                editor.valueChanged.connect(self.onUpdate)
        else:
            try:
                self.ui.exNrepsSpnbx.valueChanged.disconnect()
                self.ui.binszSpnbx.valueChanged.disconnect()
                self.ui.windowszSpnbx.valueChanged.disconnect()
                # this should always remain connected 
                self.ui.windowszSpnbx.valueChanged.connect(self.setCalibrationDuration)
                self.ui.startBtn.clicked.disconnect()
                self.ui.startBtn.clicked.connect(self.onStart)
                for editor in self.ui.parameterStack.widgets():
                    editor.valueChanged.disconnect()
            except TypeError:
                # disconnecting already disconnected signals throws TypeError
                pass

    def playCalTone(self):
        self.onStart(calTone=True)

    def onStart(self, calTone=False):
        # set plot axis to appropriate limits
        # first time set up data file
        if not self.verifyInputs('windowed'):
            return

        # disable the components we don't want changed amid generation
        self.ui.aochanBox.setEnabled(False)
        self.ui.aisrSpnbx.setEnabled(False)
        reprate = self.ui.reprateSpnbx.setEnabled(False)
        self.ui.stopBtn.setEnabled(True)
        self.plotProgress = False
        self.ui.protocolProgressBar.setValue(0)

        if self.currentMode == 'windowed':
            if self.acqmodel.datafile is None:
                self.acqmodel.set_save_params(self.savefolder, self.savename)
                self.acqmodel.create_data_file()
            self.ui.aichanBox.setEnabled(False)
            # FIX ME:
            if self.ui.plotDock.current() == 'calibration':
                self.ui.plotDock.switchDisplay('standard')
            self.ui.runningLabel.setText(u"RECORDING")
            self.ui.runningLabel.setStyleSheet(GREENSS)

        if calTone:
            self.runCalTone()
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

        if self.acqmodel.datafile is None:
            self.acqmodel.set_save_params(self.savefolder, self.savename)
            self.acqmodel.create_data_file()

        self.runChart()
        self.ui.runningLabel.setText(u"RECORDING")
        self.ui.runningLabel.setStyleSheet(GREENSS)
        self.ui.startChartBtn.setEnabled(False)
        self.ui.aichanBox.setEnabled(False)
        self.ui.aisrSpnbx.setEnabled(False)
        self.ui.stopChartBtn.setEnabled(True)
        self.ui.windowszSpnbx.valueChanged.connect(self.updateScollingWindowsize)

    def onUpdate(self):
        if not self.verifyInputs(self.activeOperation):
            return
        aochan = self.ui.aochanBox.currentText()
        aichan = self.ui.aichanBox.currentText()
        acq_rate = self.ui.aisrSpnbx.value()*self.fscale

        winsz = float(self.ui.windowszSpnbx.value())*self.tscale
        binsz = float(self.ui.binszSpnbx.value())*self.tscale

        nbins = np.ceil(winsz/binsz)
        bin_centers = (np.arange(nbins)*binsz)+(binsz/2)
        self.ui.psth.setBins(bin_centers)
        self.acqmodel.set_params(aochan=aochan, aichan=aichan,
                                 acqtime=winsz, aisr=acq_rate,
                                 binsz=binsz)
        self.binsz = binsz

        self.display.setXlimits((0,winsz))

        if self.ui.tabGroup.currentWidget().objectName() == 'tabExplore':
            nreps = self.ui.exNrepsSpnbx.value()

            self.acqmodel.set_params(nreps=nreps)
            
            # have model sort all signals stuff out?
            stim_index = self.ui.exploreStimTypeCmbbx.currentIndex()
            self.acqmodel.set_stim_by_index(stim_index)

            self.display.setNreps(nreps)
        if self.currentMode == 'chart':
            return winsz, acq_rate
            
    def onStop(self):
        self.acqmodel.halt() # stops generation, and acquistion if linked
        if self.currentMode == 'windowed':
            self.activeOperation = None
            self.liveLock.unlock()
            self.ui.runningLabel.setText(u"OFF")
            self.ui.runningLabel.setStyleSheet(REDSS)
            self.ui.aichanBox.setEnabled(True)
            self.connectUpdatable(False)
        self.ui.startBtn.setEnabled(True)
        self.ui.stopBtn.setText("Stop")
        self.ui.startBtn.setText('Start')
        self.ui.stopBtn.clicked.disconnect()
        self.ui.stopBtn.clicked.connect(self.onStop)

        if self.ui.tabGroup.tabText(self.ui.tabGroup.currentIndex()).lower() != 'calibration':
            self.ui.aisrSpnbx.setEnabled(True)
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
        self.ui.aichanBox.setEnabled(True)
        self.ui.aisrSpnbx.setEnabled(True)
        self.ui.stopChartBtn.setEnabled(False)
        self.ui.windowszSpnbx.valueChanged.disconnect()
        self.ui.windowszSpnbx.valueChanged.connect(self.setCalibrationDuration)

    def onGroupDone(self, halted):
        if self.activeOperation == 'calibration':
            #maybe don't call this at all if save is false?
            save = self.ui.calibrationWidget.saveChecked() and not halted
            calname = self.acqmodel.process_calibration(save)
            if save:
                ww = self.showWait()
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
        elif self.activeOperation == 'protocol' and self.currentMode == 'windowed':
            if self.acqmodel.current_cellid == 0:
                # first acquisition, don't ask if it's a new cell
                self.acqmodel.increment_cellid()
            else:
                answer = QtGui.QMessageBox.question(self, 'Cell ID', 'New cell?',
                                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                if answer == QtGui.QMessageBox.Yes:
                    self.acqmodel.increment_cellid()

            cellbox = CellCommentDialog(cellid=self.acqmodel.current_cellid)
            if cellbox.exec_():
                comment = cellbox.comment()
                self.acqmodel.set_group_comment(comment)
            else:
                # save empty comment
                self.acqmodel.set_group_comment('')

        self.onStop()

    def runChart(self):
        winsz, acq_rate = self.onUpdate()
        # change plot to scrolling plot
        self.scrollplot.setWindowSize(winsz)
        self.scrollplot.setSr(acq_rate)
        self.ui.plotDock.switchDisplay('chart')

        # self.activeOperation = 'chart'
        self.acqmodel.start_chart()

    def updateScollingWindowsize(self):
        winsz = float(self.ui.windowszSpnbx.value())*self.tscale
        self.scrollplot.setWindowSize(winsz)

    def updateChart(self, stimData, responseData):
        self.scrollplot.appendData(stimData, responseData)

    def updateGenerationRate(self, fs):
        self.ui.aosrSpnbx.setValue(fs/self.fscale)

    def runExplore(self):
        self.ui.startBtn.setText('Update')
        
        self.connectUpdatable(True)

        self.activeOperation = 'explore'
        reprate = self.ui.reprateSpnbx.value()
        interval = (1/reprate)*1000

        self.onUpdate()            
        self.acqmodel.run_explore(interval)

    def runCalTone(self):
        self.ui.calToneBtn.setText('Stop')
        self.ui.calToneBtn.clicked.disconnect()
        self.ui.calToneBtn.clicked.connect(self.stopCalTone)
        self.ui.startBtn.setEnabled(False)
        self.ui.stopBtn.setEnabled(False)

        self.activeOperation = 'caltone'
        reprate = self.ui.reprateSpnbx.value()
        interval = (1/reprate)*1000

        self.onUpdate()           
        nreps = self.ui.exNrepsSpnbx.value()
        self.acqmodel.set_params(nreps=nreps)
        self.display.setNreps(nreps)

        self.acqmodel.run_caltone(interval)

    def runProtocol(self):
        self.display.updateSpec(None)

        self.ui.startBtn.setEnabled(False)
        self.ui.stopBtn.setText("Abort")
        self.activeOperation = 'protocol'

        reprate = self.ui.reprateSpnbx.value()
        interval = (1/reprate)*1000
        
        self.onUpdate()
        if self.currentMode == 'windowed':
            overload = self.acqmodel.setup_protocol(interval)
            overload = [item for sublist in overload for item in sublist] # flatten
            if np.any(np.array(overload) > 0):
                answer = QtGui.QMessageBox.question(self, 'Oh Dear!', 
                                'Stimuli in test list are over the maximum allowable voltage output. They will be rescaled with a maximum undesired attenuation of {:.2f}dB.\n \
                                Do you want to continue?'.format(np.amax(overload)),
                                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                if answer == QtGui.QMessageBox.No:
                    self.onStop()
                    return

            # reset style sheet of progress bar
            self.ui.protocolProgressBar.setStyleSheet("QProgressBar { text-align: center; }")
            self.ui.protocolProgressBar.setMaximum(self.acqmodel.protocol_total_count())

            self.acqmodel.run_protocol()
        else:
            self.acqmodel.run_chart_protocol(interval)

    def runCalibration(self):
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
        else:
            # Always use noise on saving calibration.
            # BEWARE: Hardcoded to index 1... this could change?!
            self.acqmodel.set_calibration_by_index(1)

        if self.ui.calibrationWidget.ui.applycalCkbx.isChecked() and self.ui.calibrationWidget.isToneCal():
            frequencies, intensities = self.acqmodel.calibration_range()
            self.livecurve = ProgressWidget(list(frequencies), list(intensities))
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
        self.ui.protocolProgressBar.setMaximum(self.acqmodel.calibration_total_count())

        self.acqmodel.run_calibration(interval, self.ui.calibrationWidget.ui.applycalCkbx.isChecked())

    def displayResponse(self, times, response):
        # print 'response signal', len(response)
        if len(times) != len(response):
            print "WARNING: times and response not equal"
        if self.ui.plotDock.current() == 'standard':
            self.display.updateSpiketrace(times, response)
        elif self.ui.plotDock.current() == 'calexp':
            # convert voltage amplitudes into dB SPL    
            rms = np.sqrt(np.mean(pow(response,2))) / np.sqrt(2)
            masterdb = 94 + (20.*np.log10(rms/(MPHONE_SENSITIVITY)))
            sr = self.ui.aisrSpnbx.value()*self.fscale
            freq, signal_fft = calc_spectrum(response, sr)
            spectrum = 94 + (20.*np.log10((signal_fft/np.sqrt(2))/MPHONE_SENSITIVITY))
            spectrum[0] = 0
            peakspl = np.amax(spectrum)
            self.ui.dblevelLbl.setNum(masterdb)
            self.ui.dblevelLbl2.setNum(peakspl)
            self.extendedDisplay.updateSignal(times, response, plot='response')
            self.extendedDisplay.updateFft(freq, spectrum, plot='response')
            self.extendedDisplay.updateSpec(response, sr, plot='response')

    def displayCalibrationResponse(self, spectrum, freqs, rms):

        masterdb = 94 + (20.*np.log10(rms/(MPHONE_SENSITIVITY)))
        spectrum = 94 + (20.*np.log10((spectrum/np.sqrt(2))/MPHONE_SENSITIVITY))
        spectrum[0] = 0
        peakspl = np.amax(spectrum)
        self.ui.dblevelLbl.setNum(masterdb)
        self.ui.dblevelLbl2.setNum(peakspl)

        self.calibrationDisplay.updateInFft(freqs, spectrum)


    def displayDbResult(self, f, db, resultdb):
        try:
            self.livecurve.setPoint(f,db,resultdb)
        except:
            print u"WARNING : Problem drawing to calibration plot"
            raise

    def spawnTuningCurve(self, frequencies, intensities, plotType):
        self.livecurve = ProgressWidget(frequencies, intensities)
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
        freq, spectrum = calc_spectrum(signal, fs)
        # spectrum = spectrum / np.sqrt(2)
        spectrum = 20 * np.log10(spectrum/ self.calvals['calv']) + self.calvals['caldb']

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

    def launchSaveDlg(self):
        dlg = SavingDialog(defaultFile = self.acqmodel.current_data_file())
        if dlg.exec_():
            fname, fmode = dlg.getfile()
            if fmode == 'w-':
                self.acqmodel.create_data_file(fname)
            else:
                self.acqmodel.load_data_file(fname)
            # calibration clears on data file load
            self.ui.currentCalLbl.setText('None')
            fname = os.path.basename(fname)
            self.ui.dataFileLbl.setText(fname)
        dlg.deleteLater()

    def launchCalibrationDlg(self):
        dlg = CalibrationDialog(defaultVals = self.calvals, fscale=self.fscale, datafile=self.acqmodel.datafile)
        if dlg.exec_():
            results = dlg.values()
            self.acqmodel.set_params(**results)
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
            self.display.setSpecArgs(**argdict)
            self.exvocal.setSpecArgs(**argdict)
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

    def wavfileSelected(self, modelIndex):
        """ On double click of wav file, load into display """
        # display spectrogram of file
        spath = self.exvocal.currentWavFile

        sr, wavdata = wv.read(spath)
        self.displayStim(wavdata, sr)

        if self.ui.tabGroup.currentWidget().objectName() == 'tabExplore':
            winsz = float(self.ui.windowszSpnbx.value())*self.tscale

            self.display.setXlimits((0,winsz))
        self.selectedWavFile = spath
        self.onUpdate()

    def relayCMapChange(self, cmap):
        self.exvocal.update_colormap()
        self.specArgs['colormap'] = cmap

    def setCalibrationDuration(self):
        winsz = float(self.ui.windowszSpnbx.value())
        print 'setting calibration duration', winsz
        # I shouldn't have to do both of these...
        self.acqmodel.set_calibration_duration(winsz*self.tscale)
        self.ui.calibrationWidget.setDuration(winsz)

    def updateThresh(self, thresh):
        self.ui.threshSpnbx.setValue(thresh)
        self.acqmodel.set_threshold(thresh)

    def setPlotThresh(self):
        thresh = self.ui.threshSpnbx.value()
        self.display.spiketracePlot.setThreshold(thresh)
        self.acqmodel.set_threshold(thresh)

    def tabChanged(self, tabIndex):
        if self.ui.tabGroup.tabText(tabIndex).lower() == 'calibration':
            self.stashedAisr = self.ui.aisrSpnbx.value()
            self.ui.aisrSpnbx.setValue(self.acqmodel.calibration_genrate()/self.fscale)
            self.ui.aisrSpnbx.setEnabled(False)
        elif self.prevTab == 'calibration':
            self.ui.aisrSpnbx.setEnabled(True)
            self.ui.aisrSpnbx.setValue(self.stashedAisr)
        self.prevTab = self.ui.tabGroup.tabText(tabIndex).lower()

    def modeToggled(self, mode):
        self.currentMode = mode.lower()
        if self.currentMode == "windowed":
            self.ui.startChartBtn.hide()
            self.ui.stopChartBtn.hide()
        elif self.currentMode == "chart":
            self.ui.stopChartBtn.show()
            self.ui.startChartBtn.show()
        else:
            raise Exception('unknown acquistion mode '+mode)

    def saveExploreToggled(self, save):
        self.saveExplore = save

    def clearProtocol(self):
        self.acqmodel.clear_protocol()

    def updateCalDb(self):
        self.calvals['caldb'] = self.ui.refDbSpnbx.value()

    def setStatusMsg(self, status):
        self.statusBar().showMessage(status)

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
        self.onStop()
        self.acqmodel.close_data()
        super(MainWindow, self).closeEvent(event)


def log_uncaught(*exc_info):
    logger = logging.getLogger('main')
    logger.error("Uncaught exception: ", exc_info=exc_info)

if __name__ == "__main__":
    # this is the entry point for the whole application
    app = QtGui.QApplication(sys.argv)
    sys.excepthook = log_uncaught
    dlg = SavingDialog()
    if dlg.exec_():
        fname, fmode = dlg.getfile()
        myapp = MainWindow("controlinputs.json", datafile=fname, filemode=fmode)
        app.setActiveWindow(myapp)
        myapp.show()
        status = app.exec_()
    else:
        status = 0
        print 'canceled'
    dlg.deleteLater()
    sys.exit(status)

