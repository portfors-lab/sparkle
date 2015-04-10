"""Converts Batlab format .pst and .raw files into Sparkly HDF5 format. Note
that is NOT the same as loading Batlab data into a Sparkly data object, 
i.e. :class:`BatlabData<sparkle.data.batlabdata.BatlabData>`."""

import json

import h5py

from ExtractRawData import extract_raw_data
from ParsePST import parse_pst


def convert_file(filename):
    # filename of the pst and raw files, without the extenstion. Assumes co-located files with the same name.
    experiment_data = parse_pst(filename + '.pst')
    raw_data = extract_raw_data(filename + '.raw', experiment_data)
    bat2h5(raw_data, experiment_data)

def bat2h5(rawdata, experiment_data):
    filename = experiment_data['pst_filename'].split('.')[0] + '.hdf5'
    print 'creating', filename
    try:
        h5file = h5py.File(filename, 'w')
        for attr in ['computername', 'pst_filename', 'title', 'who', 'date', 'program_date']:
            h5file.attrs[attr] = experiment_data[attr]
        for itest, test in enumerate(experiment_data['test']):
            segment_name = 'segment_{}'.format(itest+1)
            h5file.create_group(segment_name)
            # samplerate can't change between traces, can it?
            h5file[segment_name].attrs['samplerate_ad'] = test['trace'][0]['samplerate_ad']
            h5file[segment_name].attrs['comment'] = test['comment']

            testdata = rawdata[itest]
            # recording window size and samplerate same for all traces, so we can gather into 3-d array
            ntraces = len(testdata)
            nreps, nsamples = testdata[0].shape
            setname = 'test_{}'.format(itest+1)
            # print 'creating dataset', setname, (ntraces, nreps, nsamples)
            h5file[segment_name].create_dataset(setname, (ntraces, nreps, nsamples))
            h5file[segment_name][setname].attrs['start'] = test['time']
            h5file[segment_name][setname].attrs['mode'] = 'finite'
            h5file[segment_name][setname].attrs['user_tag'] = ''
            if test['full_testtype'] == 'General Auto Test' and test['testtype'] == 'tone':
                print 'General Auto Test', test['testtype']
                h5file[segment_name][setname].attrs['testtype'] = 'Tuning Curve'
            else:
                h5file[segment_name][setname].attrs['testtype'] = test['full_testtype']
                
            stims = []
            for itrace, trace in enumerate(test['trace']):
                try:
                    # print 'trace', itrace, testdata[itrace].shape
                    h5file[segment_name][setname][itrace,:,:] = testdata[itrace]
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
            h5file[segment_name][setname].attrs['stim'] = json.dumps(stims)         
        return h5file
    except:
        h5file.close()
        raise


if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    convert_file(filename)
