"""This file is as close to a direct translation of ParsePST.m as possible. 
If you are trying to access Batlab data, make sure you don't a 
:meth:`sparkly version<sparkle.data.open.open_acqdata>` instead.
"""

import re


def parse_pst(filename):

    # just go ahead and read the whole file in one go
    with open(filename) as fh:
        file_contents = fh.read()

    # windows adds carriage returns in addition to newlines
    file_contents = file_contents.translate(None, '\r')
    lines = file_contents.split('\n')
    # print lines

    # %Static strings
    test_aborted = 'Test aborted.'
    end_id = 'End of ID information'
    end_test_parameters = 'End of test parameters'
    end_spike_data = 'End of spike data'
    end_auto_test = 'End of auto test'

    test_types = ['tone',
                  'fmsweep',
                  'synthesized_batsound',
                  'amsound',
                  'broad_band_noise',
                  'narrow_band_noise',
                  'click',
                  'vocalization',
                  'high_pass_noise',
                  'low_pass_noise',
                  'sine_wave_modulation',
                  'square_wave_modulation']

    # %Indicates the current line being read.
    line_num = 1
    # %Total lines in the PST file
    num_lines = len(lines)
    # %Offset into the raw data file
    raw_pos = 0

    # %Collect experiment-wide data from ID section
    experiment = {}
    experiment['pst_filename'] = lines[0];
    experiment['date'] = lines[1];
    experiment['title'] = lines[2];
    experiment['who'] = lines[3];
    experiment['computername'] = lines[4];
    experiment['program_date'] = lines[5];
    experiment['test'] = []

    # discard rest of ID section
    line_num = lines.index(end_id) + 1

    while line_num < num_lines-1:
        # %Get the test type
        test = {}
        full_testtype = lines[line_num];
        line_num += 1;
        # %Get the test number.
        # test_line = textscan(lines{line_num},'%n %*s %*s %*n %s',1);
        match = re.match('(\d+) (.*)', lines[line_num])
        test['testnum'] = int(match.group(1))
        test['time'] = match.group(2)
        # %This is the Batlab assigned test type, not the test type that Bat2Matlab uses
        test['full_testtype'] = full_testtype
        # %Store the beginning location of the test
        line_num += 1

        # %Extract the test paramewters
        num_traces = int(re.match('\d+', lines[line_num]).group(0))
        line_num += 1

        # %Scan past the test parameter section
        line_num = lines.index(end_test_parameters) + 1
        lines[line_num-1] = ''

        # %Get the position of the beginning of the test in the raw data file
        test['offset_in_raw_file'] = raw_pos
        
        test['trace'] = []
        for trace_num in range(num_traces):
            trace_data = [int(x) for x in lines[line_num].split()]
            num_sweeps = trace_data[0]
            samplerate_da = trace_data[1];
            samplerate_ad = trace_data[3];
            duration = trace_data[4];
            points = int((samplerate_ad/1000.)*duration)
            trace = {}
            trace['record_duration'] = duration
            trace['samplerate_da'] = samplerate_da
            trace['samplerate_ad'] = samplerate_ad
            trace['num_samples'] = num_sweeps
            # %The length of the trace in the raw data file
            trace_raw_data_length = points*num_sweeps*2
            # %Store the trace raw offset and length
            trace['offset_in_raw_file'] = raw_pos
            trace['length_in_raw_file'] = trace_raw_data_length
            # %Increment the position in the raw data file
            raw_pos += trace_raw_data_length

            test_num = len(experiment['test'])
             # %Collect the stimulus parameters for all 4 channels
            stimulus_num = 0;
            test_stim_type = 0; #%Default
            stim = []
            for channel_num in range(4):
                stimulus, stim_type = parse_pst_stimulus(lines[line_num - 1 + 5*channel_num],test_num,trace_num);
                if len(stimulus) != 0: #%&& stim_type ~= 5 %FIXME. Not adding BBN stimulus
                    stimulus_num += 1
                    stim.append(stimulus)
                    if test_stim_type == 0:
                        test_stim_type = stim_type
            trace['stimulus'] = stim

            # %Set the test type based on the stimulus variety
            if test_stim_type == 0:
                test_type = 'control'

            elif test_stim_type ==1:
                if stimulus_num == 1: test_type = 'tone'
                elif stimulus_num == 2: test_type = 'twotone'
                elif stimulus_num == 3: test_type = 'threetone'
                elif stimulus_num == 4: test_type = 'fourtone'
            else:
                test_type = test_types[test_stim_type]

            test['testtype'] = test_type
            if test_stim_type > 0:
                trace['is_control'] = 0
            else:
                trace['is_control'] = 1

            line_num = lines.index(end_spike_data) + 1
            lines[line_num-1] = ''

            test['trace'].append(trace)

        # %Assert that the spike data terminates with an end auto test statement
        if lines[line_num] != end_auto_test:
            raise Exception('No end of auto test found after spike data');
        line_num += 1;  

        # %Get the test comment
        test['comment'] = lines[line_num]      
        line_num += 1;  

        experiment['test'].append(test)
    return experiment

