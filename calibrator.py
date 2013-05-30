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
from calform import Ui_CalibrationWindow
from disp_dlg import DisplayDialog

#defauts used only if user data not saved
AIPOINTS = 100
CALDB = 100
CALV = 0.175
CALF = int(15000)
DBFACTOR = 20
CALHACK = 0.136

XLEN = 5 #seconds, also not used?
SAVE_DATA_CHART = False
SAVE_DATA_TRACES = False
SAVE_FFT_DATA = True
USE_FINITE = True
VERBOSE = False
SAVE_NOISE = True

NBPATH = 'C:\\Users\\amy.boyle\\src\\notebooks\\'
NBPATH = 'C:\\Users\\Leeloo\\src\\python\\notebooks\\'


FFT_FNAME = NBPATH + 'caltest_data'
PEAKS_FNAME =  NBPATH + 'fftpeaks'
DB_FNAME =  NBPATH + 'resultdb'
INDEX_FNAME =  NBPATH + "index"
DATA_FNAME = NBPATH + "rawdata"
NOISE_FNAME = NBPATH + "noise"

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

        self.tone = []
        self.display = None
        self.ainpts = AIPOINTS # gets overriden (hopefully)
        self.caldb = CALDB
        self.calv = CALV
        self.calf = CALF

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
            except:
                print("failed to find all defaults")
                #raise

        self.set_interval_min()
        self.daq_lock = QtCore.QMutex()
        self.stim_lock = QtCore.QMutex()
        self.curve_data_lock = QtCore.QMutex()
        self.daq_timer = None
        self.aitask = None
        self.current_operation = None

        self.thread_pool = []
        self.pool = QtCore.QThreadPool()
        self.pool.setMaxThreadCount(5)

        self.signals = WorkerSignals()
        self.signals.done.connect(self.process_response)
        self.signals.curve_finished.connect(self.process_caldata)

    def on_start(self):
       
        aochan = self.ui.aochan_box.currentText().encode()
        aichan = self.ui.aichan_box.currentText().encode()

        # depending on currently displayed tab, present
        # tuning curve, or on-the-fly modifyable tone
        
        if self.ui.tabs.currentIndex() == 0 :
            # on the fly
            self.current_operation = 0
            if self.aitask is not None:
                self.on_stop()

            self.cnt = 0
            # gets info from UI and creates tone
            self.update_stim()

            sr = self.sr
            npts = self.tone.size
            aisr = self.aisr
            interval = self.ui.interval_spnbx.value()

            if SAVE_DATA_CHART or SAVE_DATA_TRACES:
                self.a = []
            
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
                
                    self.daq_timer = self.startTimer(interval)
                else:
                    # use continuous acquisition task, using NIDAQ everyncallback
                    self.aitask = AITask(aichan, aisr, self.ainpts)
                    self.aotask = AOTask(aochan, sr, npts, 
                                         trigsrc=b"ai/StartTrigger")
                    self.aitask.register_callback(self.every_n_callback,
                                                  self.ainpts)
                    self.aotask.write(self.tone)
                    
                    self.aotask.StartTask()
                    self.aitask.StartTask()
            except:
                print('ERROR! TERMINATE!')
                self.on_stop
                raise
        else:
            # tuning curve style run-through
            self.current_operation = 1
            self.halt_curve = False

            # grey out interface during curve
            self.ui.tab_2.setEnabled(False)
            self.ui.start_button.setEnabled(False)
            self.ui.label4.setText("")
            
            try:
                scale_factor = 1000
                f_start = self.ui.freq_start_spnbx.value()*scale_factor
                f_stop = self.ui.freq_stop_spnbx.value()*scale_factor
                f_step = self.ui.freq_step_spnbx.value()*scale_factor
                db_start = self.ui.db_start_spnbx.value()
                db_stop = self.ui.db_stop_spnbx.value()
                db_step = self.ui.db_step_spnbx.value()
                dur = self.ui.dur_spnbx_2.value()/scale_factor
                rft = self.ui.risefall_spnbx_2.value()/scale_factor
                reprate = self.ui.reprate_spnbx.value()
                sr = self.ui.sr_spnbx_2.value()*scale_factor
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
                self.fft_vals_lookup = {}

                if SAVE_FFT_DATA:
                    # 4D array nfrequencies x nintensities x nreps x npoints
                    self.full_fft_data = np.zeros((len(freqs),len(intensities),nreps,int((dur*sr)/2)))

                if SAVE_DATA_TRACES:
                    self.data_traces = np.zeros((len(freqs),len(intensities),nreps,int(dur*sr)))

                # data structure to hold repetitions, for averaging
                self.rep_temp = []
                self.reject_list = []
                
                self.work_queue = queue.Queue()
                for ifreq, f in enumerate(freqs):
                    for idb, db in enumerate(intensities):
                        for irep in range(nreps):
                            self.work_queue.put((f,db))
                            # also catalog where these values go in fft_max_vals
                            self.fft_vals_lookup[(f,db)] = (ifreq,idb)

                self.daq_timer = self.startTimer(interval)
                
                # save these lists for easier plotting later
                self.freqs = freqs
                self.intensities = intensities
            except:
                print("handle curve set-up exception")
                self.ui.tab_2.setEnabled(True)
                self.ui.start_button.setEnabled(True)
                raise

    def curve_worker(self, f, db):

        self.ui.flabel.setText("Frequency : %d" % (f))
        self.ui.dblabel.setText("Intensity : %d" % (db))

        sr = self.sr
        dur = self.dur
        rft = self.rft

        # make a tone, calculate it's fft and display
        tone, times = make_tone(f, db, dur, rft, sr, self.caldb, self.calv)
        self.ui.label0.setText("AO Vmax : %.5f" % (np.amax(abs(tone))))

        if np.amax(abs(tone)) < 0.1:
            print("WARNING : ENTIRE OUTPUT TONE VOLTAGE LESS THAN DEVICE MINIMUM")
        xfft, yfft = calc_spectrum(tone, sr)

        try:
            self.display.draw_line(0, 0, times, tone)
            self.display.draw_line(2, 0, xfft, abs(yfft))
         except:
             print("WARNING : Problem drawing stim to Window")

        # now present the tone once
        self.daq_lock.lock()

        aitask = AITaskFinite(self.aichan, sr, len(tone))
        aotask = AOTaskFinite(self.aochan, sr, len(tone), trigsrc=b"ai/StartTrigger")
        aotask.write(tone)
        aotask.StartTask()
        aitask.StartTask()
                        
        # blocking read
        data = aitask.read()
        
        aitask.stop()
        aotask.stop()

        self.daq_lock.unlock()

        self.current_line_data = data
        #self.process_response(f,db)
        self.signals.done.emit(f,db)
        return
        print("SHOULD NOT GET HERE")

        # extract information from acquired tone, and save
        freq, spectrum = calc_spectrum(data, sr)

        # take the abs (should I do this?), and get the highest peak
        spectrum = abs(spectrum)
        maxidx = spectrum.argmax(axis=0)
        #max_freq = freq[maxidx]
        #spec_max = np.amax(spectrum)
        maxidx = np.where(freq==f)
        max_freq = freq[maxidx]
        spec_max = spectrum[maxidx]
        vmax = np.amax(abs(data))

        self.ui.label1.setText("AI Vmax : %.5f" % (np.amax(abs(data))))
        self.ui.label2.setText("FFT peak : %.6f, \t at %d Hz\n" % (np.amax(spectrum), max_freq))
        if vmax < 0.1:
            print("WARNING : RESPONSE VOLTAGE BELOW DEVICE FLOOR")

        #tolerance of 1 Hz for frequency matching
        if max_freq < f-1 or max_freq > f+1:
            print("WARNING: MAX SPECTRAL FREQUENCY DOES NOT MATCH STIMULUS")
            print("\tTarget : {}, Received : {}".format(f, max_freq))
            ifreq, idb = self.fft_vals_lookup[(f,db)]
            self.reject_list.append((f, db, ifreq, idb))            

        if VERBOSE:
            #print(maxidx)
            print("%.5f AI V" % (vmax))
            print("%.6f FFT peak, at %d Hz\n" % (spec_max, max_freq))
            
        self.display.draw_line(1,0, times, data)
        self.display.draw_line(2,1, freq, spectrum)
        
        self.curve_data_lock.lock()        
        self.rep_temp.append(spec_max)
        if len(self.rep_temp) == self.nreps:
            ifreq, idb = self.fft_vals_lookup[(f,db)]
            self.fft_peaks[ifreq][idb] =  np.mean(self.rep_temp)
            if VERBOSE:
                print('\n' + '*'*40)
                print("Rep values: {}\nRep mean: {}".format(self.rep_temp, np.mean(self.rep_temp)))
                print('*'*40 + '\n')
            self.rep_temp = []
        self.curve_data_lock.unlock()

        if SAVE_FFT_DATA:
            irep = len(self.rep_temp) - 1
            if irep < 0 :
                irep = self.nreps - 1 
            ifreq, idb = self.fft_vals_lookup[(f,db)]
            self.full_fft_data[ifreq][idb][irep] = spectrum

            if SAVE_DATA_TRACES: 
                self.data_traces[ifreq][idb][irep] = data       

    def process_caldata(self):
        print("job finished")
        print(self.fft_peaks)
        print(self.reject_list)
        # go through FFT peaks and calculate playback resultant dB
        #for freq in self.fft_peaks
        vfunc = np.vectorize(calc_db)
        print("Using FFT peak data from ", self.caldb, " dB, ", self.calf, " Hz tone to calculate calibration curve")
        try:
            ifreq, idb = self.fft_vals_lookup[(self.calf,self.caldb)]
            cal_fft_peak = self.fft_peaks[ifreq][idb]
        except:
            print("using manual 0.224 fft peak")
            cal_fft_peak = CAL_HACK

        resultant_dB = vfunc(self.fft_peaks, self.caldb, cal_fft_peak)

        if SAVE_FFT_DATA:
            filename = FFT_FNAME
            np.save(filename, self.full_fft_data)

            filename = PEAKS_FNAME
            np.save(filename, self.fft_peaks)

            filename = DB_FNAME
            np.save(filename, resultant_dB)
            np.savetxt(filename+".txt", resultant_dB)

            with open(INDEX_FNAME + ".pkl", 'wb') as cfo:
                pickle.dump([self.fft_vals_lookup, self.reject_list], cfo)

            if SAVE_DATA_TRACES:
                filename = DATA_FNAME
                np.save(filename, self.data_traces)

        plot_cal_curve(resultant_dB, self.freqs, self.intensities, self)

        if SAVE_NOISE:
            #noise_vfunc = np.vectorize(calc_noise)
            #noise_array = noise_vfunc(self.full_fft_data,0,2000)
            noise_array = np.zeros((len(self.freqs),len(self.intensities),self.nreps))
            for ifreq in range(len(self.freqs)):
                for idb in range(len(self.intensities)):
                    for irep in range(self.nreps):
                        noise_array[ifreq,idb,irep] = calc_noise(self.full_fft_data[ifreq,idb,irep], 0, 2000)

            np.save(NOISE_FNAME, noise_array)


    def on_stop(self):
        if self.current_operation == 0 : 
            if USE_FINITE:
                self.ui.interval_spnbx.setEnabled(True)
                if self.daq_timer is not None:
                    self.killTimer(self.daq_timer)
                    self.pool.waitForDone()
                else:
                    self.display.killTimer(self.display.timer)
                    
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
            self.ui.tab_2.setEnabled(True)
            self.ui.start_button.setEnabled(True)
            # no need to kill tasks since they will finish in the thread
            self.pool.waitForDone()
            self.aitask = None
            self.aotask = None
        else:
            print("No task currently running")

    def update_stim(self):
        scale_factor = 1000
        time_scale = 1000
        f = self.ui.freq_spnbx.value()*scale_factor
        sr = self.ui.sr_spnbx.value()*scale_factor
        dur = self.ui.dur_spnbx.value()/scale_factor
        db = self.ui.db_spnbx.value()
        rft = self.ui.risefall_spnbx.value()/scale_factor
        aisr =  self.ui.aisr_spnbx.value()*scale_factor

        tone, timevals = make_tone(f,db,dur,rft,sr, self.caldb, self.calv)
        
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

    def process_response(self, f, db):
        try:
            data = self.current_line_data[:]
            sr = self.sr

            # extract information from acquired tone, and save
            freq, spectrum = calc_spectrum(data, sr)

            # take the abs (should I do this?), and get the highest peak
            spectrum = abs(spectrum)

            maxidx = spectrum.argmax(axis=0)
            max_freq = freq[maxidx]
            spec_max = np.amax(spectrum)

            fidx = np.where(freq==f)
            spec_peak_at_f = spectrum[fidx]

            vmax = np.amax(abs(data))

            self.ui.label1.setText("AI Vmax : %.5f" % (np.amax(abs(data))))
            self.ui.label2.setText("FFT peak : %.6f, \t at %d Hz\n" % (np.amax(spectrum), max_freq))
            self.ui.label3.setText("FFT peak at %d kHz : %.6f" % (f/1000, spec_peak_at_f))
            if self.current_operation == 0:
                self.ui.label4.setText("Response dB : %.2f" % (calc_db(spec_peak_at_f, self.caldb, CALHACK)))

            if vmax < 0.1:
                print("WARNING : RESPONSE VOLTAGE BELOW DEVICE FLOOR")
                self.statusBar().showMessage("WARNING : RESPONSE VOLTAGE BELOW DEVICE FLOOR")
            else:
                self.statusBar().showMessage("")

            #tolerance of 1 Hz for frequency matching
            if max_freq < f-1 or max_freq > f+1:
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
                self.curve_data_lock.lock()        
                self.rep_temp.append(spec_max)
                if len(self.rep_temp) == self.nreps:
                    ifreq, idb = self.fft_vals_lookup[(f,db)]
                    self.fft_peaks[ifreq][idb] =  np.mean(self.rep_temp)
                    if VERBOSE:
                        print('\n' + '*'*40)
                        print("Rep values: {}\nRep mean: {}".format(self.rep_temp, np.mean(self.rep_temp)))
                        print('*'*40 + '\n')
                    self.rep_temp = []
                self.curve_data_lock.unlock()

                if SAVE_FFT_DATA:
                    irep = len(self.rep_temp) - 1
                    if irep < 0 :
                        irep = self.nreps - 1 
                    ifreq, idb = self.fft_vals_lookup[(f,db)]
                    self.full_fft_data[ifreq][idb][irep] = spectrum

                    if SAVE_DATA_TRACES: 
                        self.data_traces[ifreq][idb][irep] = data    
        except:
            print("Error processing response data")
            #self.on_stop()
            raise   

    def ai_display(self):
        try:
            f, db = self.fdb
            self.process_response(f,db)
            return
            # if using a scrolling plot, use the leftmost axis lim 
            # to start the time data from, otherwise start from 0
            lims = self.display.axs[1].axis()
            lims = [0]
            # copy data to variable as data structures not synchronized :(
            data = self.current_line_data[:]
        
            t = len(data)/self.aisr
            #xdata = np.arange(lims[0], lims[0]+len(self.current_line_data))
            xdata= np.linspace(lims[0], lims[0]+t, len(data)) #time vals
           
            freq, spectrum = calc_spectrum(data, self.aisr)

            spectrum = abs(spectrum)
            #maxidx = spectrum.argmax(axis=0)
            vmax = np.amax(abs(data))

            
            maxidx = np.where(freq==f)
            max_freq = freq[maxidx]
            spec_max = spectrum[maxidx]

            if VERBOSE:
                #print(maxidx)
                #print("response x range {}, {}".format(xdata[0], xdata[-1]))
                print("%.5f AI V" % (vmax))
                print("%.6f FFT peak, at %d Hz\n" % (spec_max, freq[maxidx]))

            # update labels on GUI with FFT data
            self.ui.label1.setText("AI Vmax : %.5f" % (vmax))
            self.ui.label2.setText("FFT peak : %.6f, \t at %d Hz\n" % (spec_max, freq[maxidx]))

            if vmax < 0.1:
                self.statusBar().showMessage("WARNING : RESPONSE VOLTAGE BELOW DEVICE FLOOR")
            else:
                self.statusBar().showMessage("")

            self.display.draw_line(2,1,freq, spectrum)
            self.display.draw_line(1,0,xdata,data)
                      
        except:
            print("Error drawing line data")
            self.killTimer(self.daq_timer)
            raise

    def timerEvent(self, evt):
        #print("tick")
        if self.current_operation == 0:
            #w = WorkerObj(self.finite_worker)

            #t = QtCore.QThread()     
            #t = ShadowThread() 
            #w.moveToThread(t)
            #w.finished.connect(t.quit)
            #t.started.connect(w.process)
            #t.finished.connect(t.deleteLater)
            #w.finished.connect(t.deleteLater)
            #t.start()
            #self.thread_pool.append(t)
            t  = GenericThread(self.finite_worker)
            #t.start()
            
            #self.thread_pool.append( GenericThread(self.finite_worker) )        
            #self.thread_pool[len(self.thread_pool)-1].start()
            #print("threadpool size {}".format(len(self.thread_pool)))
        elif self.current_operation == 1:

            # if timing is correct and feasible (i.e. interval >= duration), locking 
            # shouldn't strictly be necessesary, but for posterity...
            self.stim_lock.lock()
            if self.work_queue.empty():
                # no more work, quit
                print("outta work")
                self.stim_lock.unlock()
                self.on_stop()
                # or should I emit a signal to execute this?
                print("send to processor")
                self.process_caldata()
                return
            else:
                f, db = self.work_queue.get()
            self.stim_lock.unlock()

            # spawn thread for next item in queue
            t  = GenericThread(self.curve_worker, f, db)
        self.pool.start(t)

    def finite_worker(self):

        # acquire data and reset task to be read for next timer event
        self.daq_lock.lock()
        self.aotask.StartTask()
        self.aitask.StartTask()
        
        # blocking read
        data = self.aitask.read()
        self.current_line_data = data

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

        self.daq_lock.unlock()
        self.stim_lock.unlock()

        #self.emit(QtCore.SIGNAL('ai_display()'))
        f, db = self.fdb
        self.signals.done.emit(f,db)
        
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

    def launch_display_dlg(self):
        field_vals = {'chunksz' : self.ainpts, 'caldb': self.caldb, 'calv': self.calv, 'calf' : self.calf}
        dlg = DisplayDialog(default_vals=field_vals)
        if dlg.exec_():
            ainpts, caldb, calv, calf = dlg.get_values()
            self.ainpts = ainpts
            self.caldb = caldb
            self.calv = calv
            self.calf = calf

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
    done = QtCore.pyqtSignal(int,int)
    curve_finished = QtCore.pyqtSignal()

