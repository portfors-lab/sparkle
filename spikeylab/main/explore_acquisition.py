import time
import threading

import numpy as np

from spikeylab.io.players import FinitePlayer
from spikeylab.main.abstract_acquisition import AbstractAcquisitionModel
from spikeylab.stim.stimulusmodel import StimulusModel
from spikeylab.tools.util import increment_title
from spikeylab.tools import spikestats

class Explorer(AbstractAcquisitionModel):
    def __init__(self):
        super(Explorer, self).__init__()

        self.player = FinitePlayer()
        self.save_data = False
        self.set_name = 'explore_0'

        self.stimulus = StimulusModel()

        stimuli_types = get_stimuli_models()
        self._explore_stimuli = [x() for x in stimuli_types if x.explore]

        self.current_genrate = self.stimulus.samplerate()

    def stimuli_list(self):
        return self._explore_stimuli

    def set_calibration(self, attenuations, freqs, frange):
        self.stimulus.set_calibration(attenuations, freqs, frange)

    def update_reference_voltage(self):
        self.stimulus.setReferenceVoltage(self.caldb, self.calv)

    def set_params(self, **kwargs):
        super(Explorer, self).set_params(**kwargs)

    def set_stim_by_index(self, index):
        # remove any current components
        self.stimulus.clearComponents()
        self.stimulus.insertComponent(self.explore_stimuli[index])
        self.current_genrate = self.stimulus.samplerate()
        signal, atten, overload = self.stimulus.signal()
        self.player.set_stim(signal, self.stimulus.samplerate(), attenuation=atten)
        return signal

    def current_signal(self):
        return self.stimulus.signal()

    def stim_names(self):
        stim_names = []
        for stim in self.explore_stimuli:
            stim_names.append(stim.name)
        return stim_names

    def run(self, interval):
        self._halt = False
        
        # TODO: some error checking to make sure valid paramenters are set
        if self.save_explore:
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
        self.player.start()

        # and go!
        self.acq_thread.start()

        return self.acq_thread

    def _worker(self):
        spike_counts = []
        spike_latencies = []
        spike_rates = []
        self.irep = 0
        times = self.aitimes
        while not self._halt:
            # print 'explore worker'
            try:
                self.interval_wait()

                response = self.player.run()
                
                self.signals.response_collected.emit(times, response)

                # process response; calculate spike times
                spike_times = spikestats.spike_times(response, self.threshold, self.finite_player.aisr)
                spike_counts.append(len(spike_times))
                if len(spike_times) > 0:
                    spike_latencies.append(spike_times[0])
                else:
                    spike_latencies.append(np.nan)
                spike_rates.append(spikestats.firing_rate(spike_times, self.finite_player.aitime))

                response_bins = spikestats.bin_spikes(spike_times, self.binsz)
                self.signals.spikes_found.emit(response_bins, self.irep)

                #lock it so we don't get a times mismatch
                self.player_lock.acquire()
                self.player.reset()
                times = self.aitimes
                self.player_lock.release()

                if self.save_data:
                    # save response data
                    self.save_data(response)

                self.irep +=1
                if self.irep == self.nreps:
                    total_spikes = float(sum(spike_counts))
                    avg_count = total_spikes/len(spike_counts)
                    avg_latency = sum(spike_latencies)/len(spike_latencies)
                    avg_rate = sum(spike_rates)/len(spike_rates)
                    self.irep = 0
                    self.signals.trace_finished.emit(total_spikes, avg_count, avg_latency, avg_rate)
                    spike_counts = []
                    spike_latencies = []
                    spike_rates = []

            except:
                raise

        self.player.stop()
        if self.save_data:
            self.datafile.trim(self.current_dataset_name)

    def save_data(self, data):
        self.datafile.append(self.current_dataset_name, data)
        # save stimulu info
        info = self.stimulus.doc()
        info['samplerate_ad'] = self.finite_player.aisr
        self.datafile.append_trace_info(self.current_dataset_name, info)