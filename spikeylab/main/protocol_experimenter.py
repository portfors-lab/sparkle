import numpy as np

from spikeylab.main.protocol_acquisition import Experimenter
from spikeylab.tools import spikestats
from spikeylab.tools.util import increment_title
from spikeylab.io.players import FinitePlayer

class ProtocolExperimenter(Experimenter):
    def __init__(self, signals):
        Experimenter.__init__(self, signals)

        save_data = True
        self.group_name = 'segment_0'
        self.player = FinitePlayer()

    def _initialize_run(self):
        self.current_dataset_name = self.group_name
        self.datafile.init_group(self.current_dataset_name)
        self.group_name = increment_title(self.group_name)

        info = {'samplerate_ad': self.player.aisr}
        self.datafile.set_metadata(self.current_dataset_name, info)

        self.player.set_aochan(self.aochan)
        self.player.set_aichan(self.aichan)

    def _initialize_test(self, test):
        recording_length = self.aitimes.shape[0]
        self.datafile.init_data(self.current_dataset_name, 
                                dims=(test.traceCount(), test.repCount(), recording_length),
                                mode='finite')
        # check for special condition -- replace this with a generic
        if test.editor is not None and test.editor.name == "Tuning Curve":
            frequencies, intensities =  test.autoParamRanges()
            self.signals.tuning_curve_started.emit(list(frequencies), list(intensities), 'tuning')
        elif test.traceCount() > 1:
            self.signals.tuning_curve_started.emit(range(test.traceCount()), [0], 'generic')

    def _process_response(self, response, trace_info, irep):
        if irep == 0:
            spike_counts = []
            spike_latencies = []
            spike_rates = []
        else:
            spike_counts = self.spike_counts
            spike_latencies = self.spike_latencies
            spike_rates = self.spike_rates

        self.signals.response_collected.emit(self.aitimes, response)

        # process response; calculate spike times
        spike_times = spikestats.spike_times(response, self.threshold, self.player.aisr)
        spike_counts.append(len(spike_times))
        if len(spike_times) > 0:
            spike_latencies.append(spike_times[0])
        else:
            spike_latencies.append(np.nan)
        spike_rates.append(spikestats.firing_rate(spike_times, self.player.aitime))

        response_bins = spikestats.bin_spikes(spike_times, self.binsz)
        self.signals.spikes_found.emit(response_bins, irep)

        self.datafile.append(self.current_dataset_name, response)

        if irep == self.nreps-1:
            total_spikes = float(sum(spike_counts))
            avg_count = total_spikes/len(spike_counts)
            avg_latency = sum(spike_latencies)/len(spike_latencies)
            avg_rate = sum(spike_rates)/len(spike_rates)
            self.signals.trace_finished.emit(total_spikes, avg_count, avg_latency, avg_rate)
            if trace_info['testtype'] == 'Tuning Curve':
                f = trace_info['components'][0]['frequency']
                db = trace_info['components'][0]['intensity']
                self.signals.tuning_curve_response.emit(f, db, avg_count)
            else:
                self.signals.tuning_curve_response.emit(self.trace_counter, 0, avg_count)
            self.trace_counter +=1

        self.spike_counts = spike_counts
        self.spike_latencies = spike_latencies
        self.spike_rates = spike_rates

    def clear(self):
        self.protocol_model.clearTests()