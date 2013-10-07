import numpy as np
from scipy.signal import firwin, lfilter

def calc_spike_times(signal, threshold, sr, mint=None):
    """ Simple spike dectection, for every continuous set of points over
        given threshold, returns the index of the maximum"""
    times = []
    over, = np.where(signal>threshold)
    segments, = np.where(np.diff(over) > 1)
    
    if len(segments) > 0:
        # add end points to sections for looping
        if segments[0] != 0:
            segments = np.insert(segments, [0], [0])
        if segments[-1] != len(over)-1:
            np.insert(segments, [len(segments)], [len(over)-1])
        segments[0] = segments[0]-1
        for iseg in range(len(segments)-1):
            if segments[iseg+1] - segments[iseg] == 1:
                # only single point over threshold
                idx = over[iseg]
            else:
                # find maximum of continuous set over max
                idx = over[segments[iseg]+1] + np.argmax(signal[over[segments[iseg]+1]:over[segments[iseg+1]]])
            # print 'idx', idx
            times.append(float(idx)/sr)
    # method borrowed from Lar's analysis code
    #first run a lowpass filter on signal

    # er, this is copied from SE example
    # h = firwin(numtaps=10, cutoff=5000, nyq=sr/2)
    # filtered_signal = lfilter(h, 1.0, signal)
    return times

def bin_spikes(spike_times, binsz):
    """ returns a list of bin centers, one for each time"""
    bins=[]
    for stime in spike_times:
        bins.append((np.floor(stime/binsz)*binsz)+(binsz/2))

    return bins