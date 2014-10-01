"""Finds the longest protcol length possible for a given
window size for the current RAM usage -- therefore you get different 
limits if you are using 64-bit python or 32-bit.
"""
from spikeylab.stim.stimulus_model import StimulusModel
from spikeylab.stim.types.stimuli_classes import PureTone, Vocalization, Silence

acqrate = 5e5
winsz = 0.2 #seconds

def create_tone_stim(stepsize, dur):
    component = PureTone()
    component.setDuration(dur)
    stim_model = StimulusModel()
    stim_model.setReferenceVoltage(100,1.0)
    stim_model.insertComponent(component, 0,0)
    auto_model = stim_model.autoParams()
    auto_model.insertRow(0)
    
    auto_model.toggleSelection(0,component)

    values = ['frequency', 0, 100, stepsize]
    auto_model.setParamValue(0, parameter=values[0], start=values[1], 
                            stop=values[2], step=values[3])

    print 'Number of traces: {}, num samples: {}'.format(stim_model.traceCount(), stim_model.traceCount()*(dur*5e5))
    return stim_model

if __name__ == "__main__":
    dur = 0.2
    for count in range(100, 50000, 100):
        try:
            step = 100./count
            stim = create_tone_stim(step, dur)
            signals = stim.expandedStim()
            # print 'numpy array bytes', signals[0][0][0].nbytes*count
        except MemoryError:
            print "Ran out of memory at step {}".format(step)
            break
    print "DONE"