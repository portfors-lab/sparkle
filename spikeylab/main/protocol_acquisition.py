import time
import threading
import logging

from spikeylab.main.abstract_acquisition import AbstractAcquisitionModel
from spikeylab.main.protocol_model import ProtocolTabelModel
import cProfile

class Broken(Exception): pass

class Experimenter(AbstractAcquisitionModel):
    def __init__(self, signals):
        self.protocol_model = ProtocolTabelModel()

        AbstractAcquisitionModel.__init__(self, signals)

    def set_calibration(self, attenuations, freqs, frange, calname):
        self.protocol_model.setCalibration(attenuations, freqs, frange)
        self.calname = calname
        self.cal_frange = frange

    def update_reference_voltage(self):
        self.protocol_model.setReferenceVoltage(self.caldb, self.calv)

    def count(self):
        """Total number of all tests/traces/reps currently in this protocol"""
        total = 0
        for test in self.protocol_model.stimulusList():
            total += test.traceCount()*test.loopCount()*test.repCount()
        return total

    def setup(self, interval):
        self.trace_counter = 0

        self._halt = False

        setname = self._initialize_run()

        # save the current calibration to data file doc
        info = {'calibration_used': self.calname, 'calibration_range': self.cal_frange}
        self.datafile.set_metadata(self.current_dataset_name, info)

        # save the start time and set last tick to expired, so first
        # acquisition loop iteration executes immediately
        self.start_time = time.time()
        self.last_tick = self.start_time - (interval/1000)
        self.interval = interval

        stimuli = self.protocol_model.stimulusList()

        self.acq_thread = threading.Thread(target=self._worker, 
                                           args=(stimuli,))

        # go through and get any overloads, this is not efficient since
        # I am going to be calculating the signals again later, so stash?
        # undesired_attenuations = [stim.expandedStim()[2] for stim in stimuli]
        undesired_attenuations = [[0]]
        return undesired_attenuations

    def run(self):
        self.acq_thread.start()

        return self.acq_thread

    def _initialize_run(self):
        """ This needs to set up data structures """
        raise NotImplementedError

    def _worker(self, stimuli):
        try:
            try:
                for itest, test in enumerate(stimuli):
                    # pull out signal from stim model
                    test.setReferenceVoltage(self.caldb, self.calv)

                    self._initialize_test(test)
                    profiler = cProfile.Profile()
                    # print 'profiling....'
                    # profiler.enable()
                    traces, docs, overs = test.expandedStim()
                    # profiler.disable()
                    # print 'finished profiling'
                    # profiler.dump_stats('stim_gen_cal.profile')
                    nreps = test.repCount()
                    self.nreps = test.repCount() # not sure I like this
                    # print 'profiling....'
                    # profiler.enable()
                    for itrace, (trace, trace_doc, over) in enumerate(zip(traces, docs, overs)):
                        signal, atten = trace
                        self.player.set_stim(signal, test.samplerate(), atten)

                        stamps = []
                        self.player.start()
                        for irep in range(nreps):
                            self.interval_wait()
                            if self._halt:
                                raise Broken
                            response = self.player.run()
                            stamps.append(time.time())
                            self._process_response(response, trace_doc, irep)
                            if irep == 0:
                                # do this after collection so plots match details
                                self.signals.stim_generated.emit(signal, test.samplerate())
                                self.signals.current_trace.emit(itest,itrace,trace_doc)
                                self.signals.over_voltage.emit(over)
                            
                            self.signals.current_rep.emit(irep)

                            self.player.reset()
                            
                        trace_doc['time_stamps'] = stamps
                        self.datafile.append_trace_info(self.current_dataset_name, trace_doc)
                        self.player.stop()
                    # profiler.disable()
                    # print 'finished profiling'
                    # profiler.dump_stats('test_run.profile')
            except Broken:
                # save some abortion message
                self.player.stop()
                
            self.datafile.close_data(self.current_dataset_name)
            self.signals.group_finished.emit(self._halt)
        except:
            logger = logging.getLogger('main')
            logger.exception("Uncaught Exception from Acq Thread:")

    def _initialize_test(self, test):
        raise NotImplementedError

    def _process_response(self, test):
        raise NotImplementedError