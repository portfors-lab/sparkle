import sys, os
import time
import pickle
import queue
from scipy.integrate import simps, trapz
from PyQt4 import QtCore, QtGui
from PyDAQmx import *
import numpy as np

from daq_tasks import *
from plotz import *
from audiotools import *
from calform import Ui_CalibrationWindow
from disp_dlg import DisplayDialog
from scale_dlg import ScaleDialog
from saving_dlg import SavingDialog

#defauts used only if user data not saved
AIPOINTS = 100
CALDB = 100
CALV = 0.175
CALF = int(15000)
DBFACTOR = 20
CALHACK = 0.136
NBPATH = 'C:\\Users\\amy.boyle\\src\\notebooks\\'

XLEN = 5 #seconds, also not used?
SAVE_DATA_CHART = False
SAVE_DATA_TRACES = True
SAVE_FFT_DATA = True
USE_FINITE = True
VERBOSE = True
SAVE_NOISE = False
SAVE_OUTPUT = False
PRINT_WARNINGS = True

FFT_FNAME = '_ffttraces'
PEAKS_FNAME =  '_fftpeaks'
DB_FNAME = '_resultdb'
INDEX_FNAME = '_index'
DATA_FNAME = "_rawdata"
NOISE_FNAME = "_noise"
OUTPUT_FNAME = "_outtones"

