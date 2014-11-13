import os, yaml
import numpy as np
import logging
import time
import getpass

from QtWrapper import QtCore, QtGui

from spikeylab.acq.daq_tasks import get_ao_chans, get_ai_chans

from spikeylab.gui.dialogs import SavingDialog, ScaleDialog, SpecDialog, \
            ViewSettingsDialog, CalibrationDialog, CellCommentDialog
from spikeylab.run.acquisition_manager import AcquisitionManager
from spikeylab.tools.audiotools import calc_spectrum, calc_db, audioread, \
                                       signal_amplitude, calc_summed_db, \
                                       sum_db, rms
from spikeylab.gui.plotting.pyqtgraph_widgets import ProgressWidget
from spikeylab.gui.plotting.pyqtgraph_widgets import SimplePlotWidget
from spikeylab.gui.wait_widget import WaitWidget
from spikeylab.tools.systools import get_src_directory
from spikeylab.tools.qsignals import ProtocolSignals
from spikeylab.tools.uihandler import assign_uihandler_slot
from spikeylab.tools.util import clearLayout
from spikeylab.gui.qprotocol import QProtocolTabelModel
from spikeylab.gui.stim.qstimulus import QStimulusModel
from spikeylab.gui.stim.components.qcomponents import wrapComponent
from spikeylab.stim.stimulus_model import StimulusModel
    
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
DEVNAME = config['device_name']
REFFREQ = config['reference_frequency']
REFVOLTAGE = config['reference_voltage']

