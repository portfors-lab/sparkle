"""This file is as close to a direct translation of ExtractRawData.m as possible. 
If you are trying to access Batlab data, make sure you don't a 
:meth:`sparkly version<sparkle.data.open.open_acqdata>` instead.
"""

import numpy as np

def extract_raw_data(filename, experiment_data, test_nums=None, trace_nums=[]):

    if test_nums is None:
        test_nums = range(len(experiment_data['test']))

    # % Author specified flags
    normalize_raw_data = False;
    remove_mean_raw_data = True;

    with open(filename, 'rb') as fid:
        raw_data = []

        for test_num in test_nums:
            raw_data.append([])
            test = experiment_data['test'][test_num]
            offset_in_raw_file = test['offset_in_raw_file']

            traces = test['trace']
            if len(trace_nums) == 0 or max(trace_nums) > len(traces):
                traces_2_process = range(len(traces))
            else:
                traces_2_process = trace_nums

            for trace_num in traces_2_process:
                trace = traces[trace_num]
                sample_rate = trace['samplerate_ad']
                num_sweeps = trace['num_samples']
                record_duration_per_run = trace['record_duration']
                samples_per_trace = int((record_duration_per_run / 1000.) * sample_rate)

                # %Rewind the file
                fid.seek(0, 0)
                # print 'seeking to', offset_in_raw_file+((trace_num)*(samples_per_trace*num_sweeps)*2)
                fid.seek(offset_in_raw_file+((trace_num)*(samples_per_trace*num_sweeps)*2), 0)
                # %Read the raw data segment from the monolithic binary file
                trace_data = np.fromfile(fid, count=(samples_per_trace * num_sweeps), dtype=np.int16).reshape((num_sweeps, samples_per_trace)).astype(np.float64)
                if remove_mean_raw_data:
                    trace_data = trace_data - np.tile(np.mean(trace_data, axis=1).reshape(num_sweeps, 1), samples_per_trace)
                if normalize_raw_data:
                    trace_data = trace_data/np.amax(np.amax(np.abs(trace_data)));
                else:
                    trace_data = trace_data/2**15;
                raw_data[test_num].append(trace_data);
                trace['raw_data_samples'] = trace_data.shape[0];

    return raw_data

if __name__ == '__main__':
    from ParsePST import parse_pst

    # experiment_data = parse_pst('C:/Users/Leeloo/testdata/Mouse 497/Mouse497.pst')
    # raw_data = extract_raw_data('C:/Users/Leeloo/testdata/Mouse 497/Mouse497.raw', experiment_data)

    experiment_data = parse_pst('C:/Users/Leeloo/testdata/August 5 2010/August 5 2010.pst')
    raw_data = extract_raw_data('C:/Users/Leeloo/testdata/August 5 2010/August 5 2010.raw', experiment_data)

    experiment_data = parse_pst('C:/Users/Leeloo/testdata/Mouse 739/Mouse 739.pst')
    raw_data = extract_raw_data('C:/Users/Leeloo/testdata/Mouse 739/Mouse 739.raw', experiment_data)