class Calibrator(QtGui.QMainWindow):
    def __init__(self, dev_name, parent=None):
        #auto generated code intialization
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_CalibrationWindow()
        self.ui.setupUi(self)

        cnames = get_ao_chans(dev_name.encode())
        self.ui.aochan_box.addItems(cnames)
        cnames = get_ai_chans(dev_name.encode())
        self.ui.aichan_box.addItems(cnames)

        self.ui.start_button.clicked.connect(self.on_start)
        self.ui.stop_button.clicked.connect(self.on_stop)
        self.red = QtGui.QPalette()
        self.red.setColor(QtGui.QPalette.Foreground,QtCore.Qt.red)
        self.green = QtGui.QPalette()
        self.green.setColor(QtGui.QPalette.Foreground,QtCore.Qt.green)
        self.ui.running_label.setPalette(self.red)

        self.tone = []
        self.display = None
        self.ainpts = AIPOINTS # gets overriden (hopefully)
        self.caldb = CALDB
        self.calv = CALV
        self.calf = CALF
        self.fscale = 1000
        self.tscale = 0.001

        self.savefolder = NBPATH
        self.savename = "cal"

        inlist = load_inputs()
        if len(inlist) > 0:
            try:
                self.ui.freq_spnbx.setValue(inlist[0])
                self.ui.sr_spnbx.setValue(inlist[1])
                self.ui.dur_spnbx.setValue(inlist[2])
                self.ui.db_spnbx.setValue(inlist[3])
                self.ui.risefall_spnbx.setValue(inlist[4])
                self.ui.aochan_box.setCurrentIndex(inlist[5])
                self.ui.aichan_box.setCurrentIndex(inlist[6])
                self.ainpts = inlist[7]
                self.ui.aisr_spnbx.setValue(inlist[8])
                self.ui.interval_spnbx.setValue(inlist[9])

                # tab 2
                self.ui.freq_start_spnbx.setValue(inlist[10])
                self.ui.freq_stop_spnbx.setValue(inlist[11])
                self.ui.freq_step_spnbx.setValue(inlist[12])
                self.ui.db_start_spnbx.setValue(inlist[13])
                self.ui.db_stop_spnbx.setValue(inlist[14])
                self.ui.db_step_spnbx.setValue(inlist[15])
                self.ui.dur_spnbx_2.setValue(inlist[16])
                self.ui.risefall_spnbx_2.setValue(inlist[17])
                self.ui.reprate_spnbx.setValue(inlist[18])
                self.ui.sr_spnbx_2.setValue(inlist[19])
                self.ui.nreps_spnbx.setValue(inlist[20])

                self.caldb = inlist[21]
                self.calv = inlist[22]
                self.calf = inlist[23]
                self.savefolder = inlist[24]
                self.savename = inlist[25]
            except:
                print("failed to find all defaults")
                #raise

        self.set_interval_min()
        # lock for talking to the daq
        self.daq_lock = QtCore.QMutex()
        # lock for updating/ reading stimulus (for on-the-fly gen)
        self.stim_lock = QtCore.QMutex()
        # lock for saving to acquired data structure
        self.response_data_lock = QtCore.QMutex()
        # lock for live acquisition vs. processing data 
        # -- maybe a better way to do this with signals?
        self.live_lock = QtCore.QMutex()
        self.ngenerated = 0
        self.nacquired = 0
        self.apply_calibration = 0

        self.daq_timer = None
        self.aitask = None
        self.current_operation = None

        self.thread_pool = []
        self.pool = QtCore.QThreadPool()
        self.pool.setMaxThreadCount(5)

        self.signals = WorkerSignals()
        self.signals.done.connect(self.process_response)
        self.signals.curve_finished.connect(self.process_caldata)
        self.signals.update_stim_display.connect(self.stim_display)

    def on_start(self):
       
        aochan = self.ui.aochan_box.currentText().encode()
        aichan = self.ui.aichan_box.currentText().encode()

        # depending on currently displayed tab, present
        # tuning curve, or on-the-fly modifyable tone
        if SAVE_OUTPUT:
            self.tone_array = []

        self.apply_calibration = self.ui.applycal_ckbx.isChecked()
        self.save_as_calibration = self.ui.savecal_ckbx.isChecked()

        if self.apply_calibration:
            self.calibration_vector = np.load("calibration_data.npy")
            with open("calibration_index.pkl", 'rb') as pf:
                self.calibration_index = pickle.load(pf)
            print(self.calibration_index)

        self.halt = False

        if self.ui.tabs.currentIndex() == 0 :
            if self.live_lock.tryLock():
                # on the fly
                self.current_operation = 0

                # this shouldn't actually be possible still...
                if self.aitask is not None:
                    self.on_stop()
                    print("FIX ME : NESTED START OPERATIONS ALLOWED")
                    
                self.ngenerated = 0
                self.nacquired = 0
                # gets info from UI and creates tone
                self.update_stim()

                sr = self.sr
                npts = self.tone.size
                aisr = self.aisr
                interval = self.ui.interval_spnbx.value()

                if SAVE_DATA_CHART or SAVE_DATA_TRACES:
                    self.a = []
            
                if SAVE_FFT_DATA:
                    self.full_fft_data = []

                self.ndata = 0
                self.current_line_data = []

                # do not change interval on the fly
                self.ui.interval_spnbx.setEnabled(False)
                try:
                    if USE_FINITE:
                        # set a timer to repeatedly start ao and ai tasks
                        # set up first go before timer, so that the task starts as soon 
                        # as timer fires, to get most accurate rate
                        response_npts = int(self.aitime*aisr)
                        self.aitask = AITaskFinite(aichan, aisr, response_npts)
                        self.aotask = AOTaskFinite(aochan, sr, npts, trigsrc=b"ai/StartTrigger")
                        self.aotask.write(self.tone)
                
                        if SAVE_OUTPUT:
                            self.tone_array.append(self.tone[:])
                            
                        self.ui.running_label.setPalette(self.green)
                        self.ui.running_label.setText("RUNNING")
                        self.daq_timer = self.startTimer(interval)
                    else:
                        # use continuous acquisition task, using NIDAQ everyncallback
                        self.aitask = AITask(aichan, aisr, self.ainpts)
                        self.aotask = AOTask(aochan, sr, npts, 
                                             trigsrc=b"ai/StartTrigger")
                        self.aitask.register_callback(self.every_n_callback,
                                                      self.ainpts)
                        self.aotask.write(self.tone)
                        
                        if SAVE_OUTPUT:
                            self.tone_array.append(self.tone[:])

                        self.aotask.StartTask()
                        self.aitask.StartTask()
                except:
                    print('ERROR! TERMINATE!')
                    self.on_stop
                    raise
            else:
                print("start pressed when task already running, updating stimulus...")
                if USE_FINITE:
                    self.update_stim()
                else:
                    self.on_stop()
                    self.on_start()
        else:
            if self.live_lock.tryLock():
                # tuning curve style run-through
                self.current_operation = 1
                self.halt_curve = False

                # grey out interface during curve
                self.ui.tab_2.setEnabled(False)
                self.ui.start_button.setEnabled(False)
                self.ui.label4.setText("")

                self.ngenerated = 0
                self.nacquired = 0
            
                try:
                    #scale_factor = 1000
                    f_start = self.ui.freq_start_spnbx.value()*self.fscale
                    f_stop = self.ui.freq_stop_spnbx.value()*self.fscale
                    f_step = self.ui.freq_step_spnbx.value()*self.fscale
                    db_start = self.ui.db_start_spnbx.value()
                    db_stop = self.ui.db_stop_spnbx.value()
                    db_step = self.ui.db_step_spnbx.value()
                    dur = self.ui.dur_spnbx_2.value()*self.tscale
                    rft = self.ui.risefall_spnbx_2.value()*self.tscale
                    reprate = self.ui.reprate_spnbx.value()
                    sr = self.ui.sr_spnbx_2.value()*self.fscale
                    nreps = self.ui.nreps_spnbx.value()

                    # acquisitions threads must access the following data
                    self.dur = dur
                    self.sr = sr
                    self.rft = rft
                    self.nreps = nreps
                    self.aichan = aichan
                    self.aochan = aochan

                    if f_start < f_stop:
                        freqs = range(f_start, f_stop+1, f_step)
                    else:
                        freqs = range(f_start, f_stop-1, -f_step)
                    if db_start < db_stop:
                        intensities = range(db_start, db_stop+1, db_step)
                    else:
                        intensities = range(db_start, db_stop-1, -db_step)

                    # calculate ms interval from reprate
                    interval = (1/reprate)*1000

                    # set up display
                    if self.display == None or not(self.display.active):
                        self.spawn_display()
                    self.display.show()

                    # data structure to store the averages of the resultant FFT peaks
                    self.fft_peaks = np.zeros((len(freqs),len(intensities)))
                    self.playback_dB = np.zeros((len(freqs),len(intensities)))
                    self.vin = np.zeros((len(freqs),len(intensities)))
                    self.fft_vals_lookup = {}
                    self.fft_vals_index = np.zeros((len(freqs),len(intensities)))

                    if SAVE_FFT_DATA:
                        # 4D array nfrequencies x nintensities x nreps x npoints
                        self.full_fft_data = np.zeros((len(freqs),len(intensities),nreps,int((dur*sr)/2)))

                    if SAVE_DATA_TRACES:
                        self.data_traces = np.zeros((len(freqs),len(intensities),nreps,int(dur*sr)))

                    # data structure to hold repetitions, for averaging
                    self.rep_temp = []
                    self.vrep_temp = []
                    self.reject_list = []

                    if self.save_as_calibration:
                        self.freq_index = {}

                    self.work_queue = queue.Queue()
                    for ifreq, f in enumerate(freqs):
                        if self.save_as_calibration:
                            self.freq_index[f] = ifreq
                        for idb, db in enumerate(intensities):
                            for irep in range(nreps):
                                self.work_queue.put((f,db))
                                # also catalog where these values go in fft_max_vals
                                self.fft_vals_lookup[(f,db)] = (ifreq,idb)
                                #print(ifreq,idb)
                                #self.fft_vals_index[ifreq,idb] = (f,db)

                    self.ui.running_label.setText("RUNNING")
                    self.ui.running_label.setPalette(self.green)
                    self.daq_timer = self.startTimer(interval)

                    # save these lists for easier plotting later
                    self.freqs = freqs
                    self.intensities = intensities
                except:
                    self.live_lock.unlock()
                    print("handle curve set-up exception")
                    self.ui.tab_2.setEnabled(True)
                    self.ui.start_button.setEnabled(True)
                    raise
            else:
                print("Operation alread in progress")

    def curve_worker(self, f, db):
        print("curve worker")

        self.ui.flabel.setText("Frequency : %d" % (f))
        self.ui.dblabel.setText("Intensity : %d" % (db))

        sr = self.sr
        dur = self.dur
        rft = self.rft

        if self.apply_calibration:
            cidx = self.calibration_index[f]
            adjdb = self.calibration_vector[cidx]
            adjdb = 100 - adjdb
        else:
            adjdb = 0

        # make a tone, calculate it's fft and display
        tone, times = make_tone(f, db, dur, rft, sr, self.caldb, self.calv, adjustdb=adjdb)
        self.ui.label0.setText("AO Vmax : %.5f" % (np.amax(abs(tone))))

        if PRINT_WARNINGS:
            if np.amax(abs(tone)) < 0.005:
                print("WARNING : ENTIRE OUTPUT TONE VOLTAGE LESS THAN DEVICE MINIMUM")
        xfft, yfft = calc_spectrum(tone, sr)

        try:
            self.signals.update_stim_display.emit(times, tone, xfft, abs(yfft))
        except:
            print("WARNING : Problem drawing stim to Window")

        # now present the tone once
        self.daq_lock.lock()

        aitask = AITaskFinite(self.aichan, sr, len(tone))
        aotask = AOTaskFinite(self.aochan, sr, len(tone), trigsrc=b"ai/StartTrigger")
        aotask.write(tone)

        if SAVE_OUTPUT:
            self.tone_array.append(self.tone[:])
        
        aotask.StartTask()
        aitask.StartTask()
                        
        self.ngenerated +=1
        # blocking read
        data = aitask.read()
        
        aitask.stop()
        aotask.stop()

        self.daq_lock.unlock()

        #self.current_line_data = data
        #self.process_response(f,db)
        self.signals.done.emit(f, db, data[:])

    def process_caldata(self):
        #After running curve do calculations and save data to file
        self.live_lock.lock()
        print("job finished")
        #print('fft peaks ', self.fft_peaks)
        print('rejects ', self.reject_list)
        # go through FFT peaks and calculate playback resultant dB
        #for freq in self.fft_peaks
        vfunc = np.vectorize(calc_db)
        #dB_from_v_vfunc = np.vectorize(calc_db_from_v)

        try:
            self.response_data_lock.lock()
            ifreq, idb = self.fft_vals_lookup[(self.calf,self.caldb)]
            cal_fft_peak = self.fft_peaks[ifreq][idb]
            cal_vmax =  self.vin[ifreq][idb]
            self.response_data_lock.unlock()
            print("Using FFT peak data from ", self.caldb, " dB, ", 
                  self.calf, " Hz tone to calculate calibration curve")
        except:
            print("WARNING : using manual %.4f fft peak" % (CALHACK))
            cal_fft_peak = CALHACK
            cal_vmax = 0

        #resultant_dB = vfunc(self.fft_peaks, self.caldb, cal_fft_peak)
        resultant_dB = vfunc(self.vin, self.caldb, cal_vmax)

        fname = self.savename
        while os.path.isfile(os.path.join(self.savefolder, fname + INDEX_FNAME + ".pkl")):
            # increment filename until we come across one that 
            # doesn't exist
            if not fname[-1].isdigit():
                fname = fname + '0'
            else:
                currentno = re.search('(\d+)$', fname).group(0)
                prefix = fname[:-(len(currentno))]
                currentno = int(currentno) +1
                fname = prefix + str(currentno)

        self.statusBar().showMessage("writing " + fname)
        if SAVE_FFT_DATA:
            self.response_data_lock.lock()
            filename = os.path.join(self.savefolder, fname + FFT_FNAME)
            np.save(filename, self.full_fft_data)

            filename = os.path.join(self.savefolder, fname + PEAKS_FNAME)
            np.save(filename, self.fft_peaks)

            with open(os.path.join(self.savefolder, fname + INDEX_FNAME + ".pkl"), 'wb') as cfo:
                # make a dictionary of the other paramters used to 
                # generate this roll-off curve
                params = {'calV': self.calv, 'caldB' : self.caldb, 
                          'calf' : self.calf, 'rft' : self.rft, 
                          'samplerate' : self.sr, 'duration' : self.dur}
                pickle.dump([self.fft_vals_lookup, self.reject_list, params], cfo)

            if SAVE_DATA_TRACES:
                filename = os.path.join(self.savefolder, fname + DATA_FNAME)
                np.save(filename, self.data_traces)

            self.response_data_lock.unlock()

            if SAVE_OUTPUT:
                filename = os.path.join(self.savefolder, fname + OUTPUT_FNAME)
                np.save(filename, self.tone_array)

        filename = os.path.join(self.savefolder, fname + DB_FNAME)
        np.save(filename, resultant_dB)
        np.savetxt(filename+".txt", resultant_dB)

        if self.save_as_calibration:
            filename = "calibration_data"
            calibration_vector = resultant_dB[:,0]
            np.save(filename,calibration_vector)
            with open("calibration_index.pkl",'wb') as pkf:
                pickle.dump(self.freq_index, pkf)

        print("plotting calibration curve")
        plot_cal_curve(resultant_dB, self.freqs, self.intensities, self)

        if SAVE_NOISE:
            #noise_vfunc = np.vectorize(calc_noise)
            #noise_array = noise_vfunc(self.full_fft_data,0,2000)
            noise_array = np.zeros((len(self.freqs),len(self.intensities),self.nreps))
            for ifreq in range(len(self.freqs)):
                for idb in range(len(self.intensities)):
                    for irep in range(self.nreps):
                        noise_array[ifreq,idb,irep] = calc_noise(self.full_fft_data[ifreq,idb,irep], 0, 2000)

            np.save(self.savefolder + fname + NOISE_FNAME, noise_array)

        self.live_lock.unlock()

    def on_stop(self):
        if self.current_operation == 0 : 
            if USE_FINITE:
                self.ui.interval_spnbx.setEnabled(True)
                if self.daq_timer is not None:
                    self.ui.running_label.setText("STOPPING")
                    self.killTimer(self.daq_timer)
                    self.daq_timer = None
                    self.halt = True
                    self.pool.waitForDone()
                    self.ui.running_label.setText("BUSY")
                    self.ui.running_label.setPalette(self.red)
                    QtGui.QApplication.processEvents()
                    self.save_speculative_data()
                try:
                    self.aitask.stop()
                    self.aotask.stop()
                    self.aitask = None
                    self.aotask = None
                except DAQError:
                    print("No task running")
                except:
                    pass
                    #raise
           
        elif self.current_operation == 1:
            self.killTimer(self.daq_timer)
            self.halt = True
            self.ui.tab_2.setEnabled(True)
            self.ui.start_button.setEnabled(True)
            # no need to kill tasks since they will finish in the thread
            self.pool.waitForDone()

            self.aitask = None
            self.aotask = None
        else:
            print("No task currently running")
        self.ui.running_label.setText("OFF")
        self.ui.running_label.setPalette(self.red)

    def save_speculative_data(self):
        #print("locking")
        #self.live_lock.lock()
        if SAVE_OUTPUT:
            # due to the method of loading the write, the last tone in
            # tone array was never generated, so delete it
            del self.tone_array[-1]
            print("saving output tones, shape : ", len(self.tone_array), ', ', len(self.tone_array[0]))
            filename = OUTPUT_FNAME
            np.save(filename, self.tone_array)
        if SAVE_FFT_DATA:
            print("saving fft traces, shape : ", len(self.full_fft_data), ', ', len(self.full_fft_data[0]))
            filename = FFT_FNAME
            np.save(filename, self.full_fft_data)
        self.live_lock.unlock()

    def update_stim(self):
        scale_factor = 1000
        time_scale = 1000
        f = self.ui.freq_spnbx.value()*self.fscale
        sr = self.ui.sr_spnbx.value()*self.fscale
        dur = self.ui.dur_spnbx.value()*self.tscale
        db = self.ui.db_spnbx.value()
        rft = self.ui.risefall_spnbx.value()*self.tscale
        aisr =  self.ui.aisr_spnbx.value()*self.fscale

        if self.apply_calibration:
            cidx = self.calibration_index[f]
            adjdb = self.calibration_vector[cidx]
            adjdb = 100 - adjdb
        else:
            adjdb=0

        tone, timevals = make_tone(f,db,dur,rft,sr, self.caldb, self.calv, adjustdb=adjdb)
        
        npts = tone.size

        #also plot stim FFT
        freq, spectrum = calc_spectrum(tone,sr)
       
        self.stim_lock.lock()
        self.tone = tone
        self.sr = sr
        self.aitime = dur
        self.aisr = aisr
        self.stim_lock.unlock()
        self.fdb = (f,db)

        self.statusBar().showMessage('npts: {}'.format(npts))
        print('\n' + '*'*40 + '\n')

        self.ui.flabel.setText("Frequency : %d" % (f))
        self.ui.dblabel.setText("Intensity : %d" % (db))
        self.ui.label0.setText("AO Vmax : %.5f" % (np.amax(abs(tone))))

        print("update_stim")
        # now update the display of the stim
        if self.display == None or not(self.display.active):
            self.spawn_display()
            
        self.stim_display(timevals, tone, freq, abs(spectrum))
        #self.display.ylim_auto([self.display.axs[2]])

    def spawn_display(self):
        self.display = AnimatedWindow(([],[]), ([],[]), 
                                      ([[],[]],[[],[]]), parent=self)
        self.display.show()
        # set axes limits appropriately
        self.display.axs[0].set_title("Stimulus")
        self.display.axs[0].set_xlim(0,3)
        self.display.axs[0].set_ylim(-10,10)
        self.display.axs[1].set_title("Response")
        self.display.axs[1].set_xlim(0,3)
        self.display.axs[1].set_ylim(-10,10)
        self.display.axs[2].set_title("FFTs")
        self.display.axs[2].set_xlim(0,self.sr/2)
        self.display.axs[1].lines[0].set_color('g')
        #self.display.canvas.draw()

    def stim_display(self, xdata, ydata, xfft, yfft):
        # hard coded for stim in axes 0 and FFT in 2
        try:
            self.display.draw_line(0, 0, xdata, ydata)
            self.display.draw_line(2, 0, xfft, yfft)
        except:
            print("WARNING : Problem drawing stim to Window")

    def process_response(self, f, db, data):
        try:
            #print("process response")
            sr = self.sr

            # extract information from acquired tone, and save
            freq, spectrum = calc_spectrum(data, sr)

            # take the abs (should I do this?), and get the highest peak
            spectrum = abs(spectrum)

            maxidx = spectrum.argmax(axis=0)
            max_freq = freq[maxidx]
            spec_max = np.amax(spectrum)

            fidx = np.where(freq==f)
            #where returns a tuple of a list of indices and type          
            fidx = fidx[0][0]
            spec_peak_at_f = spectrum[fidx]

            vmax = np.amax(abs(data))
            
            self.ui.label1.setText("AI Vmax : %.5f" % (vmax))
            self.ui.label2.setText("FFT peak : %.6f, \t at %d Hz\n" % (np.amax(spectrum), max_freq))
            self.ui.label3.setText("FFT peak at %d kHz : %.6f" % (f/1000, spec_peak_at_f))
            if self.current_operation == 0 and self.apply_calibration:
                self.ui.label4.setText("Response dB : %.2f" % (calc_db(spec_peak_at_f, self.caldb, CALHACK)))

            if vmax < 0.005:
                if PRINT_WARNINGS:
                    print("WARNING : RESPONSE VOLTAGE BELOW DEVICE FLOOR")
                self.statusBar().showMessage("WARNING : RESPONSE VOLTAGE BELOW DEVICE FLOOR")
            else:
                self.statusBar().showMessage("")

            #tolerance of 1 Hz for frequency matching
            if max_freq < f-1 or max_freq > f+1:
                if PRINT_WARNINGS:
                    print("WARNING : MAX SPECTRAL FREQUENCY DOES NOT MATCH STIMULUS")
                    print("\tTarget : {}, Received : {}".format(f, max_freq))
                if self.current_operation == 1:
                    ifreq, idb = self.fft_vals_lookup[(f,db)]
                    self.reject_list.append((f, db, ifreq, idb))            

            if VERBOSE:
                #print(maxidx)
                print("%.5f AI V" % (vmax))
                print("%.6f FFT peak, at %d Hz\n" % (spec_max, max_freq))
            
            try:
                times = np.arange(len(data))/sr
                self.display.draw_line(1,0, times, data)
                self.display.draw_line(2,1, freq, spectrum)
            except:
                print("WARNING : Problem drawing to Window")        

            if self.current_operation == 1:
                self.response_data_lock.lock()        
                self.rep_temp.append(spec_peak_at_f)
                self.vrep_temp.append(vmax)
                if len(self.rep_temp) == self.nreps:
                    ifreq, idb = self.fft_vals_lookup[(f,db)]
                    self.fft_peaks[ifreq][idb] =  np.mean(self.rep_temp)
                    self.vin[ifreq][idb] = np.mean(self.vrep_temp)
                    if VERBOSE:
                        print('\n' + '*'*40)
                        print("Rep values: {}\nRep mean: {}".format(self.rep_temp, np.mean(self.rep_temp)))
                        print("V rep values: {}\nV rep mean: {}".format(self.vrep_temp, np.mean(self.vrep_temp)))
                        print('*'*40 + '\n')
                    self.rep_temp = []
                    self.vrep_temp = []
                self.response_data_lock.unlock()

                if SAVE_FFT_DATA:
                    irep = len(self.rep_temp) - 1
                    if irep < 0 :
                        irep = self.nreps - 1 
                    ifreq, idb = self.fft_vals_lookup[(f,db)]
                    self.full_fft_data[ifreq][idb][irep] = spectrum

                    if SAVE_DATA_TRACES: 
                        self.data_traces[ifreq][idb][irep] = data
                self.response_data_lock.unlock()

            elif self.current_operation == 0:
                if SAVE_FFT_DATA:
                    self.response_data_lock.lock()
                    self.full_fft_data.append(spectrum)
                    self.response_data_lock.unlock()
            else:
                raise Exception("Unknown Operation Error")
            self.nacquired +=1
        except:
            print("Error processing response data")
            #self.on_stop()
            raise   

        print('generated ', self.ngenerated, ', acquired ', self.nacquired, ', halted ', self.halt)
        
        if self.current_operation == 0:
            if self.halt and self.ngenerated == self.nacquired:
                print("finished collecting, wrapping up...")
                self.live_lock.unlock()
        elif self.current_operation == 1:
            # or should I emit a signal to execute this? 
            # I don't think it matters in the main thread
            if self.nacquired == len(self.freqs) * len(self.intensities) * self.nreps:
                print("unlock live")
                self.live_lock.unlock()
                self.process_caldata()
        else:
            print('ERROR: NO TASK DETECTED AFTER PROCESS REPSONSE')
           
    def timerEvent(self, evt):
        #print("tick")
        if self.current_operation == 0:

            t  = GenericThread(self.finite_worker)
           
        elif self.current_operation == 1:

            # if timing is correct and feasible (i.e. interval >= duration), locking 
            # shouldn't strictly be necessesary, but for posterity...
            self.stim_lock.lock()
            if self.work_queue.empty():
                # no more work, quit
                print("outta work")
                self.stim_lock.unlock()
                self.on_stop()
                #self.process_caldata()
                return
            else:
                f, db = self.work_queue.get()
            self.stim_lock.unlock()

            # spawn thread for next item in queue
            t  = GenericThread(self.curve_worker, f, db)
        self.pool.start(t)

    def finite_worker(self):
        #print("finite worker")

        # acquire data and reset task to be read for next timer event
        self.daq_lock.lock()
        self.aotask.StartTask()
        self.aitask.StartTask()
        
        self.ngenerated +=1

        # blocking read
        data = self.aitask.read()

        self.aitask.stop()
        self.aotask.stop()

        aochan = self.ui.aochan_box.currentText().encode()
        aichan = self.ui.aichan_box.currentText().encode()

        self.stim_lock.lock()

        npts =  self.tone.size
        response_npts = int(self.aitime*self.aisr)

        self.aitask = AITaskFinite(aichan, self.aisr, response_npts)
        self.aotask = AOTaskFinite(aochan, self.sr, npts, trigsrc=b"ai/StartTrigger")
        self.aotask.write(self.tone)

        if SAVE_OUTPUT:
            self.tone_array.append(self.tone[:])

        self.daq_lock.unlock()
        self.stim_lock.unlock()

        f, db = self.fdb
        self.signals.done.emit(f, db, data[:])
        
    def every_n_callback(self,task):
        
        # read in the data as it is acquired and append to data structure
        try:
            read = c_int32()
            inbuffer = np.zeros(task.n)
            task.ReadAnalogF64(task.n,10.0,DAQmx_Val_GroupByScanNumber,
                               inbuffer,task.n,byref(read),None)
            if SAVE_DATA_CHART:
                self.a.extend(inbuffer.tolist())
                # for now use stimulus data size also for acquisition
                #ainpts = len(self.tone)

            #print(self.data[0])
            self.ndata += read.value
            #print(self.ndata)
            
            n = read.value
            lims = self.display.axs[1].axis()
            #print("lims {}".format(lims))
            #print("ndata {}".format(self.ndata))
            
            # for display purposes only
            ndata = len(self.current_line_data)
            aisr = self.aisr

            #print(self.aisr, self.aitime, ndata/aisr)
            if ndata/aisr >= self.aitime:
                if len(self.current_line_data) != self.aitime*self.aisr:
                    print("incorrect number of data points saved")
                if SAVE_DATA_TRACES:
                    self.a.append(self.current_line_data)
                self.current_line_data = []
            
            self.current_line_data.extend(inbuffer.tolist())
        except MemoryError:
            print("data size: {}, elements: {}"
                  .format(sys.getsizeof(self.a)/(1024*1024), len(self.a)))
            self.aitask.stop()
            self.aotask.stop()
            raise
        except: 
            print('ERROR! TERMINATE!')
            #print("data size: {}, elements: {}".format(sys.getsizeof(self.a)/(1024*1024), len(self.a)))
            self.aitask.stop()
            self.aotask.stop()
            raise

    def set_interval_min(self):
        dur = self.ui.dur_spnbx.value()
        interval = self.ui.interval_spnbx.value()
        if interval < dur:
            print("interval less than duration, increasing interval")
            self.ui.interval_spnbx.setValue(dur)
        if interval == dur:
            print("Warning: No interval down-time, consider using continuous acquisition to avoid failure.")

    def set_dur_max(self):
        dur = self.ui.dur_spnbx_2.value()
        reprate = self.ui.reprate_spnbx.value()
        if reprate < (dur/1000):
            self.ui.dur_spnbx_2.setValue(reprate*1000)

    def xor_applycal(self,checked):
        if checked:
            self.ui.applycal_ckbx.setChecked(False)

    def xor_savecal(self,checked):
        if checked:
            self.ui.savecal_ckbx.setChecked(False)

    def launch_display_dlg(self):
        field_vals = {'chunksz' : self.ainpts, 'caldb': self.caldb, 'calv': self.calv, 'calf' : self.calf}
        dlg = DisplayDialog(default_vals=field_vals)
        if dlg.exec_():
            ainpts, caldb, calv, calf = dlg.get_values()
            self.ainpts = ainpts
            self.caldb = caldb
            self.calv = calv
            self.calf = calf

    def launch_scaledlg(self):
        field_vals = {'fscale' : self.fscale, 'tscale' : self.tscale}
        dlg = ScaleDialog(default_vals=field_vals)
        if dlg.exec_():
            fscale, tscale = dlg.get_values()
            self.fscale = fscale
            self.tscale = tscale
        self.update_unit_labels()

    def launch_savedlg(self):
        field_vals = {'savefolder' : self.savefolder, 'savename' : self.savename, 'saveformat' : 'npy'}
        dlg = SavingDialog(default_vals = field_vals)
        if dlg.exec_():
            savefolder, savename, saveformat = dlg.get_values()
            self.savefolder = savefolder
            self.savename = savename
            #self.saveformat = saveformat

    def update_unit_labels(self):
        if self.fscale == 1000:
            self.ui.f_units.setText('kHz')
            self.ui.sr_units.setText('kHz')
            self.ui.aisr_units.setText('kHz')
        elif self.fscale == 1:
            self.ui.f_units.setText('Hz')
            self.ui.sr_units.setText('Hz')
            self.ui.aisr_units.setText('Hz')
        else:
            print(self.fscale)
            raise Exception("Invalid frequency scale")
            
        if self.tscale == 0.001:
            self.ui.dur_units.setText('ms')
            self.ui.interval_units.setText('ms')
            self.ui.risefall_units.setText('ms')
        elif self.tscale == 1:
            self.ui.dur_units.setText('s')
            self.ui.interval_units.setText('s')
            self.ui.risefall_units.setText('s')
        else:
            print(self.tscale)
            raise Exception("Invalid time scale")
            
    def keyPressEvent(self,event):
        print("keypress from calibrator")
        #print(event.text())
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            if USE_FINITE:
                self.update_stim()
            else:
                self.on_stop()
                self.on_start()
            self.setFocus()
        elif event.key () == QtCore.Qt.Key_Escape:
            self.setFocus()
        elif event.text() == 'r':
            print("redraw")
            self.display.redraw()
        
    def closeEvent(self,event):
        # halt acquisition loop
        self.on_stop()

        outlist = []
        #save inputs into file to load up next time - order is important
        outlist.append(self.ui.freq_spnbx.value())
        outlist.append(self.ui.sr_spnbx.value())
        outlist.append(self.ui.dur_spnbx.value())
        outlist.append(self.ui.db_spnbx.value())
        outlist.append(self.ui.risefall_spnbx.value())
        outlist.append(self.ui.aochan_box.currentIndex())
        outlist.append(self.ui.aichan_box.currentIndex())
        outlist.append(self.ainpts)
        outlist.append(self.ui.aisr_spnbx.value())
        outlist.append(self.ui.interval_spnbx.value())

        outlist.append(self.ui.freq_start_spnbx.value())
        outlist.append(self.ui.freq_stop_spnbx.value())
        outlist.append(self.ui.freq_step_spnbx.value())
        outlist.append(self.ui.db_start_spnbx.value())
        outlist.append(self.ui.db_stop_spnbx.value())
        outlist.append(self.ui.db_step_spnbx.value())
        outlist.append(self.ui.dur_spnbx_2.value())
        outlist.append(self.ui.risefall_spnbx_2.value())
        outlist.append(self.ui.reprate_spnbx.value())
        outlist.append(self.ui.sr_spnbx_2.value())
        outlist.append(self.ui.nreps_spnbx.value())

        outlist.append(self.caldb)
        outlist.append(self.calv)
        outlist.append(self.calf)
        outlist.append(self.savefolder)
        outlist.append(self.savename)

        save_inputs(outlist)

        QtGui.QMainWindow.closeEvent(self,event)

