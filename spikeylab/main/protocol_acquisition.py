import time
import threading

from spikeylab.main.abstract_acquisition import AbstractAcquisitionModel
from spikeylab.main.protocol_model import ProtocolTabelModel

class Broken(Exception): pass

class Experimenter(AbstractAcquisitionModel):
    def __init__(self, signals):
        self.protocol_model = ProtocolTabelModel()

        AbstractAcquisitionModel.__init__(self, signals)

    def set_calibration(self, attenuations, freqs, frange):
        self.protocol_model.setCalibration(attenuations, freqs, frange)
        
    def update_reference_voltage(self):
        self.protocol_model.setReferenceVoltage(self.caldb, self.calv)

    def run(self, interval):
        setname = self._initialize_run()

        self._halt = False

        # save the start time and set last tick to expired, so first
        # acquisition loop iteration executes immediately
        self.start_time = time.time()
        self.last_tick = self.start_time - (interval/1000)
        self.interval = interval

        stimuli = self.protocol_model.stimulusList()
        self.trace_counter = 0

        self.acq_thread = threading.Thread(target=self._worker, 
                                           args=(stimuli,))
        self.acq_thread.start()

        return self.acq_thread

    def _initialize_run(self):
        """ This needs to set up data structures """
        raise NotImplementedError

    def _worker(self, stimuli):
        try:
            for itest, test in enumerate(stimuli):
                # pull out signal from stim model
                test.setReferenceVoltage(self.caldb, self.calv)
                self._initialize_test(test)

                traces, doc = test.expandedStim()
                nreps = test.repCount()
                self.nreps = test.repCount() # not sure I like this
                for itrace, (trace, trace_doc) in enumerate(zip(traces, doc)):
                    signal, atten = trace
                    self.player.set_stim(signal, test.samplerate(), atten)

                    self.player.start()
                    for irep in range(nreps):
                        self.interval_wait()
                        if self._halt:
                            raise Broken
                        response = self.player.run()
                        self._process_response(response, trace_doc, irep)
                        if irep == 0:
                            # do this after collection so plots match details
                            self.signals.stim_generated.emit(signal, test.samplerate())
                            self.signals.current_trace.emit(itest,itrace,trace_doc)
                        self.signals.current_rep.emit(irep)

                        self.player.reset()
                    # always save protocol response
                    self.datafile.append_trace_info(self.current_dataset_name, trace_doc)

                    self.player.stop()
        except Broken:
            # save some abortion message
            self.player.stop()

        self.signals.group_finished.emit(self._halt)

    def _initialize_test(self, test):
        raise NotImplementedError

    def _process_response(self, test):
        raise NotImplementedError