class MainWindow(ControlWindow):
    """Main GUI for the application. Run the main fucntion of this file"""
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
            
        # get stimuli components, they must be wrapped to get editor
        self.exploreStimuli = [wrapComponent(x) for x in self.acqmodel.stimuli_list()]
        
        # auto generated code intialization
        ControlWindow.__init__(self, inputsFilename)
        if datafile is not None:
            self.ui.reviewer.setDataObject(self.acqmodel.datafile)
            self.ui.dataFileLbl.setText(fname)

        self.ui.cellIDLbl.setText(str(self.acqmodel.current_cellid))

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

        self.ui.protocolView.setModel(QProtocolTabelModel(self.acqmodel.protocol_model()))
        self.ui.calibrationWidget.setCurveModel(QStimulusModel(self.acqmodel.calibration_stimulus('tone')))

        self.signals = ProtocolSignals()
        self.signals.response_collected.connect(self.displayResponse)
        self.signals.calibration_response_collected.connect(self.displayCalibrationResponse)
        self.signals.average_response.connect(self.displayDbResult)
        self.signals.spikes_found.connect(self.displayRaster)
        self.signals.trace_finished.connect(self.traceDone)
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

        self.ui.threshSpnbx.valueChanged.connect(self.setPlotThresh)        
        self.ui.windowszSpnbx.valueChanged.connect(self.setCalibrationDuration)
        self.ui.exNrepsSpnbx.setKeyboardTracking(False)
        self.ui.threshSpnbx.setKeyboardTracking(False)
        self.ui.delaySpnbx.setKeyboardTracking(False)

        self.activeOperation = None

        # update GUI to reflect loaded values
        self.setPlotThresh()
        self.setCalibrationDuration()

        # set up wav file directory finder paths
        self.exvocal = self.ui.parameterStack.widgetForName("Vocalization")
        self.exvocal.filelistView.doubleClicked.connect(self.recordingSelected)
        self.exvocal.filelistView.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.selectedWavFile = self.exvocal.currentWavFile

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

        logger.info("{} Program Started {}, user: {} {}".format('*'*8, time.strftime("%d-%m-%Y"), getpass.getuser(), '*'*8))

        self.calvals['calf'] = REFFREQ
        self.calvals['calv'] = REFVOLTAGE
        if self.fscale == 1000:
            scale_lbl = 'kHz'
        elif self.fscale == 1:
            scale_lbl = 'Hz'
        self.ui.refToneLbl.setText("Intensity of {}{} Tone at {}V".format(REFFREQ/self.fscale, scale_lbl, REFVOLTAGE))
        self.acqmodel.set(**self.calvals)
        self.acqmodel.set_calibration(None, self.calvals['calf'], self.calvals['frange'])
        self.calpeak = None
        self.ui.tabGroup.setCurrentIndex(0)
        
        #updates the microphone calibration in the acquisition model
        self.updateMicrophoneCalibration(0) # arg is place holder

        # connect data reviewer to data display
        self.ui.reviewer.reviewDataSelected.connect(self.displayOldData)
        self.ui.reviewer.testSelected.connect(self.displayOldProgressPlot)

        self.display.spiketracePlot.invertPolarity.connect(self.toggleResponsePolarity)
    # def update_ui_log(self, message):
    #     self.ui.logTxedt.appendPlainText(message)

    def connectUpdatable(self, connect):
        if connect:
            self.ui.startBtn.clicked.disconnect()
            self.ui.startBtn.clicked.connect(self.onUpdate)
            self.ui.binszSpnbx.valueChanged.connect(self.onUpdate)
            self.ui.windowszSpnbx.valueChanged.disconnect()
            self.ui.windowszSpnbx.valueChanged.connect(self.onUpdate)
            self.ui.exNrepsSpnbx.valueChanged.connect(self.onUpdate)
            self.ui.delaySpnbx.valueChanged.connect(self.onUpdate)
            for editor in self.ui.parameterStack.widgets():
                editor.valueChanged.connect(self.onUpdate)
            self.ui.actionSet_Scale.setEnabled(False)
            self.ui.actionSave_Options.setEnabled(False)
            self.ui.actionSet_Calibration.setEnabled(False)
        else:
            try:
                self.ui.exNrepsSpnbx.valueChanged.disconnect()
                self.ui.binszSpnbx.valueChanged.disconnect()
                self.ui.windowszSpnbx.valueChanged.disconnect()
                self.ui.delaySpnbx.valueChanged.disconnect()
                # this should be connected when search ISN'T running
                self.ui.windowszSpnbx.valueChanged.connect(self.setCalibrationDuration)
                self.ui.startBtn.clicked.disconnect()
                self.ui.startBtn.clicked.connect(self.onStart)
                for editor in self.ui.parameterStack.widgets():
                    editor.valueChanged.disconnect()
                self.ui.actionSet_Scale.setEnabled(True)
                self.ui.actionSave_Options.setEnabled(True)
                self.ui.actionSet_Calibration.setEnabled(True)

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
        self.ui.aisrSpnbx.setEnabled(False)
        reprate = self.ui.reprateSpnbx.setEnabled(False)
        self.ui.stopBtn.setEnabled(True)
        self.plotProgress = False
        self.ui.protocolProgressBar.setValue(0)

        self.acqmodel.set(reprate=self.ui.reprateSpnbx.value())

        if self.currentMode == 'windowed':
            if self.acqmodel.datafile is None:
                self.acqmodel.set_save_params(self.savefolder, self.savename)
                self.acqmodel.create_data_file()
            self.ui.aichanBox.setEnabled(False)
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
        aochan = str(self.ui.aochanBox.currentText())
        aichan = str(self.ui.aichanBox.currentText())
        acq_rate = self.ui.aisrSpnbx.value()*self.fscale

        winsz = float(self.ui.windowszSpnbx.value())*self.tscale
        binsz = float(self.ui.binszSpnbx.value())*self.tscale

        nbins = np.ceil(winsz/binsz)
        bin_centers = (np.arange(nbins)*binsz)+(binsz/2)
        self.ui.psth.setBins(bin_centers)
        self.acqmodel.set(aochan=aochan, aichan=aichan, acqtime=winsz,
                          aisr=acq_rate, binsz=binsz)
        self.binsz = binsz

        self.display.setXlimits((0,winsz))

        if self.ui.tabGroup.currentWidget().objectName() == 'tabExplore':
            nreps = self.ui.exNrepsSpnbx.value()

            self.acqmodel.set(nreps=nreps)
            
            # have model sort all signals stuff out?
            self.acqmodel.set_explore_delay(self.ui.delaySpnbx.value()*self.tscale)
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

        if str(self.ui.tabGroup.tabText(self.ui.tabGroup.currentIndex())).lower() != 'calibration':
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
        winsz = float(self.ui.windowszSpnbx.value())*self.tscale
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
            overload = self.acqmodel.setup_protocol(interval)
            # overload = [item for sublist in overload for item in sublist] # flatten
            # if np.any(np.array(overload) > 0):
            #     answer = QtGui.QMessageBox.question(self, 'Oh Dear!', 
            #                     'Stimuli in test list are over the maximum allowable voltage output. They will be rescaled with a maximum undesired attenuation of {:.2f}dB.\n \
            #                     Do you want to continue?'.format(np.amax(overload)),
            #                     QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            #     if answer == QtGui.QMessageBox.No:
            #         self.onStop()
            #         return

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
        self.acqmodel.set_calibration_duration(winsz*self.tscale)
        
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
            rep_multiplier = 1      
        else:
            # Always use noise on saving calibration.
            # BEWARE: Hardcoded to index 1... this could change?!
            self.acqmodel.set_calibration_by_index(1)
            rep_multiplier = 2     

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
        self.ui.protocolProgressBar.setMaximum(self.acqmodel.calibration_total_count()*rep_multiplier)

        self.acqmodel.run_calibration(interval, self.ui.calibrationWidget.ui.applycalCkbx.isChecked())

    def mphoneCalibrate(self):
        self.onStart(True)

        self.display.updateSpec(None)

        self.ui.startBtn.setEnabled(False)
        self.activeOperation = 'caltone'

        reprate = self.ui.reprateSpnbx.value()
        interval = (1/reprate)*1000
        
        self.onUpdate()

        self.acqmodel.run_mphone_calibration(interval)

    def displayResponse(self, times, response):
        if len(times) != len(response):
            print "WARNING: times and response not equal"
        # print 'response signal', len(response)
        # convert voltage amplitudes into dB SPL    
        sr = self.ui.aisrSpnbx.value()*self.fscale
        # amp = signal_amplitude(response, sr)
        mphonesens = self.ui.mphoneSensSpnbx.value()
        mphonedb = self.ui.mphoneDBSpnbx.value()
        amp_signal = calc_db(np.amax(response), mphonesens, mphonedb)
        amp_signal_rms = calc_db(rms(response, sr), mphonesens, mphonedb)

        freq, signal_fft = calc_spectrum(response, sr)
        idx = np.where((freq > 5000) & (freq < 100000))
        summed_db0 = calc_summed_db(signal_fft[idx], mphonesens, mphonedb)
        spectrum = calc_db(signal_fft, mphonesens, mphonedb)
        spectrum[spectrum < 30] = 0
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
            self.display.updateSpiketrace(times, response)
        elif self.ui.plotDock.current() == 'calexp':
            self.extendedDisplay.updateSignal(times, response, plot='response')
            self.extendedDisplay.updateFft(freq, spectrum, plot='response')
            self.extendedDisplay.updateSpec(response, sr, plot='response')

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
        self.ui.aosrSpnbx.setValue(fs/self.fscale)
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
            # requires initmate knowledge of datafile organization
            path = str(path)
            group_path = os.path.dirname(path)
            response = self.acqmodel.datafile.get(path, (tracenum, repnum))
            npoints = response.shape[0]
            stimuli = self.acqmodel.datafile.get_trace_info(path)

            stimulus = stimuli[tracenum]
            group_info = dict(self.acqmodel.datafile.get_info(group_path))
            aisr = group_info['samplerate_ad']

            # show the stimulus details
            self.reportProgress(-1, tracenum, stimulus)
            self.reportRep(repnum)

            winsz = float(npoints)/aisr
            times = np.linspace(0, winsz, npoints)

            # plot response signal
            self.ui.plotDock.switchDisplay('standard')
            self.display.setXlimits((0,winsz))
            self.display.updateSpiketrace(times, response)
            # need to also recreate the stim
            if repnum == 0:
                # assume user must first access the first presentation
                # before being able to browse through reps
                stim_signal = StimulusModel.signalFromDoc(stimulus, self.calvals['calv'], self.calvals['caldb'])
                fs = stimulus['samplerate_da']
                timevals = np.arange(len(stim_signal)).astype(float)/fs
                freq, spectrum = calc_spectrum(stim_signal, fs)
                spectrum = calc_db(spectrum, self.calvals['calv']) + self.calvals['caldb']
                self.display.updateSignal(timevals, stim_signal)
                self.display.updateFft(freq, spectrum)
                self.display.updateSpec(stim_signal, fs)

    def displayOldProgressPlot(self, path):
        if self.activeOperation is None:
            path = str(path)
            group_path = os.path.dirname(path)
            testdata = self.acqmodel.datafile.get(path)
            test_info = dict(self.acqmodel.datafile.get_info(path))
            comp_info = self.acqmodel.datafile.get_trace_info(path)
            group_info = dict(self.acqmodel.datafile.get_info(group_path))
            aisr = group_info['samplerate_ad']
            if test_info['testtype'] == 'Tuning Curve':
                # we need to harvest the intensities out of the component doc
                intensities = []
                frequencies = []
                for comp in comp_info[1:]:
                    # only a single tone present in stims
                    intensities.append(comp['components'][0]['intensity'])
                    frequencies.append(comp['components'][0]['frequency'])
                intensities = list(set(intensities))
                frequencies = list(set(frequencies))
                intensities.sort() #got out of order?
                frequencies.sort()
                xlabels = frequencies
                groups = intensities
                plottype = 'tuning'
            else:
                xlabels = range(testdata.shape[0]-1)
                groups = ['all traces']
                plottype = 'other'
            # a not-so-live curve
            self.comatosecurve = ProgressWidget.loadCurve(testdata, groups, self.ui.threshSpnbx.value(), aisr, xlabels)
            self.comatosecurve.setLabels(plottype)
            self.ui.progressDock.setWidget(self.comatosecurve)

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
            self.ui.reviewer.setDataObject(self.acqmodel.datafile)
        dlg.deleteLater()

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

    def recordingSelected(self, modelIndex):
        """ On double click of wav file, load into display """
        # display spectrogram of file
        spath = self.exvocal.currentWavFile

        sr, audio_signal = audioread(spath)
        self.displayStim(audio_signal, sr)

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
        self.ui.calibrationWidget.setDuration(winsz)

    def updateThresh(self, thresh):
        self.ui.threshSpnbx.setValue(thresh)
        self.acqmodel.set_threshold(thresh)

    def setPlotThresh(self):
        thresh = self.ui.threshSpnbx.value()
        self.display.spiketracePlot.setThreshold(thresh)
        self.acqmodel.set_threshold(thresh)

    def tabChanged(self, tabIndex):
        if str(self.ui.tabGroup.tabText(tabIndex)).lower() == 'calibration':
            self.stashedAisr = self.ui.aisrSpnbx.value()
            self.ui.aisrSpnbx.setValue(self.acqmodel.calibration_genrate()/self.fscale)
            self.ui.aisrSpnbx.setEnabled(False)
            self.setCalibrationDuration()
        elif self.prevTab == 'calibration':
            self.ui.aisrSpnbx.setEnabled(True)
            self.ui.aisrSpnbx.setValue(self.stashedAisr)
        self.prevTab = str(self.ui.tabGroup.tabText(tabIndex)).lower()

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

    def updateMicrophoneCalibration(self, x):
        mphonesens = self.ui.mphoneSensSpnbx.value()
        mphonedb = self.ui.mphoneDBSpnbx.value()
        self.acqmodel.set_mphone_calibration(mphonesens, mphonedb)

    def saveExploreToggled(self, save):
        self.saveExplore = save

    def clearProtocol(self):
        self.ui.protocolView.model().clearTests()

    def updateCalDb(self):
        self.calvals['caldb'] = self.ui.refDbSpnbx.value()
        self.acqmodel.set(caldb=self.calvals['caldb'])

    def setStatusMsg(self, status):
        self.statusBar().showMessage(status)

    def toggleResponsePolarity(self):
        self.acqmodel.toggle_response_polarity()

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




