"""Loops through a set of frequency and attenuation ranges to test
whether there is any signal loss from a piece of hardware connected
in between the analog out and intput terminals of the DAQ card.

Should be used to test the attenuator and amplifer separately. The 
attenuation range will (at least try) to set the value on the attenuator
so it does not make sense to have more than one value (0) for this, if you
are testing a difference piece of hardware.

Plots and displays results
"""
import sys

import matplotlib.pyplot as plt
import numpy as np

from sparkle.io.players import FinitePlayer
from sparkle.tools import audiotools
from test.scripts.util import record

#################################################
# change these values to suit

refV = 1.0 # the amplitude of stimulus to output
dur = 0.2 # duration of stimulus
fs = 5e5 # ongoing and recording samplerate

# ranges to loop through
frequency_range = range(5000, int(1e5), 2000)
attenuation_range = [30, 20, 10, 0]

# channels of the DAC to generate or record on
outchan = u"PCI-6259/ao0"
inchan = u"PCI-6259/ai0"

################################################
player = FinitePlayer()
player.set_aochan(outchan)
player.set_aichan(inchan)
player.set_aidur(dur)
player.set_aisr(fs)

npts = dur * fs
all_results = []
for atten in attenuation_range:
    freq_results = []
    for freq in frequency_range:
        sys.stdout.write('.') # print without space
        tone = refV * np.sin((freq*dur) * np.linspace(0, 2*np.pi, npts))
        tone_rms = audiotools.rms(tone)
        result = record(player, tone, fs, atten)
        rms = audiotools.rms(result)
        # magnitude of signal loss
        db = 20.*np.log10(rms/tone_rms)

        if np.amax(abs(result)) > 9.0:
            print 'voltage getting high!', np.amax(abs(result))
            sys.exit(-1)
        # print 'rms', rms
        # print 'max', np.amax(abs(result))
        freq_results.append(db)
    all_results.append(freq_results)
    plt.plot(frequency_range, freq_results, label=str(atten))
print 'done'

plt.legend()

# print 'all_results', all_results
plt.show()
