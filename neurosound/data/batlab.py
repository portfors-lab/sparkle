import logging
import re

import numpy as np

from neurosound.data.acqdata import AcquisitionData
from neurosound.tools.exceptions import DataIndexError, DisallowedFilemodeError, \
                                        ReadOnlyError, OverwriteFileError
from neurosound.tools.util import convert2native, max_str_num
from ParsePST import parse_pst
from ExtractRawData import extract_raw_data

class BatlabData(AcquisitionData):
    def __init__(self, filename, user='unknown', filemode='r'):
        super(BatlabData, self).__init__(filename, user, filemode)

        # Batlab data is read only
        if filemode != 'r':
            raise ReadOnlyError(filename)

        # these data formats are as close to the MATLAB structure as possible
        experiment_data = parse_pst(filename + '.pst')
        self.raw_data = extract_raw_data(filename + '.raw', experiment_data)

        # reformat metadata to match neurosound
        self.info = batlab2neurosound(experiment_data)

        self.tests = []
        # reshape into single test list with each test represented by a single numpy array
        for itest, test in enumerate(self.raw_data):
            shape = (len(test), test[0].shape[0], test[0].shape[1])
            testdata = np.zeros(shape)
            testdata = NamedArray(testdata, 'test_{}'.format(itest+1))
            for itrace, trace in enumerate(test):
                # aborted tests will be short on traces, leave these as zeros to make data shapes work
                testdata[itrace,:trace.shape[0],:] = trace[:]
            self.tests.append(testdata)


        logger = logging.getLogger('main')
        logger.info('Opened data file %s' % filename)

    def close(self):
        pass

    def get(self, key, index=None):
        # data is [test][trace][reps, samples] -- [list][list][numpy array]
        match = re.search('test_(\d+)(/trace_(\d+))?', key)
        if match is not None:
            testno = int(match.group(1))
            traceno = match.group(3)

            if traceno is None:
                # get entire test
                # 1 indexed, so substract 1
                if index is None:
                    return self.tests[testno -1]
                else:
                    return test.tests[testno -1][index]
            else:
                traceno = int(traceno)
                if index is None:
                    return self.raw_data[testno-1][traceno-1]
                else:
                    return self.raw_data[testno-1][traceno-1][index]

    def get_info(self, key):
        return self.info[key]

    def get_trace_info(self, key):
        return self.info[key]['stim']

    def calibration_list(self):
        return []

    def all_datasets(self):
        return self.tests
        
    def keys(self):
        return self.info.keys()

class NamedArray(np.ndarray):
    def __new__(cls, input_array, name):
        obj = np.asarray(input_array).view(cls)
        obj.name = name
        return obj

def batlab2neurosound(experiment_data):
    """NeuroSound expects meta data to have a certain heirarchial organization,
    reformat batlab experiment data to fit. 
    """
    # This is mostly for convention.. attribute that matters most is samplerate, 
    # since it is used in the GUI to calculate things like duration
    nsdata = {}
    for attr in ['computername', 'pst_filename', 'title', 'who', 'date', 'program_date']:
        nsdata[attr] = experiment_data[attr]
    for itest, test in enumerate(experiment_data['test']):
        setname = 'test_{}'.format(itest+1)
        nsdata[setname] = {}
        nsdata[setname]['samplerate_ad'] = test['trace'][0]['samplerate_ad']
        nsdata[setname]['comment'] = test['comment']
        nsdata[setname]['start'] = test['time']
        nsdata[setname]['mode'] = 'finite'
        nsdata[setname]['user_tag'] = ''

        if test['full_testtype'] == 'General Auto Test' and test['testtype'] == 'tone':
            print 'General Auto Test', test['testtype']
            nsdata[setname]['testtype'] = 'Tuning Curve'
        else:
            nsdata[setname]['testtype'] = test['full_testtype']

        stims = []
        for itrace, trace in enumerate(test['trace']):
            try:
                stim = {'samplerate_da': trace['samplerate_da'],
                        'overloaded_attenuation': 0,}
                components = []
                for icomp, component in enumerate(trace['stimulus']):
                    # always add in silence component to match batlab's delay parameter
                    delay_comp = {'index': [icomp, 0], 'stim_type': 'silence', 
                            'intensity': 0, 'duration': component['delay']/1000., 
                            'start_s': 0, 'risefall': 0}
                    components.append(delay_comp)
                    # FIXME need to pull in speaker calibration to get real intensity
                    comp = {'risefall' : component['rise_fall']/1000., 
                            'index': [icomp, 1], 
                            'duration': component['duration']/1000.,
                            'start_s': component['delay']/1000.,
                            'intensity': 100 - component['attenuation']}
                    if component['soundtype_name'] == 'vocalization':
                        # print component
                        comp['stim_type'] = 'Vocalization'
                        comp['filename'] = component['vocal_call_file']
                        comp['browsedir'] = ''
                    elif component['soundtype_name'] == 'fmsweep':
                        comp['stim_type'] = 'FM Sweep'
                        usweep = 1 if component['usweep'] else -1
                        comp['start_f'] = component['frequency'] - (component['bandwidth']/2)*usweep
                        comp['stop_f'] = component['frequency'] + (component['bandwidth']/2)*usweep
                    elif component['soundtype_name'] == 'tone':
                        comp['stim_type'] = 'Pure Tone'
                        comp['frequency'] = component['frequency']
                    else:
                        print 'FOUND UNKNOWN STIM', component['soundtype_name']
                        raise ValueError
                    components.append(comp)
                stim['components'] = components
                stims.append(stim)
            except TypeError:
                print 'PROBLEM with', itest, itrace
                print 'component', component
                continue

        nsdata[setname]['stim'] = stims

    return nsdata