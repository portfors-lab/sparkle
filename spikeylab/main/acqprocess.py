import multiprocessing
import numpy as np
import time
import gc

from spikeylab.acq.players import FinitePlayer
class Broken(Exception): pass


def getscience(queues, stimuli, reprate, aifs, aidur, aichan, aochan):

    npoints = aidur*float(aifs)
    aitimes = np.linspace(0, aidur, npoints)
    t0 = time.time()
    starttime = t0
    timecollection = []
    try:
        player = FinitePlayer()
        player.set_aisr(aifs)
        player.set_aidur(aidur)
        player.set_aochan(aochan)
        player.set_aichan(aichan)

        cached_stims = [stim.expandedStim() for stim in stimuli]
        # logger = logging.getLogger('main')
        gc.disable()
        player.start_timer(reprate)
        try:
            print 'process!'
            for itest, test in enumerate(stimuli):
                # pull out signal from stim model

                _initialize_test(test, queues)

                traces, docs, overs = cached_stims[itest]
                nreps = test.repCount()

                fs = test.samplerate()
                if True:
                    player.set_stim(np.array([0., 0.]), fs, 0)
                    trace_doc = {'samplerate_da':fs, 'reps': nreps, 'user_tag': test.userTag(),
                    'calv': test.calv, 'caldb':test.caldb, 'components': [{'start_s':0, 
                    'stim_type':'Control Silence', 'duration':0}],
                    'testtype': 'control', 'overloaded_attenuation':0}
                    itrace = -1
                    down_the_shute(queues, 'stim_generated', (np.array([0]), fs))
                    down_the_shute(queues, 'current_trace', (itest,itrace,trace_doc))
                    down_the_shute(queues, 'over_voltage', (0,))
            
                    stamps = []
                    player.start()
                    for irep in range(nreps):
                        # self.interval_wait()  
                        if False:
                            raise Broken
                        response = player.run()
                        stamps.append(time.time())
                        # self._process_response(response, trace_doc, irep)
                        
                        # print 'size of response len: {} bytes: {}'.format(len(response), response.nbytes)
                        down_the_shute(queues, 'response_collected', (aitimes, response))
                        down_the_shute(queues, 'current_rep', (irep,))
                        player.reset()

                    trace_doc['time_stamps'] = stamps
                    # self.datafile.append_trace_info(self.current_dataset_name, trace_doc)
                    player.stop()

                for itrace, (trace, trace_doc, over) in enumerate(zip(traces, docs, overs)):
                    signal, atten = trace

                    # t1 = time.time()
                    player.set_stim(signal, fs, atten)
                    # prplayer start time {:.3f}'.format(time.time()-t1)

                    stamps = []
                    player.start()
                    for irep in range(nreps):
                        # self.interval_wait()
                        if False:
                            raise Broken
                        elapsed = time.time()-t0
                        print 'down time {:.3f}'.format(elapsed)
                        # timecollection.append(elapsed)
                        response = player.run()
                        s = time.time()
                        oldt = t0
                        t0=time.time()
                        looplen = t0 - oldt
                        player.reset()
                        time.sleep(0.001)
                        # print 'reset time {:.3f}'.format(time.time()-s)
                        print 'loop duration {:.3f}'.format(looplen)
                        timecollection.append(looplen)

                        stamps.append(time.time())
                        down_the_shute(queues, 'response_collected', (aitimes, response))
                        if irep == 0:
                            down_the_shute(queues, 'stim_generated', (signal, fs))
                            down_the_shute(queues, 'current_trace', (itest,itrace,trace_doc))
                            down_the_shute(queues, 'over_voltage', (over,))
                        down_the_shute(queues, 'current_rep', (irep,))
                        
                    trace_doc['time_stamps'] = stamps
                    # self.datafile.append_trace_info(self.current_dataset_name, trace_doc)
                    player.stop()

                # log as well, test type and user tag will be the same across traces
                # logger.info("Finished test type: {}, tag: {}".format(trace_doc['testtype'], trace_doc['user_tag']))
        except Broken:
            # save some abortion message
            player.stop()

        player.stop_timer()
        # self.datafile.close_data(self.current_dataset_name)
        down_the_shute(queues, 'group_finished', (False,))
        gc.enable()
    except:
        raise
        # logger.exception("Uncaught Exception from Acq Thread: ")

    # print 'all elapsed', timecollection
    tc = np.array(timecollection[1:])
    print 'deadlines missed {}/{}'.format(len(tc[tc > (1./reprate)+0.005]), len(tc))

def _initialize_test(test, queues):
    # recording_length = self.aitimes.shape[0]
    # +1 to trace count for silence window
    # self.datafile.init_data(self.current_dataset_name, 
    #                         dims=(test.traceCount()+1, test.repCount(), recording_length),
    #                         mode='finite')
    # check for special condition -- replace this with a generic
    # if test.editor is not None and test.editor.name == "Tuning Curve":
    if test.stimType() == "Tuning Curve":
        frequencies, intensities =  test.autoParamRanges()
        down_the_shute(queues, 'tuning_curve_started', (list(frequencies), list(intensities), 'tuning'))
    elif test.traceCount() > 1:
        down_the_shute(queues, 'tuning_curve_started', (range(test.traceCount()), [0], 'generic'))

