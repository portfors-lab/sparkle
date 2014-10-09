"""This test makes sure we get the same results for RMS and peak amplitude for
tones. Calibrations and tone curves should match.
"""

import sys

import numpy as np
from PyQt4 import QtGui

from spikeylab.acq.players import FinitePlayer
from spikeylab.stim.types.stimuli_classes import FMSweep
from spikeylab.tools import audiotools as atools
from spikeylab.gui.plotting.pyqtgraph_widgets import SimplePlotWidget
from test.scripts.util import record, run_tone_curve

dur = 0.2
fs = 5e5

player = FinitePlayer()
player.set_aochan(u"PCI-6259/ao0")
player.set_aichan(u"PCI-6259/ai0")

player.set_aidur(dur)
player.set_aisr(fs)

refv = 2.0 # Volts
calf = 17000
# ref dB must be measured for peak and RMS acurately
refdb_rms = 99.6 # dB SPL
refdb_peak = 97 # dB SPL

tone_frequencies = range(17000, 100000, 5000)
# tone_intensities = [50, 60, 70, 80, 90, 100]
# tone_frequencies = [5000, calf, 50000, 100000]
tone_intensities = [70, 80]

frange = [3750, 101250] # range to apply calibration to
filter_len = 2**13
# get a calibration... the way we calculate amplitude shouldn't
# matter much to tones, so make sure it doesn't affect
# the calibration
chirp = FMSweep()
chirp.setDuration(dur)
chirp.setIntensity(80)

npts = dur*fs
freqs = np.arange(npts/2+1)/(float(npts)/fs)

# Run for RMS
atools.USE_RMS = True
atools.mphone_sensitivity = 0.00407

chirp_signal = chirp.signal(fs, 0, refdb_rms, refv)
recorded_chirp = record(player, chirp_signal, fs)
chirp_curve_rms = atools.attenuation_curve(chirp_signal, recorded_chirp, 
                                   fs, calf, smooth_pts=99)
cal = atools.impulse_response(fs, chirp_curve_rms, freqs, frange, filter_len)

print 'Running RMS curve'
testcurve_rms = run_tone_curve(tone_frequencies, tone_intensities,
                               player, fs, dur, refdb_rms, refv, cal,
                               frange)

# Run for peak amplitude
atools.USE_RMS = False
chirp_signal = chirp.signal(fs, 0, refdb_peak, refv)
recorded_chirp = record(player, chirp_signal, fs)
chirp_curve_peak = atools.attenuation_curve(chirp_signal, recorded_chirp, 
                                   fs, calf, smooth_pts=99)
cal = atools.impulse_response(fs, chirp_curve_peak, freqs, frange, filter_len)

print "\nRunning Peak curve"
testcurve_peak = run_tone_curve(tone_frequencies, tone_intensities,
                                player, fs, dur, refdb_peak, refv, cal,
                                frange)

print "\nDone."
# Plot calibrations
app = QtGui.QApplication(sys.argv)

# this should look like a single line plot -- i.e the curves should be identical
cal_plot = SimplePlotWidget(freqs, [chirp_curve_rms, chirp_curve_peak])
curve_plot = SimplePlotWidget(tone_frequencies, testcurve_rms)
curve_plot.appendRows(tone_frequencies, testcurve_peak, 'r')

cal_plot.show()
curve_plot.show()

sys.exit(app.exec_())