# the below classes are all attempts to make QThread work according
# to recommendations on 
# http://mayaposch.wordpress.com/2011/11/01/how-to-really-truly-use-qthreads-the-full-explanation/
# see also: http://stackoverflow.com/questions/6783194/background-thread-with-qthread-in-pyqt
class WorkerObj(QtCore.QObject):

    finished = QtCore.pyqtSignal()

    def __init__(self,function, *args, **kwargs):
        QtCore.QObject.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def process(self):
        print("processing...")
        self.function(*self.args,**self.kwargs)


class ShadowThread(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)
    def run(self):
        QtCore.QThread.run(self)

def make_tone(freq,db,dur,risefall,samplerate, caldb, calv):
    # create portable tone generator class that allows the 
    # ability to generate tones that modifyable on-the-fly
    npts = dur * samplerate
    #print("duration (s) :{}".format(dur))
    # equation for db from voltage is db = 20 * log10(V2/V1))
    # 10^(db/20)
    v_at_caldB = calv
    caldB = caldb
    amp = (10 ** ((db-caldB)/DBFACTOR)*v_at_caldB)

    if VERBOSE:
        print("current dB: {}, current frequency: {} kHz, AO Amp: {:.6f}".format(db, freq/1000, amp))
        print("cal dB: {}, V at cal dB: {}".format(caldB, v_at_caldB))

    rf_npts = risefall * samplerate
    #print('amp {}, freq {}, npts {}, rf_npts {}'
    # .format(amp,freq,npts,rf_npts))
    
    tone = amp * np.sin((freq*dur) * np.linspace(0, 2*np.pi, npts))
    #add rise fall
    if risefall > 0:
        tone[:rf_npts] = tone[:rf_npts] * np.linspace(0,1,rf_npts)
        tone[-rf_npts:] = tone[-rf_npts:] * np.linspace(1,0,rf_npts)
        
    timevals = np.arange(npts)/samplerate

    return tone, timevals

def calc_spectrum(signal,rate):
    #calculate complex fft

    # pad with zeros?
    #padded_signal = np.zeros(len(signal*2))
    #padded_signal[:len(signal)] = signal
    #signal = padded_signal
    npts = len(signal)

    freq = np.arange(npts)/(npts/rate)
    freq = freq[:(npts/2)] #single sided

    sp = np.fft.fft(signal)/npts
    sp = sp[:(npts/2)]

    return freq, sp.real

def calc_db(peak, caldB, fft_peak_cal):
    pbdB = DBFACTOR * np.log10(peak/fft_peak_cal) + caldB
    return pbdB

def calc_noise(fft_vector, ix1,ix2):
    fft_slice = fft_vector[ix1:ix2]
    area = trapz(fft_slice)
    return area


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
