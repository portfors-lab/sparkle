import multiprocessing as multip
import os
import platform
import threading

import yaml

from sparkle.acq.daq_tasks import AITask, AITaskFinite, AOTaskFinite, \
    DigitalOutTask

if platform.system() == 'Windows':
    import win32com.client
elif platform.system() == 'Linux':
    pass


PRINT_WARNINGS = False
VERBOSE = True

class AbstractPlayerBase(object):
    """Holds state information for current acquisition/generation task"""
    def __init__(self):

        self.stim = []

        self.ngenerated = 0
        self.nacquired = 0

        self.aitask = None

        # self.tone_lock = threading.Lock()
        # self.daq_lock = threading.Lock()
        self.tone_lock = multip.Lock()
        self.daq_lock = multip.Lock()

        self.aitask = None
        self.aotask = None

        self.stim_changed = False

        self.attenuator = None
        self.connect_attenuator(False)

        self.trigger_src = None #"PCI-6259/port0/line1"  
        self.trigger_dest = None #"/PCI-6259/PFI0"

    def start(self):
        """Abstract, must be implemented by subclass"""
        raise NotImplementedError

    def stop(self):
        """Abstract, must be implemented by subclass"""
        raise NotImplementedError

    def reset_generation(self, trigger):
        """Re-arms the analog output according to current settings

        :param trigger: name of the trigger terminal. ``None`` value means generation begins immediately on run
        :type trigger: str
        """
        self.tone_lock.acquire()

        npts =  self.stim.size
        try:
            self.aotask = AOTaskFinite(self.aochan, self.fs, npts, trigsrc=trigger)
            self.aotask.write(self.stim)
            if self.attenuator is not None:
                self.attenuator.SetAtten(self.atten)
            else:
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

    def set_stim(self, signal, fs, attenuation=0):
        """Sets any vector as the next stimulus to be output. Does not call write to hardware"""

        self.tone_lock.acquire()
        self.stim = signal
        self.fs = fs
        self.atten = attenuation
        self.stim_changed = True

        self.tone_lock.release()


    def get_samplerate(self):
        """The current analog output(generation) samplerate 

        :returns: int -- samplerate (Hz)
        """
        return self.fs

    def get_aidur(self):
        """The current input(recording) window duration 

        :returns: float -- window length (seconds)"""
        return self.aitime

    def get_aifs(self):
        """The current analog input (recording) samplerate 

        :returns: int -- samplerate (Hz)
        """
        return self.aifs

    def set_aifs(self, fs):
        """Sets the current analog input (recording) samplerate 

        :param fs: recording samplerate (Hz)
        :type fs: int
        """
        self.aifs = fs

    def set_aidur(self,dur):
        """Sets the current input(recording) window duration

        :param dur: window length (seconds)
        :type dur: float
        """
        self.aitime = dur

    def set_aochan(self, aochan):
        """Sets the current analog output (generation) channel

        :param aochan: AO channel name
        :type aochan: str
        """
        self.aochan = aochan

    def set_aichan(self, aichan):
        """Sets the current analog input (recording) channel

        :param aichan: AI channel name
        :type aochan: str
        """
        self.aichan = aichan

    def connect_attenuator(self, connect=True):
        """Establish a connection to the TDT PA5 attenuator"""
        if connect:
            try:
                pa5 = win32com.client.Dispatch("PA5.x")
                success = pa5.ConnectPA5('GB', 1)
                if success == 1:
                    print 'Connection to PA5 attenuator established'
                    pass
                else:
                    print 'Connection to PA5 attenuator failed'
                    errmsg = pa5.GetError()
                    print u"Error: ", errmsg
                    raise Exception(u"Attenuator connection failed")
            except:
                print "Error connecting to attenuator"
                pa5 = None

            self.attenuator = pa5
        else:
            # if there is an attenuator, make sure it is set to 0 before disconnecting
            if self.attenuator:
                self.attenuator.setAtten(0)
            self.attenuator = None
        return self.attenuator

    def attenuator_connected(self):
        """Returns whether a connection to the attenuator has been established (bool)"""
        return self.attenuator is not None

    def start_timer(self, reprate):
        """Start the digital output task that serves as the acquistion trigger"""
        print 'starting digital output at rate {} Hz'.format(reprate)
        self.trigger_task = DigitalOutTask(self.trigger_src, reprate)
        self.trigger_task.start()

    def stop_timer(self):
        self.trigger_task.stop()

    def set_trigger(self, trigger):
        self.trigger_dest = trigger

