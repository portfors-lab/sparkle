""" Here is a doc string for spikestats :)"""
import numpy as np
from scipy.signal import firwin, lfilter

def spike_times(signal, threshold, sr, mint=None):
    """Detect spikes from a given signal

    :param signal: Spike trace recording (vector)
    :type signal: numpy array
    :param threshold: Threshold value to determine spikes
    :type threshold: float
    :returns: list(float) of spike times in seconds

    For every continuous set of points over given threshold, 
    returns the time of the maximum"""
    times = []
    over, = np.where(signal>threshold)
    segments, = np.where(np.diff(over) > 1)
    if len(over) > 1:
        if len(segments) == 0:
            segments = [0, len(over)-1]
        else:
            # add end points to sections for looping
            if segments[0] != 0:
                segments = np.insert(segments, [0], [0])
            else:
                #first point in singleton
                times.append(float(over[0])/sr)
            if segments[-1] != len(over)-1:
                segments = np.insert(segments, [len(segments)], [len(over)-1])
            else:
                times.append(float(over[-1])/sr)

        for iseg in range(1,len(segments)):
            if segments[iseg] - segments[iseg-1] == 1:
                # only single point over threshold
                idx = over[iseg]
            else:
                segments[0] = segments[0]-1                
                # find maximum of continuous set over max
                idx = over[segments[iseg-1]+1] + np.argmax(signal[over[segments[iseg-1]+1]:over[segments[iseg]]])
            times.append(float(idx)/sr)
    elif len(over) == 1:
        times.append(float(over[0])/sr)
        
    return times

def bin_spikes(spike_times, binsz):
    """Sort spike times into bins

    :param spike_times: times of spike instances
    :type spike_times: list
    :param binsz: length of time bin to use
    :type binsz: float
    :returns: list of bin indicies, one for each element in spike_times
    """
    bins=[]
    for stime in spike_times:
        # bins.append((np.floor(stime/binsz)*binsz)+(binsz/2))
        bins.append(int(np.floor(stime/binsz)))
    return bins

def spike_latency(signal, threshold, sr):
    """Find the latency of the first spike over threshold

    :param signal: Spike trace recording (vector)
    :type signal: numpy array
    :param threshold: Threshold value to determine spikes
    :type threshold: float
    :returns: float -- Time of peak of first spike, or None if no values over threshold

    This is the same as the first value returned from calc_spike_times
    """
    over, = np.where(signal>threshold)
    segments, = np.where(np.diff(over) > 1)

    if len(over) > 1:
        if len(segments) == 0:
            # only signal peak
            idx = over[0] + np.argmax(signal[over[0]:over[-1]])
            latency = float(idx)/sr
        elif segments[0] == 0:
            #first point in singleton
            latency = float(over[0])/sr
        else:
            idx = over[0] + np.argmax(signal[over[0]:over[segments[0]]])
            latency = float(idx)/sr
    elif len(over) > 0:
        latency = float(over[0])/sr
    else:
        latency = None

    return latency

def firing_rate(spike_times, window_size=None):
    """Calculate the firing rate of spikes

    :param spike_times: times of spike instances
    :type spike_times: list
    :param window_size: length of time to use to determine rate.
    If none, uses time from first to last spike in spike_times
    :type window_size: float
    """
    if len(spike_times) == 0:
        return 0

    if window_size is None:
        if len(spike_times) > 1:
            window_size = spike_times[-1] - spike_times[0]
        elif len(spike_times) > 0:
            # Only one spike, and no window - what to do?
            window_size = 1
        else:
            window_size = 0

    rate = window_size/len(spike_times)
    return rate