import logging
import threading
import time

import numpy as np

from sparkle.run.abstract_acquisition import AbstractAcquisitionRunner
from sparkle.run.protocol_model import ProtocolTabelModel


class Broken(Exception): pass

class ListAcquisitionRunner(AbstractAcquisitionRunner):
    """Provides a common interface and some facilitatory functions for
    the presentation of data with a pre-determined order"""
    def __init__(self, *args):
        self.protocol_model = ProtocolTabelModel()

        super(ListAcquisitionRunner, self).__init__(*args)
        
        self.silence_window = False

    def set_calibration(self, attenuations, freqs, frange, calname):
        """See :meth:`AbstractAcquisitionRunner<sparkle.run.abstract_acquisition.AbstractAcquisitionRunner.set_calibration>`"""
        self.protocol_model.setCalibration(attenuations, freqs, frange)
        self.calname = calname
        self.cal_frange = frange

    def update_reference_voltage(self):
        """See :meth:`AbstractAcquisitionRunner<sparkle.run.abstract_acquisition.AbstractAcquisitionRunner.update_reference_voltage>`"""
        self.protocol_model.setReferenceVoltage(self.caldb, self.calv)

    def count(self):
        """Total number of all tests/traces/reps currently in this protocol

        :returns: int -- the total
        """
        total = 0
        for test in self.protocol_model.allTests():
            total += test.traceCount()*test.loopCount()*test.repCount() + test.repCount()
        return total

    def max_reps(self):
        all_reps = [] 
        for test in self.protocol_model.allTests():
            all_reps.append(test.repCount())
        return max(all_reps)

    def setup(self, interval):
        """Prepares the tests for execution, interval in ms"""
        self.trace_counter = 0

        self._halt = False
        self.interval = interval

    def run(self):
        """Runs the acquisiton"""
        self._initialize_run()

        stimuli = self.protocol_model.allTests()

        self.acq_thread = threading.Thread(target=self._worker, 
                                           args=(stimuli,), )
        # save the current calibration to data file doc        
        if self.save_data:
            info = {'calibration_used': self.calname, 'calibration_range': self.cal_frange}
            self.datafile.set_metadata(self.current_dataset_name, info)

        # save the start time and set last tick to expired, so first
        # acquisition loop iteration executes immediately
        self.start_time = time.time()
        self.last_tick = self.start_time - (self.interval/1000)

        self.acq_thread.start()
        return self.acq_thread
 
    def _initialize_run(self):
        """ This needs to set up data structures """
        # should set the current_dataset_name
        # Any settings that the player should have
        raise NotImplementedError

    def _worker(self, stimuli):
        t0 = time.time()
        starttime = t0
        timecollection = []
        try:
            logger = logging.getLogger('main')
            # self.player.start_timer(self.reprate)
            # incase of early abortion...
            itest = 0
            itrace = -1
            irep = 0
            try:
                for itest, test in enumerate(stimuli):
                    # pull out signal from stim model
                    test.setReferenceVoltage(self.caldb, self.calv)

                    self._initialize_test(test)
                    if self.save_data:
                        self.datafile.set_metadata(self.current_dataset_name, test.testDoc(), signal=True)
                    # profiler = cProfile.Profile()
                    # print 'profiling....'
                    # profiler.enable()
                    # traces, docs, overs = self._cached_stims[itest]
                    traces, docs, overs = test.expandedStim()
                    # profiler.disable()
                    # print 'finished profiling'
                    # profiler.dump_stats('stim_gen_cal.profile')
                    nreps = test.repCount()
                    self.nreps = test.repCount() # not sure I like this
                    # print 'profiling....'
                    # profiler.enable()
                    fs = test.samplerate()
                    if self.silence_window:
                        self.player.set_stim(np.array([0., 0.]), fs, 0)
                        trace_doc = {'samplerate_da':fs, 'components': [{'start_s':0, 'index':(0,0),
                        'stim_type':'silence', 'duration':0, 'risefall':0, 'intensity':0}], 'overloaded_attenuation':0}
                        itrace = -1
                        self.putnotify('stim_generated', (np.array([0, 0]), fs))
                        self.putnotify('current_trace', (itest,itrace,trace_doc))
                        self.putnotify('over_voltage', (0,))
                

                        stamps = []
                        self.player.start()
                        for irep in range(nreps):
                            self.interval_wait()  
                            if self._halt:
                                raise Broken
                            response = self.player.run()
                            stamps.append(time.time())
                            self._process_response(response, trace_doc, irep)
                            if test.stimType() == 'Tuning Curve':
                                extra_info = {'f': -1, 'db': 80}
                            else:
                                extra_info = {'all traces': True}
                            self.putnotify('response_collected', (self.aitimes, response, itest, -1, irep, extra_info))

                            # print 'size of response len: {} bytes: {}'.format(len(response), response.nbytes)
                            self.putnotify('current_rep', (irep,))
                            self.player.reset()

                        trace_doc['time_stamps'] = stamps
                        if self.save_data:
                            self.datafile.append_trace_info(self.current_dataset_name, trace_doc)
                        self.player.stop()
                    for itrace, (trace, trace_doc, over) in enumerate(zip(traces, docs, overs)):
                        
                        signal, atten = trace
                        # t1 = time.time()
                        self.player.set_stim(signal, fs, atten)
                        # print 'player start time {:.3f}'.format(time.time()-t1)

                        stamps = []
                        self.player.start()
                        for irep in range(nreps):
                            self.interval_wait()
                            if self._halt:
                                raise Broken
                            elapsed = time.time()-t0
                            # print 'down time {:.3f}'.format(elapsed),
                            # timecollection.append(elapsed)
                            response = self.player.run()
                            s = time.time()
                            oldt = t0
                            t0=time.time()
                            looplen = t0 - oldt
                            self.player.reset()
                            # print 'reset time {:.3f}'.format(time.time()-s)
                            # print 'loop duration {:.3f}'.format(looplen)
                            timecollection.append(looplen)
                            stamps.append(s)

                            if test.stimType() == 'Tuning Curve':
                                f = trace_doc['components'][0]['frequency']
                                db = trace_doc['components'][0]['intensity']
                                extra_info = {'f': f, 'db': db}
                            else:
                                extra_info = {'all traces': True}
                            
                            self.putnotify('response_collected', (self.aitimes, response, itest, itrace, irep, extra_info))
                            self._process_response(response, trace_doc, irep)

                            if irep == 0:
                                self.putnotify('stim_generated', (signal, fs))
                                self.putnotify('current_trace', (itest,itrace,trace_doc))
                                self.putnotify('over_voltage', (over,))
                            self.putnotify('current_rep', (irep,))
                            
                        # not getting saved:
                        trace_doc['time_stamps'] = stamps
                        if self.save_data:
                            self.datafile.append_trace_info(self.current_dataset_name, trace_doc)
                        self.player.stop()

                    # log as well, test type and user tag will be the same across traces
                    # logger.info("Finished test type: {}, tag: {}".format(trace_doc['testtype'], trace_doc['user_tag']))
                    # profiler.disable()
                    # print 'finished profiling'
                    # profiler.dump_stats('test_run.profile')
            except Broken:
                # save some abortion message
                if self.save_data:
                    self.datafile.set_metadata(self.current_dataset_name, {'aborted': 'test {}, trace {}, rep {}'.format(itest+1, itrace+1, irep+1)})
                self.player.stop()

            # self.player.stop_timer()
            if self.save_data:
                self.datafile.backup(self.current_dataset_name)
            self.putnotify('group_finished', (self._halt,))
        except:
            logger.exception("Uncaught Exception from Acq Thread: ")

        # print 'all elapsed', timecollection
        tc = np.array(timecollection[1:])
        print 'deadlines missed {}/{}'.format(len(tc[tc > (1./self.reprate)+0.01]), len(tc))

    def clear_child_process(self):
        del self.acq_thread
        
    def _initialize_test(self, test):
        raise NotImplementedError

    def _process_response(self, test):
        raise NotImplementedError