class FinitePlayer(AbstractPlayerBase):
    """For finite generation/acquisition tasks"""
    def __init__(self):
        super(FinitePlayer, self).__init__()

    def start(self):
        """Writes output buffer and settings to device

        :returns: numpy.ndarray -- if the first presentation of a novel stimulus, or None if a repeat stimulus
        """

        # this shouldn't actually be possible still...
        if self.aitask is not None:
            self.stop()
            raise Exception("FIX ME : NESTED START OPERATIONS ALLOWED")

        self.daq_lock.acquire()

        self.ngenerated = 0
        self.nacquired = 0

        return self.reset()

    def run(self):
        """Begins simultaneous generation/acquisition

        :returns: numpy.ndarray -- read samples
        """
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

        response_npts = int(self.aitime*self.aifs)
        try:
            self.aitask = AITaskFinite(self.aichan, self.aifs, response_npts, trigsrc=self.trigger_dest)
            new_gen = self.reset_generation(u"ai/StartTrigger")
        except:
            print u'ERROR! TERMINATE!'
            self.daq_lock.release()
            self.stop()
            raise

        self.daq_lock.release()
        return new_gen

    def stop(self):
        """Halts the acquisition, this must be called before resetting acquisition"""
        try:
            self.aitask.stop()
            self.aotask.stop()
            pass
        except:     
            print u"No task running"
        self.aitask = None
        self.aotask = None


class ContinuousPlayer(AbstractPlayerBase):
    """This is a continuous player for a chart acquitision operation"""
    def __init__(self):
        super(ContinuousPlayer, self).__init__()
        self.on_read = lambda x: x # placeholder

    def start_continuous(self, aichans, update_hz=10):
        """Begins a continuous analog generation, calling a provided function
         at a rate of 10Hz

        :param aichans: name of channel(s) to record (analog input) from
        :type aichans: list<str>
        :param update_hz: Rate (Hz) at which to read data from the device input buffer
        :type update_hz: int
         """
        self.daq_lock.acquire()

        self.ngenerated = 0 # number of stimuli presented during chart run
        npts = int(self.aifs/update_hz) #update display at 10Hz rate
        nchans = len(aichans)
        self.aitask = AITask(aichans, self.aifs, npts*5*nchans)
        self.aitask.register_callback(self._read_continuous, npts)
        self.aitask.start()

    def set_read_function(self, fun):
        """Set the function to be executed for every read from the device buffer

        :param fun: callable which must take a numpy.ndarray as the only positional argument
        :type fun: function
        """
        self.on_read = fun

    def _read_continuous(self, data):
        self.on_read(data)

    def run(self):
        """Executes the stimulus generation, and returns when completed"""
        self.aotask.StartTask()
        self.aotask.wait() # don't return until generation finished
        self.aotask.stop()
        self.aotask = None

    def start(self):
        """Arms the analog output (generation) for the current settings"""
        self.reset()

    def reset(self):
        """Re-arms the analog output (generation) to be preseneted again, for the current settings"""
        try:
            new_gen = self.reset_generation(u"")
        except:
            print u'ERROR! GENERATION FAILED!'
            # self.stop()
            raise
        return new_gen

    def stop(self):
        """Halts the analog output task"""
        try:
            self.aotask.stop()
        except:     
            print u"No task running"
        self.aotask = None

    def stop_all(self):
        """Halts both the analog output and input tasks"""
        if self.aotask is not None:
            self.aotask.stop()
        self.aitask.stop()
        self.daq_lock.release()
        self.aitask = None
        self.aotask = None

    def generation_count(self):
        """Number of stimulus presentations

        :returns: int -- number of analog output events
        """
        #not safe
        return self.ngenerated
