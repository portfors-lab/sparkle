import numpy as np

from itertools import islice, count

from sparkle.acq.players import FinitePlayer
from sparkle.run.list_runner import ListAcquisitionRunner
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

            info = {'samplerate_ad': self.player.aifs, 'averaged': self.average,
                    'artifact_reject': self.reject, 'reject_rate': self.rejectrate}
            self.datafile.set_metadata(self.current_dataset_name, info)

        self.player.set_aochan(self.aochan)
        self.player.set_aichan(self.aichan)    

    def _initialize_test(self, test):      
        # override default trace_counter initialization to make space for silence window
        self.trace_counter = -1
          
        if self.save_data:
            recording_length = self.aitimes.shape[0]
            # +1 to trace count for silence window
            if self.average:
                self.datafile.init_data(self.current_dataset_name, 
                                        dims=(test.traceCount()+1, 1, len(self.aichan), recording_length),
                                        mode='finite')
                self.avg_buffer = np.zeros((test.repCount(), len(self.aichan), recording_length))
            else:
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
            if self.average:
                self.avg_buffer[irep, :] = response
                if irep == self.nreps - 1:

                    # Checks if any values are higher than the Artifact Rejection
                    # value for each sample and if so converts to nan
                    if self.reject:
                        # print 'rejectrate:', self.rejectrate
                        for i in islice(count(), self.avg_buffer.shape[0]):
                            for j in islice(count(), self.avg_buffer.shape[2]):
                                if self.avg_buffer[i][0][j] >= self.rejectrate:
                                    self.avg_buffer[i][0][j] = np.nan
                            # print '[', i, ']: ', self.avg_buffer[i][0]

                    avg_response = np.nanmean(self.avg_buffer, axis=0)
                    # print '\navg_response: ', avg_response
                    self.datafile.append(self.current_dataset_name, avg_response)
                    self.avg_buffer = np.zeros_like(self.avg_buffer)  # Zero's out the array
            else:
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
