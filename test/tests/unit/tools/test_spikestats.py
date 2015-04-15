import numpy as np
import scipy.io.wavfile as wv

import test.sample as sample
from sparkle.tools.spikestats import bin_spikes, firing_rate, spike_latency, \
    spike_times


def test_spike_times_sin():
    """Use a smooth stimulus to test"""
    n = 1024
    x = np.arange(n)
    fq = 16
    y = np.sin(2*np.pi*fq*x/n)
    threshold = 0.7
    fs = 10

    times = spike_times(y, threshold, fs)

    assert len(times) == fq

    # calculate where the peaks will be for sin wave
    period = (float(n)/10)/16
    peak_time = period/4
    print period, peak_time
    sin_peak_times = np.arange(0,102.4,period)+peak_time

    print sin_peak_times, times
    # very small rounding errors different for different calc methods
    assert np.allclose(sin_peak_times, times, atol=0.00000001)

def test_spike_times_sample_syl():
    """ Not realistic, but complex """
    sylpath = sample.samplewav()
    fs, wavdata = wv.read(sylpath)
    wavdata = wavdata.astype(float)/np.max(wavdata)
    threshold = 0.8

    times = spike_times(wavdata, threshold, fs)

    # manually found outwith
    control_times = [ 0.039461,  0.039704,  0.039717,  0.039819,  0.039896,  0.039933,
        0.039984,  0.039997,  0.040048,  0.04024,   0.040304,  0.040507,  0.04052,
        0.040597,  0.040712,  0.040763,  0.040776,  0.040968,  0.041005,  0.04144,
        0.043683,  0.043824]

    assert np.allclose(control_times, times, atol=0.00000001)

def test_spike_times_single_point_mid():
    y = np.zeros(1024)
    idx = 77
    y[idx] = 1
    threshold = 0.8
    fs = 10

    times = spike_times(y, threshold, fs)
    assert len(times) == 1
    assert times[0] == float(idx)/fs


def test_spike_times_single_point_start():
    y = np.zeros(1024)
    idx = 0
    y[idx] = 1
    threshold = 0.8
    fs = 10

    times = spike_times(y, threshold, fs)
    assert len(times) == 1
    assert times[0] == float(idx)/fs

def test_spike_times_single_point_end():
    y = np.zeros(1024)
    idx = 1023
    y[idx] = 1
    threshold = 0.8
    fs = 10

    times = spike_times(y, threshold, fs)
    assert len(times) == 1
    assert times[0] == float(idx)/fs

def test_spike_times_flat_max():
    y = np.zeros(1024)
    idx = range(77,87)
    y[idx] = 1
    threshold = 0.8
    fs = 10

    # should be first point over threshold in this case
    times = spike_times(y, threshold, fs)
    assert len(times) == 1
    assert times[0] == float(idx[0])/fs

def test_spike_times_start_over_thresh():
    y = np.zeros(1024)
    idx = range(0,15)
    y[idx] = 1
    threshold = 0.8
    fs = 10

    # should be first point over threshold in this case
    times = spike_times(y, threshold, fs)
    assert len(times) == 1
    assert times[0] == float(idx[0])/fs

def test_spike_times_end_over_thresh():
    y = np.zeros(1024)
    idx = range(110,1024)
    y[idx] = 1
    threshold = 0.8
    fs = 10

    # should be first point over threshold in this case
    times = spike_times(y, threshold, fs)
    assert len(times) == 1
    assert times[0] == float(idx[0])/fs

def test_spike_times_flat_max_with_single_start():
    y = np.zeros(1024)
    idx = range(555,565)
    y[idx] = 1
    idx1 = 77
    y[idx1] = 1
    threshold = 0.8
    fs = 10

    # should be first point over threshold in this case
    times = spike_times(y, threshold, fs)
    print times
    assert len(times) == 2
    assert times[0] == float(idx1)/fs
    assert times[1] == float(idx[0])/fs

def test_spike_times_flat_max_with_single_ends():
    y = np.zeros(1024)
    idx = range(555,565)
    y[idx] = 1
    idx1 = 77
    y[idx1] = 1
    idx2 = 666
    y[idx2] = 1
    threshold = 0.8
    fs = 10

    # should be first point over threshold in this case
    times = spike_times(y, threshold, fs)
    print times
    assert len(times) == 3
    assert times[0] == float(idx1)/fs
    assert times[1] == float(idx[0])/fs
    assert times[2] == float(idx2)/fs

def test_spike_times_flat_max_with_single_mid():
    y = np.zeros(1024)
    idx = range(77,87)
    y[idx] = 1
    idx1 = 666
    y[idx1] = 1
    idx2 = range(888,898)
    y[idx2] = 1
    threshold = 0.8
    fs = 10

    # should be first point over threshold in this case
    times = spike_times(y, threshold, fs)
    print times
    assert len(times) == 3
    assert times[0] == float(idx[0])/fs
    assert times[1] == float(idx1)/fs
    assert times[2] == float(idx2[0])/fs

def test_spike_times_all_over():
    y = np.ones(1024)
    threshold = 0.8
    fs = 10

    times = spike_times(y, threshold, fs)
    assert len(times) == 1
    assert times[0] == 0

def test_spike_times_empty():
    y = np.zeros(1024)
    threshold = 0.8
    fs = 10

    times = spike_times(y, threshold, fs)
    assert len(times) == 0

#--------------------------------

