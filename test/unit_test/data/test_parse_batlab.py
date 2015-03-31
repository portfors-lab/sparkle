import test.sample as sample
from sparkle.data.ExtractRawData import extract_raw_data
from sparkle.data.ParsePST import parse_pst

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
              'square_wave_modulation',
              'twotone',
              'threetone',
              'fourtone',
              'control']

def test_parse_batlab():
    filename = sample.batlabfile()
    experiment_data = parse_pst(filename + '.pst')
    
    assert 'pst_filename' in experiment_data
    assert 'test' in experiment_data

    assert len(experiment_data['test']) == 13
    assert len(experiment_data['test'][0]['trace']) == 10
    assert len(experiment_data['test'][12]['trace']) == 4

    for i, test in enumerate(experiment_data['test']):
        assert test['testnum'] == i+1 # batlab counts from 1, not 0
        assert test['testtype'] in test_types
        for trace in test['trace']:
            # know that the test recordings are all the same for these parameters
            assert trace['record_duration'] == 100 # batlab reports in ms
            assert trace['samplerate_ad'] == 40000
            assert trace['length_in_raw_file'] == (trace['record_duration']/1000.) * trace['samplerate_ad'] * 2 * trace['num_samples']

        assert 'stimulus' in trace

    raw_data = extract_raw_data(filename + '.raw', experiment_data)
    assert len(raw_data) == 13
    assert len(raw_data[0]) == 10
    assert len(raw_data[12]) == 4
    assert raw_data[0][0].shape == (5, 4000)
    assert raw_data[12][0].shape == (5, 4000)
