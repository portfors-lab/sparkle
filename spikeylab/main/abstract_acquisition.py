import time
import threading

import numpy as np

class AbstractAcquisitionModel():
    """Holds state information for an experimental session"""
    def __init__(self, signals):
        self.signals = signals
        self.threshold = None

        self.player = None

        self.datafile = None

        self.caldb = 100
        self.calv = 0.1
        self.calf = 20000

        self.binsz = 0.005

        self.update_reference_voltage()
        self.set_calibration(None, None, None)

        self.player_lock = threading.Lock()

    def update_reference_voltage(self):
        raise NotImplementedError

    def set_calibration(self, attenuations, freqs, frange):
        raise NotImplementedError

    def set_threshold(self, threshold):
        """Spike detection threshold

        :param threshold: electrical potential to determine spikes (V)
        :type threshold: float
        """
        self.threshold = threshold

    def set_params(self, **kwargs):
        self.player_lock.acquire()
        if 'acqtime' in kwargs:
            self.player.set_aidur(kwargs['acqtime'])
        if 'aisr' in kwargs:
            self.player.set_aisr(kwargs['aisr'])
        if 'aisr' in kwargs or 'acqtime' in kwargs:
            t = kwargs.get('acqtime', self.player.get_aidur())
            npoints = t*float(kwargs.get('aisr', self.player.get_aisr()))
            self.aitimes = np.linspace(0, t, npoints)
        self.player_lock.release()

        if 'aochan' in kwargs:
            self.aochan = kwargs['aochan']
        if 'aichan' in kwargs:
            self.aichan = kwargs['aichan']
        if 'nreps' in kwargs:
            self.nreps = kwargs['nreps']
            self.irep = 0
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

    def run(self, interval, **kwargs):
        raise NotImplementedError

    def halt(self):
        """Stop the current on-going generation/acquisition"""
        self._halt = True

    def interval_wait(self):
        # calculate time since last interation and wait to acheive desired interval
        now = time.time()
        elapsed = (now - self.last_tick)*1000
        #print("interval %d, time from start %d \n" % (elapsed, (now - self.start_time)*1000))
        if elapsed < self.interval:
            #print('sleep ', (self.interval-elapsed))
            self.signals.warning.emit('') # clear previous warning
            time.sleep((self.interval-elapsed)/1000)
            now = time.time()
        elif elapsed > self.interval:
            self.signals.warning.emit("WARNING: PROVIDED INTERVAL EXCEEDED, ELAPSED TIME %d" % (elapsed))
        self.last_tick = now

    def save_data(self, data, setname):
        self.datafile.append(setname, data)
        # save stimulu info
        info = self.stimulus.doc()
        info['samplerate_ad'] = self.player.aisr
        self.datafile.append_trace_info(setname, info)


    # def setup_relay(self, foriegn_signal):
    #     self.signals.response_collected.connect(foriegn_signal.response_collected.emit)
    #     self.signals.calibration_response_collected.connect(foriegn_signal.calibration_response_collected.emit)
    #     self.signals.average_response.connect(foriegn_signal.average_response.emit)
    #     self.signals.spikes_found.connect(foriegn_signal.spikes_found.emit)
    #     self.signals.trace_finished.connect(foriegn_signal.trace_finished.emit)
    #     self.signals.stim_generated.connect(foriegn_signal.stim_generated.emit)
    #     self.signals.warning.connect(foriegn_signal.warning.emit)
    #     self.signals.ncollected.connect(foriegn_signal.ncollected.emit)
    #     self.signals.current_trace.connect(foriegn_signal.current_trace.emit)
    #     self.signals.current_rep.connect(foriegn_signal.current_rep.emit)
    #     self.signals.group_finished.connect(foriegn_signal.group_finished.emit)
    #     self.signals.samplerateChanged.connect(foriegn_signal.samplerateChanged.emit)
    #     self.signals.calibration_file_changed.connect(foriegn_signal.calibration_file_changed.emit)
    #     self.signals.tuning_curve_started.connect(foriegn_signal.tuning_curve_started.emit)
    #     self.signals.tuning_curve_response.connect(foriegn_signal.tuning_curve_response.emit)