def parse_pst_stimulus(stim_text, test_num, trace_num):
    # print stim_text
    stim_data = stim_text.split()
    # print 'stim_data', stim_data

    if len(stim_data) == 0 or int(stim_data[0]) == 0:
        return [], 0

    stim_type = int(stim_data[1])
    stimulus = {}
    stimulus['attenuation'] = float(stim_data[2])
    stimulus['duration'] = float(stim_data[3])
    stimulus['delay'] = float(stim_data[4])

    # %Static stimulus labels
    stim_types = ['tone',
              'fmsweep',
              'synthesized_batsound',
              'amsound',
              'broad_band_noise',
              'narrow_band_noise',
              'click',
              'stored_vocal_call',
              'high_pass_noise',
              'low_pass_noise',
              'sine_wave_modulation',
              'square_wave_modulation'];

    # %Default values
    stimulus['frequency'] = [];
    stimulus['rise_fall'] = 0;
    stimulus['soundtype_name'] = [];
    stimulus['reverse_vocal_call'] = [];
    stimulus['vocal_call_file'] = [];
    stimulus['bandwidth'] = [];
    stimulus['usweep'] = [];

    if stim_type == 0:
        return stimulus, stim_type
    elif stim_type == 1: #tone
        stimulus['frequency'] = float(stim_data[5]);
        stimulus['rise_fall'] = float(stim_data[6]);
        stimulus['soundtype_name'] = 'tone';
    elif stim_type == 2: #fmsweep
        stimulus['frequency'] = float(stim_data[5]);
        stimulus['bandwidth'] = float(stim_data[6]);
        stimulus['usweep'] = float(stim_data[7]);
        stimulus['rise_fall'] = float(stim_data[8]);
        stimulus['soundtype_name'] = 'fmsweep';
    elif stim_type == 8: # vocalization
        # print 'vocalization', stim_data
        stimulus['soundtype_name'] = 'vocalization';
        stimulus['reverse_vocal_call'] = int(stim_data[5]);
        if int(stim_data[6]) == 0:
            # %Old school
            # print 'stim_data 20', stim_data[20]
            stimulus['vocal_call_file'] = stim_data[20]
        else:
            # %New School
            # print stim_data[24], stim_data[33] + stim_data[35]
            # if len(stim_data[24]) > 1 and stim_data != '-1':
            #     print 'WARNING: PST file generated between March and September 2007. \n No audio file extension information available. \n Using .call1'
            # else:
            stimulus['vocal_call_file'] = stim_data[33] + stim_data[35]
    else:
        stimulus['soundtype_name'] = stim_types[stim_type];

    return stimulus, stim_type

if __name__ == '__main__':
  # parse_pst('/home/leeloo/testdata/Mouse 497/Mouse497.pst')
  parse_pst('C:/Users/Leeloo/testdata/Mouse 497/Mouse497.pst')
  parse_pst('C:/Users/Leeloo/testdata/August 5 2010/August 5 2010.pst')