def down_the_shute(queues, name, *args):
    # self.signals[name][0].send(*args)
    queues[name][0].put(*args)
    queues[name][1].set()

class AcqProcess(multiprocessing.Process):
    def __init__(self, queues, stimuli, reprate, aifs, aidur, aichan, aochan):
        multiprocessing.Process.__init__(self)
        self.queues = queues
        self.stimuli = stimuli
        self.reprate = reprate
        npoints = aidur*float(aifs)
        aitimes = np.linspace(0, aidur, npoints)
        player = FinitePlayer()
        player.set_aisr(aifs)
        player.set_aidur(aidur)
        player.set_aochan(aochan)
        player.set_aichan(aichan)
        self.player = player
        self.aitimes = aitimes

    def run(self):
        t0 = time.time()
        starttime = t0
        timecollection = []
        try:
            cached_stims = [stim.expandedStim() for stim in self.stimuli]
            # logger = logging.getLogger('main')
            gc.disable()
            self.player.start_timer(self.reprate)
            try:
                for itest, test in enumerate(self.stimuli):
                    # pull out signal from stim model

                    _initialize_test(test, self.queues)

                    traces, docs, overs = cached_stims[itest]
                    nreps = test.repCount()

                    fs = test.samplerate()
                    if True:
                        self.player.set_stim(np.array([0., 0.]), fs, 0)
                        trace_doc = {'samplerate_da':fs, 'reps': nreps, 'user_tag': test.userTag(),
                        'calv': test.calv, 'caldb':test.caldb, 'components': [{'start_s':0, 
                        'stim_type':'Control Silence', 'duration':0}],
                        'testtype': 'control', 'overloaded_attenuation':0}
                        itrace = -1
                        down_the_shute(self.queues, 'stim_generated', (np.array([0]), fs))
                        down_the_shute(self.queues, 'current_trace', (itest,itrace,trace_doc))
                        down_the_shute(self.queues, 'over_voltage', (0,))
                
                        stamps = []
                        self.player.start()
                        for irep in range(nreps):
                            # self.interval_wait()  
                            if False:
                                raise Broken
                            response = self.player.run()
                            stamps.append(time.time())
                            # self._process_response(response, trace_doc, irep)
                            
                            # print 'size of response len: {} bytes: {}'.format(len(response), response.nbytes)
                            down_the_shute(self.queues, 'response_collected', (self.aitimes, response))
                            down_the_shute(self.queues, 'current_rep', (irep,))
                            self.player.reset()

                        trace_doc['time_stamps'] = stamps
                        # self.datafile.append_trace_info(self.current_dataset_name, trace_doc)
                        self.player.stop()

                    for itrace, (trace, trace_doc, over) in enumerate(zip(traces, docs, overs)):
                        signal, atten = trace

                        # t1 = time.time()
                        self.player.set_stim(signal, fs, atten)
                        # prplayer start time {:.3f}'.format(time.time()-t1)

                        stamps = []
                        self.player.start()
                        for irep in range(nreps):
                            # self.interval_wait()
                            if False:
                                raise Broken
                            elapsed = time.time()-t0
                            print 'down time {:.3f}'.format(elapsed)
                            # timecollection.append(elapsed)
                            response = self.player.run()
                            s = time.time()
                            oldt = t0
                            t0=time.time()
                            looplen = t0 - oldt
                            self.player.reset()
                            time.sleep(0.001)
                            # print 'reset time {:.3f}'.format(time.time()-s)
                            print 'loop duration {:.3f}'.format(looplen)
                            timecollection.append(looplen)

                            stamps.append(time.time())
                            down_the_shute(self.queues, 'response_collected', (self.aitimes, response))
                            if irep == 0:
                                down_the_shute(self.queues, 'stim_generated', (signal, fs))
                                down_the_shute(self.queues, 'current_trace', (itest,itrace,trace_doc))
                                down_the_shute(self.queues, 'over_voltage', (over,))
                            down_the_shute(self.queues, 'current_rep', (irep,))
                            
                        trace_doc['time_stamps'] = stamps
                        # self.datafile.append_trace_info(self.current_dataset_name, trace_doc)
                        self.player.stop()

                    # log as well, test type and user tag will be the same across traces
                    # logger.info("Finished test type: {}, tag: {}".format(trace_doc['testtype'], trace_doc['user_tag']))
            except Broken:
                # save some abortion message
                self.player.stop()

            self.player.stop_timer()
            # self.datafile.close_data(self.current_dataset_name)
            down_the_shute(self.queues, 'group_finished', (False,))
            gc.enable()
        except:
            raise
            # logger.exception("Uncaught Exception from Acq Thread: ")

        # print 'all elapsed', timecollection
        tc = np.array(timecollection[1:])
        print 'deadlines missed {}/{}'.format(len(tc[tc > (1./self.reprate)+0.005]), len(tc))
