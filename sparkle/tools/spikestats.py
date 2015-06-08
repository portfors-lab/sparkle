""" Here is a doc string for spikestats :)"""
import numpy as np

def refractory(times, refract=0.002):
	"""Removes spikes in times list that do not satisfy refractor period

	:param times: list(float) of spike times in seconds
	:type times: list(float)
	:param refract: Refractory period in seconds
	:type refract: float
	:returns: list(float) of spike times in seconds

	For every interspike interval < refract, 
	removes the second spike time in list and returns the result"""
	times_refract = []
	times_refract.append(times[0])
	for i in range(1,len(times)):
		if times_refract[-1]+refract <= times[i]:
			times_refract.append(times[i])        
	return times_refract

def spike_times(signal, threshold, fs, absval=True):
    """Detect spikes from a given signal

    :param signal: Spike trace recording (vector)
    :type signal: numpy array
    :param threshold: Threshold value to determine spikes
    :type threshold: float
    :param absval: Whether to apply absolute value to signal before thresholding
    :type absval: bool
    :returns: list(float) of spike times in seconds

    For every continuous set of points over given threshold, 
    returns the time of the maximum"""
    times = []
    if absval:
        signal = np.abs(signal)
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
                times.append(float(over[0])/fs)
                if 1 not in segments:
                    # make sure that first point is in there
                    segments[0] = 1
            if segments[-1] != len(over)-1:
                segments = np.insert(segments, [len(segments)], [len(over)-1])
            else:
                times.append(float(over[-1])/fs)

        for iseg in range(1,len(segments)):
            if segments[iseg] - segments[iseg-1] == 1:
                # only single point over threshold
                idx = over[segments[iseg]]
            else:
                segments[0] = segments[0]-1                
                # find maximum of continuous set over max
                idx = over[segments[iseg-1]+1] + np.argmax(signal[over[segments[iseg-1]+1]:over[segments[iseg]]])
            times.append(float(idx)/fs)
    elif len(over) == 1:
        times.append(float(over[0])/fs)
        
    if len(times)>0:
    	return refractory(times)
    else:
    	return times

def bin_spikes(spike_times, binsz):
    """Sort spike times into bins

    :param spike_times: times of spike instances
    :type spike_times: list
    :param binsz: length of time bin to use
    :type binsz: float
    :returns: list of bin indicies, one for each element in spike_times
    """
    bins = np.empty((len(spike_times),), dtype=int)
    for i, stime in enumerate(spike_times):
        # around to fix rounding errors
        bins[i] = np.floor(np.around(stime/binsz, 5))
    return bins

def spike_latency(signal, threshold, fs):
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
            latency = float(idx)/fs
        elif segments[0] == 0:
            #first point in singleton
            latency = float(over[0])/fs
        else:
            idx = over[0] + np.argmax(signal[over[0]:over[segments[0]]])
            latency = float(idx)/fs
    elif len(over) > 0:
        latency = float(over[0])/fs
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

def dataset_spike_counts(dset, threshold, fs):
    """Dataset should be of dimensions (trace, rep, samples)"""
    if len(dset.shape) == 3:
        results = np.zeros(dset.shape[0])
        for itrace in range(dset.shape[0]):
            results[itrace] = count_spikes(dset[itrace], threshold, fs)
        return results
    elif len(dset.shape == 2):
        return count_spikes(dset, threshold, fs)
    else:
        raise Exception("Improper data dimensions")

def count_spikes(dset, threshold, fs):
    trace_count = 0
    for irep in range(dset.shape[0]):
        trace_count += len(spike_times(dset[irep,:], threshold, fs))
    return trace_count