def test_bin_spikes_even_middle_times():
    times = np.arange(0.05, 0.95, 0.1)
    binsz = 0.1
    bins = bin_spikes(times, binsz)
    assert np.array_equal(range(len(times)), bins)
    # assert bins == np.array(range(len(times)))

def test_bin_spikes_even_start_edge_times():
    times = np.arange(0, 0.9, 0.1)
    binsz = 0.1
    bins = bin_spikes(times, binsz)
    assert np.array_equal(range(len(times)), bins)

def test_bin_spikes_even_end_edge_times():
    times = np.arange(0.099, 0.999, 0.1)
    binsz = 0.1
    bins = bin_spikes(times, binsz)
    assert np.array_equal(range(len(times)), bins)

def test_bin_spikes_uneven_times():
    # manual times
    times = [0.7, 0.66, 0.22, 0.4, 0.4, 0.39]
    binsz = 0.1
    bins = bin_spikes(times, binsz)
    assert np.array_equal([7, 6, 2, 4, 4, 3], bins)

#---------------------------------

def test_spike_latency_smooth_stim():
    n = 1024
    x = np.arange(n)
    fq = 16
    y = np.sin(2*np.pi*fq*x/n)
    threshold = 0.7
    fs = 10

    latency = spike_latency(y, threshold, fs)

    # calculate where the peaks will be for sin wave
    period = (float(n)/10)/16
    peak_time = period/4
    print period, peak_time
    assert latency == peak_time

def test_spike_latency_single_point_mid():
    y = np.zeros(1024)
    idx = 77
    y[idx] = 1
    threshold = 0.8
    fs = 10

    latency = spike_latency(y, threshold, fs)
    assert latency == float(idx)/fs

def test_spike_latency_single_point_start():
    y = np.zeros(1024)
    idx = 0
    y[idx] = 1
    threshold = 0.8
    fs = 10

    latency = spike_latency(y, threshold, fs)
    assert latency == float(idx)/fs

def test_spike_latency_single_point_last():
    y = np.zeros(1024)
    idx = 1023
    y[idx] = 1
    threshold = 0.8
    fs = 10

    latency = spike_latency(y, threshold, fs)
    assert latency == float(idx)/fs

def test_spike_latency_same_max():
    y = np.zeros(1024)
    idx = range(77,87)
    y[idx] = 1
    threshold = 0.8
    fs = 10

    latency = spike_latency(y, threshold, fs)
    assert latency == float(idx[0])/fs

def test_spike_latency_same_max_start():
    y = np.zeros(1024)
    idx = range(0,87)
    y[idx] = 1
    threshold = 0.8
    fs = 10

    latency = spike_latency(y, threshold, fs)
    assert latency == float(idx[0])/fs

def test_spike_latency_same_last():
    y = np.zeros(1024)
    idx = range(1002, 1024)
    y[idx] = 1
    threshold = 0.8
    fs = 10

    latency = spike_latency(y, threshold, fs)
    assert latency == float(idx[0])/fs


def test_spike_latency_flat_max_with_single_start():
    y = np.zeros(1024)
    idx = range(555,565)
    y[idx] = 1
    idx1 = 77
    y[idx1] = 1
    threshold = 0.8
    fs = 10

    # should be first point over threshold in this case
    latency = spike_latency(y, threshold, fs)
    latency == float(idx[0])/fs

def test_spike_latency_flat_max_with_single_ends():
    y = np.zeros(1024)
    idx = range(555,565)
    y[idx] = 1
    idx1 = 77
    y[idx1] = 1
    idx2 = 666
    y[idx2] = 1
    threshold = 0.8
    fs = 10

    # should be first point over threshold in this case
    latency = spike_latency(y, threshold, fs)
    assert latency == float(idx1)/fs

def test_spike_latency_flat_max_with_single_mid():
    y = np.zeros(1024)
    idx = range(77,87)
    y[idx] = 1
    idx1 = 666
    y[idx1] = 1
    idx2 = range(888,898)
    y[idx2] = 1
    threshold = 0.8
    fs = 10

    # should be first point over threshold in this case
    latency = spike_latency(y, threshold, fs)
    assert latency == float(idx[0])/fs

def test_spike_latency_all_over():
    y = np.ones(1024)
    threshold = 0.8
    fs = 10

    latency = spike_latency(y, threshold, fs)
    assert latency == 0

def test_spike_latency_empty():
    y = np.zeros(1024)
    threshold = 0.8
    fs = 10

    latency = spike_latency(y, threshold, fs)
    assert latency is None


#--------------------------------

# def test_firing_rate_even_middle_times():
#     times = np.arange(0.05, 0.95, 0.1)
#     winsz = 0.1
#     rate = firing_rate(times, winsz)
#     print rate
#     assert rate == winsz

# def test_firing_rate_even_start_edge_times():
#     times = np.arange(0, 0.9, 0.1)
#     winsz = 0.1
#     rate = firing_rate(times, winsz)
#     assert rate == winsz

# def test_firing_rate_even_end_edge_times():
#     times = np.arange(0.099, 0.999, 0.1)
#     winsz = 0.1
#     rate = firing_rate(times, winsz)
#     assert rate == winsz

# def test_firing_rate_uneven_times():
#     # manual times
#     times = [0.7, 0.66, 0.22, 0.4, 0.4, 0.39]
#     winsz = 0.1
#     rate = firing_rate(times, winsz)
#     assert rate == (max(times) - min(times))/len(times)
