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

    return times

def bin_spikes(spike_times, binsz):
    """ returns a list of bin centers, one for each time"""
    bins=[]
    for stime in spike_times:
        bins.append((np.floor(stime/binsz)*binsz)+(binsz/2))

    return bins