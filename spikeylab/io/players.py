import threading
import Queue
import platform
if platform.system() == 'Windows':
    import win32com.client
elif platform.system() == 'Linux':
    pass

from spikeylab.io.daq_tasks import AITaskFinite, AOTaskFinite, AITask

PRINT_WARNINGS = False
VERBOSE = True

class PlayerBase():
    """Holds state information for current acquisition/generation task"""
    def __init__(self):

        self.stim = []

        self.ngenerated = 0
        self.nacquired = 0

        self.aitask = None

        self.tone_lock = threading.Lock()
        self.daq_lock = threading.Lock()

        self.aitask = None
        self.aotask = None

        self.maxv = 5 #Volts

        self.stim_changed = False

        self.connect_attenuator()        

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def reset_generation(self, trigger):
        self.tone_lock.acquire()

        npts =  self.stim.size
        try:
            self.aotask = AOTaskFinite(self.aochan, self.sr, npts, trigsrc=trigger)
            self.aotask.write(self.stim)
            try:
                self.attenuator.SetAtten(self.atten)
            except:
                # print "ERROR: attenuation not set!"
                pass
                # raise

            self.ngenerated +=1
            if self.stim_changed:
                new_gen = self.stim
            else:
                new_gen = None
            self.stim_changed = False

        except:
            print u'ERROR! TERMINATE!'
            self.tone_lock.release()
            raise

        self.tone_lock.release()
        return new_gen

    def set_stim(self, signal, sr, attenuation=0):
        """Sets any vector as the next stimulus to be output. Does not call write to hardware"""
        
        # in the interest of not blowing out the speakers I am going to set this to 5?
        if max(abs(signal)) > self.maxv:
            print("WARNING: OUTPUT VOLTAGE {:.2f} EXCEEDS MAXIMUM({}V), RECALULATING".format(max(abs(signal)), self.maxv))
            signal = signal/max(abs(signal))*self.maxv

        self.tone_lock.acquire()
        self.stim = signal
        self.sr = sr
        self.atten = attenuation
        self.stim_changed = True

        self.tone_lock.release()


    def get_samplerate(self):
        return self.sr

    def get_aidur(self):
        return self.aitime

    def get_aisr(self):
        return self.aisr

    def set_aisr(self, aisr):
        self.aisr = aisr

    def set_aidur(self,dur):
        self.aitime = dur

    def set_aochan(self, aochan):
        self.aochan = aochan

    def set_aichan(self, aichan):
        self.aichan = aichan

    def set_maxv(self, v):
        return
        self.maxv = v

    def connect_attenuator(self):
        # establish connection to the attenuator
        try:
            pa5 = win32com.client.Dispatch("PA5.x")
            success = pa5.ConnectPA5('GB', 1)
            if success == 1:
                print 'Connection to PA5 attenuator established'
            else:
                print 'Connection to PA5 attenuator failed'
                errmsg = pa5.GetError()
                print u"Error: ", errmsg
                raise Exception(u"Attenuator connection failed")
        except:
            print "Error connecting to attenuator"
            pa5 = None

        self.attenuator = pa5
        
        return self.attenuator

    def attenuator_connected(self):
        return self.attenuator is not None

class FinitePlayer(PlayerBase):
    """For finite generation/acquisition tasks"""
    def __init__(self):
        PlayerBase.__init__(self)

    def start(self):
        """Write output buffer and settings to device"""

        # this shouldn't actually be possible still...
        if self.aitask is not None:
            self.stop()
            raise Exception("FIX ME : NESTED START OPERATIONS ALLOWED")

        self.daq_lock.acquire()

        self.ngenerated = 0
        self.nacquired = 0

        return self.reset()

    def run(self):
        """Begin simultaneous generation/acquisition, returns read samples"""
        try:
            if self.aotask is None:
                print u"You must arm the calibration first"
                return
            # acquire data and stop task, lock must have been release by
            # previous reset
            self.daq_lock.acquire()
            self.aotask.StartTask()
            self.aitask.StartTask()

            # blocking read
            data = self.aitask.read()

            # write task should always be shorter than read
            # self.aotask.WaitUntilTaskDone(10)

            self.nacquired += 1
            
            self.aitask.stop()
            self.aotask.stop()
            
        except:
            print u'ERROR! TERMINATE!'
            self.daq_lock.release()
            self.stop()
            raise

        return data

    def reset(self):
        """Rearms the gen/acq task, to the same channels as before"""

        response_npts = int(self.aitime*self.aisr)
        try:
            self.aitask = AITaskFinite(self.aichan, self.aisr, response_npts)
            new_gen = self.reset_generation(u"ai/StartTrigger")
        except:
            print u'ERROR! TERMINATE!'
            self.daq_lock.release()
            self.stop()
            raise

        self.daq_lock.release()
        return new_gen

    def stop(self):
        try:
            self.aitask.stop()
            self.aotask.stop()
        except:     
            print u"No task running"
        self.aitask = None
        self.aotask = None


class ContinuousPlayer(PlayerBase):
    """This is a continuous player for a chart acquitision operation"""
    def __init__(self):
        PlayerBase.__init__(self)
        self.on_read = lambda x: x # placeholder

    def start_continuous(self, aichans, update_hz=10):
        """Begins a continuous analog generation, calling a provided function
         at a rate of 10Hz"""
        self.daq_lock.acquire()

        self.ngenerated = 0 # number of stimuli presented during chart run
        npts = int(self.aisr/update_hz) #update display at 10Hz rate
        nchans = len(aichans)
        self.aitask = AITask(aichans, self.aisr, npts*5*nchans)
        self.aitask.register_callback(self._read_continuous, npts)
        self.aitask.start()

    def set_read_function(self, fun):
        self.on_read = fun

    def _read_continuous(self, task):
        inbuffer = task.read().squeeze()
        self.on_read(inbuffer)

    def run(self):
        self.aotask.StartTask()
        self.aotask.wait() # don't return until generation finished
        self.aotask.stop()
        self.aotask = None

    def start(self):
        self.reset()

    def reset(self):
        try:
            new_gen = self.reset_generation(u"")
        except:
            print u'ERROR! GENERATION FAILED!'
            # self.stop()
            raise
        return new_gen

    def stop(self):
        try:
            self.aotask.stop()
        except:     
            print u"No task running"
        self.aotask = None

    def stop_all(self):
        if self.aotask is not None:
            self.aotask.stop()
        self.aitask.stop()
        self.daq_lock.release()
        self.aitask = None
        self.aotask = None

    def generation_count(self):
        #not safe
        return self.ngenerated