import sys
import numpy as np
from spikeylab.io.players import FinitePlayer
from test.scripts.util import record

refV = 1.0
dur = 0.2
fs = 5e5
npts = dur * fs

frequency_range = range(5000, int(1e5), 2000)
attenuation_range = [30, 20, 10, 0]

player = FinitePlayer()
player.set_aochan(u"PCI-6259/ao0")
player.set_aichan(u"PCI-6259/ai0")
player.set_aidur(dur)
player.set_aisr(fs)

import matplotlib.pyplot as plt
all_results = []
for atten in attenuation_range:
    freq_results = []
    for freq in frequency_range:
        sys.stdout.write('.') # print without space
        tone = refV * np.sin((freq*dur) * np.linspace(0, 2*np.pi, npts))
        tone_rms = np.sqrt(np.mean(pow(tone,2)))
        result = record(player, tone, fs, atten)
        rms = np.sqrt(np.mean(pow(result,2)))
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
