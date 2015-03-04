import numpy as np

from neurosound.run.list_runner import ListAcquisitionRunner
from neurosound.tools import spikestats
from neurosound.tools.util import next_str_num
from neurosound.acq.players import FinitePlayer
from neurosound.stim.stimulus_model import StimulusModel

class ProtocolRunner(ListAcquisitionRunner):
    """Handles the presentation of data for an experimental protocol"""
    def __init__(self, *args):
        super(ProtocolRunner, self).__init__(*args)

        self.save_data = True
        self.group_name = 'segment_'
        self.player = FinitePlayer()

        self.silence_window = True

    def _initialize_run(self):
        if self.save_data:
            data_items = self.datafile.keys()
            self.current_dataset_name = next_str_num(self.group_name, data_items)

            self.datafile.init_group(self.current_dataset_name)

            info = {'samplerate_ad': self.player.aifs}
            self.datafile.set_metadata(self.current_dataset_name, info)

        self.player.set_aochan(self.aochan)
        self.player.set_aichan(self.aichan)    

    def _initialize_test(self, test):      
        # override defualt trace_counter intialization to make space for silence window
        self.trace_counter = -1
          
        if self.save_data:
            recording_length = self.aitimes.shape[0]
            # +1 to trace count for silence window
            self.datafile.init_data(self.current_dataset_name, 
                                    dims=(test.traceCount()+1, test.repCount(), recording_length),
                                    mode='finite')
        # check for special condition -- replace this with a generic
        # if test.editor is not None and test.editor.name == "Tuning Curve":
        self.current_test_type = test.stimType()
        if test.stimType() == "Tuning Curve":
            frequencies, intensities =  test.autoParamRanges()
            self.putnotify('tuning_curve_started', (list(frequencies), list(intensities), 'tuning'))
        else:
            self.putnotify('tuning_curve_started', (range(test.traceCount()), ['all traces'], 'generic'))
    
    def _process_response(self, response, trace_info, irep):
        if irep == 0:
            spike_counts = []
            spike_latencies = []
            spike_rates = []
        else:
            spike_counts = self.spike_counts
            spike_latencies = self.spike_latencies
            spike_rates = self.spike_rates

        # invert polarity affects spike counting, but saves original polarity to file
        self.putnotify('response_collected', (self.aitimes, response))

        # process response; calculate spike times
        spike_times = spikestats.spike_times(response, self.threshold, self.player.aifs)
        spike_counts.append(len(spike_times))
        if len(spike_times) > 0:
            spike_latencies.append(spike_times[0])
        else:
            spike_latencies.append(np.nan)
        spike_rates.append(spikestats.firing_rate(spike_times, self.player.aitime))

        response_bins = spikestats.bin_spikes(spike_times, self.binsz)
        self.putnotify('spikes_found', (response_bins, irep))

        if self.save_data:
            self.datafile.append(self.current_dataset_name, response)

        if irep == self.nreps-1:
            total_spikes = float(sum(spike_counts))
            avg_count = total_spikes/len(spike_counts)
            avg_latency = sum(spike_latencies)/len(spike_latencies)
            avg_rate = sum(spike_rates)/len(spike_rates)
            self.putnotify('trace_finished', (total_spikes, avg_count, avg_latency, avg_rate))
            if self.current_test_type == 'Tuning Curve' and trace_info['components'][0]['stim_type'] != 'silence':
                f = trace_info['components'][0]['frequency']
                db = trace_info['components'][0]['intensity']
                self.putnotify('tuning_curve_response', (f, db, avg_count))
            else:
                self.putnotify('tuning_curve_response', (self.trace_counter, 'all traces', avg_count))
            self.trace_counter +=1

        self.spike_counts = spike_counts
        self.spike_latencies = spike_latencies
        self.spike_rates = spike_rates

    def set_comment(self, cellid, comment):
        """Saves the provided comment to the current dataset.

        :param cellid: number of the current cell
        :type cellid: int
        :param comment: a message to add documentation to data
        :type comment: str
        """
        info = {'cellid': cellid, 'comment': comment}
        self.datafile.set_metadata(self.current_dataset_name, info)

    def clear(self):
        """Clears all tests from protocol list"""
        self.protocol_model.clear()
