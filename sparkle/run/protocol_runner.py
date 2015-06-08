import numpy as np

from sparkle.acq.players import FinitePlayer
from sparkle.run.list_runner import ListAcquisitionRunner
from sparkle.stim.stimulus_model import StimulusModel
from sparkle.tools import spikestats
from sparkle.tools.util import next_str_num


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
                                    dims=(test.traceCount()+1, test.repCount(), len(self.aichan), recording_length),
                                    mode='finite')
        # check for special condition -- replace this with a generic
        # if test.editor is not None and test.editor.name == "Tuning Curve":
        if test.stimType() == "Tuning Curve":
            frequencies, intensities =  test.autoParamRanges()
            self.putnotify('tuning_curve_started', (list(frequencies), list(intensities), 'tuning'))
        else:
            self.putnotify('tuning_curve_started', (range(test.traceCount()), ['all traces'], 'generic'))
    
    def _process_response(self, response, trace_info, irep):

        if self.save_data:
            self.datafile.append(self.current_dataset_name, response)

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
