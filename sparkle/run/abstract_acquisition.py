import threading
import time

import numpy as np


class AbstractAcquisitionRunner(object):
    """Holds state information for an experimental session"""
    def __init__(self, queues):
        self.queues = queues
        self.threshold = None

        self.player = None

        self.datafile = None

        self.caldb = 100
        self.calv = 0.1
        self.calf = 20000
        self.reprate = 2

        self.binsz = 0.005

        self.update_reference_voltage()
        self.set_calibration(None, None, None, None)

        self.player_lock = threading.Lock()
        self.current_dataset_name = None
        self.save_data = False # subclasses may set different defaults
        
    def update_reference_voltage(self):
        """Updates the voltage intensity combination used to calculate
        the appropriate amplitude for outgoing signals. Uses internal
        values to class that may have changed"""
        raise NotImplementedError

    def set_calibration(self, attenuations, freqs, frange, calname):
        """Sets the calibration for all tests controlled by this class.

        :param attenuations: Vector of frequency attenuations in dB.
                            i.e. the frequency response of the system.
        :type attenuations: list or numpy.ndarray
        :param freqs: Matching frequencyes for the attenuation vector
        :type freqs: list or numpy.ndarray
        :param frange: Frequency range (min, max) to restrict the application of the 
                        calibration to (in Hz)
        :type frange: (int, int)
        :param calname: Name of the calibration, for documentation purposes
        :type calname: str
        """
        raise NotImplementedError

    def set_threshold(self, threshold):
        """Spike detection threshold

        :param threshold: electrical potential to determine spikes (V)
        :type threshold: float
        """
        self.threshold = threshold

    def set(self, **kwargs):
        """Sets an internal setting for acquistion, using keywords.

        Available parameters to set: 
        
        :param acqtime: duration of recording (input) window (seconds)
        :type acqtime: float
        :param aifs: sample rate of the recording (input) operation (Hz)
        :type aifs: int
        :param aochan: AO (generation) channel name
        :type aochan: str
        :param aichan: AI (recording) channel name
        :type aichan: str
        :param nreps: number of repetitions for each unique stimulus
        :type nreps: int
        :param binsz: time bin duration for spike sorting (seconds)
        :type binsz: float
        :param caldb: See :meth:`StimulusModel<sparkle.stim.stimulus_model.StimulusModel.setReferenceVoltage>`
        :type caldb: float
        :param calv: See :meth:`StimulusModel<sparkle.stim.stimulus_model.StimulusModel.setReferenceVoltage>`
        :type calv: float
        :param datafile: a reference to an open file to save data to
        :type datafile: :class:`AcquisitionData<sparkle.data.dataobjects.AcquisitionData>`
        """
        self.player_lock.acquire()
        if 'acqtime' in kwargs:
            self.player.set_aidur(kwargs['acqtime'])
        if 'aifs' in kwargs:
            self.player.set_aifs(kwargs['aifs'])
            self.aifs = kwargs['aifs']
        if 'aifs' in kwargs or 'acqtime' in kwargs:
            t = kwargs.get('acqtime', self.player.get_aidur())
            npoints = t*float(kwargs.get('aifs', self.player.get_aifs()))
            self.aitimes = np.linspace(0, t, npoints)
        if 'trigger' in kwargs:
            self.player.set_trigger(kwargs['trigger'])
        self.player_lock.release()

        if 'aochan' in kwargs:
            self.aochan = kwargs['aochan']
        if 'aichan' in kwargs:
            self.aichan = kwargs['aichan']
        if 'binsz' in kwargs:
            self.binsz = kwargs['binsz']
        if 'save' in kwargs:
            self.save_data = kwargs['save']
        if 'caldb' in kwargs:
            self.caldb = kwargs['caldb']
        if 'calv' in kwargs:
            self.calv = kwargs['calv']
        if 'calf' in kwargs:
            self.calf = kwargs['calf']
        if 'caldb' in kwargs or 'calv' in kwargs:
            self.update_reference_voltage()
        if 'datafile' in kwargs:
            self.datafile = kwargs['datafile']
        if 'reprate' in kwargs:
            self.reprate = kwargs['reprate']
        if 'save' in kwargs:
            self.save_data = kwargs['save']

    def run(self, interval, **kwargs):
        """Runs the acquisiton

        :param interval: time between the start of each acquistion sweep (seconds)
        :type interval: float

        """
        raise NotImplementedError

    def halt(self):
        """Stop the current on-going generation/acquisition"""
        self._halt = True

    def interval_wait(self):
        """Pauses the correct amount of time according to this 
        acquisition object's interval setting, and the last time this 
        function was called"""
        # calculate time since last interation and wait to acheive desired interval
        now = time.time()
        elapsed = (now - self.last_tick)*1000
        # print("interval %d, time from start %d \n" % (elapsed, (now - self.start_time)*1000))
        if elapsed < self.interval:
            # print('sleep ', (self.interval-elapsed))
            # self.signals.warning.emit('') # clear previous warning
            time.sleep((self.interval-elapsed)/1000)
            now = time.time()
        elif elapsed > self.interval:
            pass
            # self.signals.warning.emit("WARNING: PROVIDED INTERVAL EXCEEDED, ELAPSED TIME %d" % (elapsed))
        self.last_tick = now

    def putnotify(self, name, *args):
        """Puts data into queue and alerts listeners"""
        # self.signals[name][0].send(*args)
        self.queues[name][0].put(*args)
        self.queues[name][1].set()