class GenericThread(QtCore.QRunnable):
    def __init__(self, function, *args, **kwargs):
        QtCore.QRunnable.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs
    """
    def __del__(self):
        self.wait()
    """
    def run(self):
        self.function(*self.args,**self.kwargs)
        return

class WorkerSignals(QtCore.QObject):
    done = QtCore.pyqtSignal(int, int, numpy.ndarray)
    curve_finished = QtCore.pyqtSignal()
    update_stim_display = QtCore.pyqtSignal(numpy.ndarray,numpy.ndarray, numpy.ndarray, numpy.ndarray)

def load_inputs():
    cfgfile = "inputs.cfg"
    try:
        with open(cfgfile, 'rb') as cfo:
            input_list = pickle.load(cfo)
    except:
        print("error loading user inputs file")
        #raise
        input_list = []
    return input_list

def save_inputs(savelist):
    #should really do this with a dict
    cfgfile = "inputs.cfg"
    with open(cfgfile, 'wb') as cfo:
        pickle.dump(savelist,cfo)

def plot_cal_curve(results_array, freqs, intensities, p):
    # plot calibration curve: frequency against resultant dB by
    # target dB
    curve_lines = []
    for idb in range(results_array.shape[1]):
        ydata = results_array[:,idb]
        curve_lines.append((freqs,ydata))
    calcurve_plot = BasicPlot(*curve_lines, parent=p)
    calcurve_plot.setWindowTitle("Calibration Curve")
    calcurve_plot.axs[0].set_xlabel("Frequency (Hz)")
    calcurve_plot.axs[0].set_ylabel("Recorded dB")
    # set the labels on the lines for the legend
    for iline, line in enumerate(calcurve_plot.axs[0].lines):
        line.set_label(intensities[iline])
    calcurve_plot.axs[0].legend()
    calcurve_plot.show()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    devName = "PCI-6259"
    myapp = Calibrator(devName)
    myapp.show()
    sys.exit(app.exec_())
