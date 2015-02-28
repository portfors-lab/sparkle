import time
import threading
import logging

import numpy as np

from spikeylab.acq.players import FinitePlayer
from spikeylab.run.abstract_acquisition import AbstractAcquisitionRunner
from spikeylab.stim.stimulus_model import StimulusModel
from spikeylab.tools.util import increment_title
from spikeylab.tools import spikestats

class SearchRunner(AbstractAcquisitionRunner):
    """Handles the presentation of data where changes are allowed to
    be made to the stimulus while running"""
    def __init__(self, *args):
        self._stimulus = StimulusModel()

        super(SearchRunner, self).__init__(*args)

        self.player = FinitePlayer()
        self.save_data = False
        self.set_name = 'explore_1'

        # stimuli_types = get_stimuli_models()
        # self._explore_stimuli = [x() for x in stimuli_types if x.explore]

        # self.delay = Silence()
        # self._stimulus.insertfComponent(self.delay)

    def stimulus(self):
        """Gets a list of all the stimuli this runner has access to. Order
        of the list matches the index order which stimuli can be set by.

        :returns: (subclasses of) list<:class:`AbstractStimulusComponent<spikeylab.stim.abstract_component.AbstractStimulusComponent>`>
        """
        return self._stimulus

    def set_calibration(self, attenuations, freqs, frange, calname):
        """See :meth:`AbstractAcquisitionRunner<spikeylab.run.abstract_acquisition.AbstractAcquisitionRunner.set_calibration>`"""
        self._stimulus.setCalibration(attenuations, freqs, frange)

    def update_reference_voltage(self):
        """See :meth:`AbstractAcquisitionRunner<spikeylab.run.abstract_acquisition.AbstractAcquisitionRunner.update_reference_voltage>`"""
        self._stimulus.setReferenceVoltage(self.caldb, self.calv)

    # def set_delay(self, duration):
    #     self.delay.setDuration(duration)

    # def set_stim_by_index(self, index):
    #     """Sets the stimulus to be generated to the one referenced by index

    #     :param index: index number of stimulus to set from this class's internal list of stimuli
    #     :type index: int
    #     """
    #     # remove any current components
    #     self._stimulus.clearComponents()
    #     self._stimulus.insertComponent(self.delay)
    #     self._stimulus.insertComponent(self._explore_stimuli[index], 0, 1)
    #     signal, atten, overload = self._stimulus.signal()
    #     self.player.set_stim(signal, self._stimulus.samplerate(), attenuation=atten)
    #     self.putnotify('over_voltage', (overload,))
    #     return signal, overload

    def reset_stim(self):
        signal, atten, overload = self._stimulus.signal()
        self.player.set_stim(signal, self._stimulus.samplerate(), attenuation=atten)
        self.putnotify('over_voltage', (overload,))
        self.nreps = self._stimulus.repCount()
        self.irep = 0
        return signal, overload

    def set_current_stim_parameter(self, param, val):
        """Sets a parameter on the current stimulus

        :param param: name of the parameter of the stimulus to set
        :type param: str
        :param val: new value to set the parameter to
        """
        component = self._stimulus.component(0,1)
        component.set(param, val)

    def current_signal(self):
        """Signal of the currently set stimulus

        :returns: numpy.ndarray
        """
        return self._stimulus.signal()

    # def stim_names(self):
    #     """The names of the all the stimuli this class can generate, in order

    #     :returns: list<str>
    #     """
    #     stim_names = []
    #     for stim in self._explore_stimuli:
    #         stim_names.append(stim.name)
    #     return stim_names

    def run(self, interval):
        """See :meth:`AbstractAcquisitionRunner<spikeylab.run.abstract_acquisition.AbstractAcquisitionRunner.run>`"""
        self._halt = False
        
        # TODO: some error checking to make sure valid paramenters are set
        if self.save_data:
            # initize data set
            self.current_dataset_name = self.set_name
            self.datafile.init_data(self.current_dataset_name, self.aitimes.shape, mode='open')
            self.set_name = increment_title(self.set_name)

        # save the start time and set last tick to expired, so first
        # acquisition loop iteration executes immediately
        self.start_time = time.time()
        self.last_tick = self.start_time - (interval/1000)
        self.interval = interval
        self.acq_thread = threading.Thread(target=self._worker)

        # arm the first read
        self.player.set_aochan(self.aochan)
        self.player.set_aichan(self.aichan)

        # and go!
        self.acq_thread.start()

        return self.acq_thread

    def _worker(self):
        try:
            spike_counts = []
            spike_latencies = []
            spike_rates = []
            self.irep = 0
            times = self.aitimes
            # report inital stim
            trace_doc = self._stimulus.componentDoc()
            trace_doc['overloaded_attenuation'] = np.nan
            self.putnotify('current_trace', (0,0,trace_doc))

            # self.player.start_timer(self.reprate)
            stim = self.player.start()
            while not self._halt:
                # print 'explore worker'
                self.interval_wait()

                response = self.player.run()
                stamp = time.time()

                response = response*self.response_polarity
                self.putnotify('response_collected', (times, response))
                if stim is not None:
                    self.putnotify('stim_generated', (stim, self.player.get_samplerate()))
                    trace_doc = self._stimulus.componentDoc()
                    trace_doc['overloaded_attenuation'] = np.nan
                    self.putnotify('current_trace', (0,0,trace_doc))
                
                # process response; calculate spike times
                spike_times = spikestats.spike_times(response, self.threshold, self.player.aisr)
                spike_counts.append(len(spike_times))
                if len(spike_times) > 0:
                    spike_latencies.append(spike_times[0])
                else:
                    spike_latencies.append(np.nan)
                spike_rates.append(spikestats.firing_rate(spike_times, self.player.aitime))

                # produces erroneous results if threshold is None (this is 
                # the case in cal toner, but we don't really care then)
                response_bins = spikestats.bin_spikes(spike_times, self.binsz)
                self.putnotify('spikes_found', (response_bins, self.irep))

                #lock it so we don't get a times mismatch
                self.player_lock.acquire()
                stim = self.player.reset()
                times = self.aitimes
                self.player_lock.release()

                if self.save_data:
                    # save response data
                    self.save_to_file(response, stamp)

                self.irep +=1
                if self.irep == self.nreps:
                    total_spikes = float(sum(spike_counts))
                    avg_count = total_spikes/len(spike_counts)
                    avg_latency = sum(spike_latencies)/len(spike_latencies)
                    avg_rate = sum(spike_rates)/len(spike_rates)
                    self.irep = 0
                    self.putnotify('trace_finished', (total_spikes, avg_count, avg_latency, avg_rate))
                    
                    spike_counts = []
                    spike_latencies = []
                    spike_rates = []

            self.player.stop()
            # self.player.stop_timer()
            if self.save_data:
                self.datafile.trim(self.current_dataset_name)

        except:
            logger = logging.getLogger('main')
            logger.exception("Uncaught Exception from Explore Thread:")

    def save_to_file(self, data, stamp):
        """Saves data to current dataset.

        :param data: data to save to file
        :type data: numpy.ndarray
        :param stamp: time stamp of when the data was acquired
        :type stamp: str
        """
        self.datafile.append(self.current_dataset_name, data)
        # save stimulu info
        info = dict(self._stimulus.componentDoc().items() + self._stimulus.testDoc().items())
        print 'saving doc', info
        info['time_stamps'] = [stamp]
        info['samplerate_ad'] = self.player.aisr
        self.datafile.append_trace_info(self.current_dataset_name, info)