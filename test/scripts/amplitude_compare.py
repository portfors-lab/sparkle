"""This test makes sure we get the same results for RMS and peak amplitude for
tones. Calibrations and tone curves should match.
"""

import sys

import numpy as np

from sparkle.QtWrapper import QtGui
from sparkle.acq.players import FinitePlayer
from sparkle.gui.plotting.pyqtgraph_widgets import SimplePlotWidget
from sparkle.stim.types.stimuli_classes import FMSweep
from sparkle.tools import audiotools as atools
from test.scripts.util import record, run_tone_curve

# copied from SO
v = 1.0
s = 1.0
p = 0.0
def rgbcolor(h, f):
    """Convert a color specified by h-value and f-value to an RGB
    three-tuple."""
    # q = 1 - f
    # t = f
    if h == 0:
        return v, f, p
    elif h == 1:
        return 1 - f, v, p
    elif h == 2:
        return p, v, f
    elif h == 3:
        return p, 1 - f, v
    elif h == 4:
        return f, p, v
    elif h == 5:
        return v, p, 1 - f

def rgb(i, n):
    """Compute a list of distinct colors, ecah of which is
    represented as an RGB three-tuple"""
    hue = 360.0 / n * i
    h = np.floor(hue / 60) % 6
    f = hue / 60 - np.floor(hue / 60)
    color_tuple = rgbcolor(h,f)
    color_tuple = (color_tuple[0]*255, color_tuple[1]*255, color_tuple[2]*255)
    return color_tuple

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
tone_intensities = [60]#, 70]

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
rms_curve_spec_peak, rms_curve_amp_rms, rms_curve_amp_peak, rms_curve_summed = run_tone_curve(tone_frequencies, tone_intensities,
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
peak_curve_spec_peak, peak_curve_amp_rms, peak_curve_amp_peak,  peak_curve_summed = run_tone_curve(tone_frequencies, tone_intensities,
                                player, fs, dur, refdb_peak, refv, cal,
                                frange)

print "\nDone."
# Plot calibrations
app = QtGui.QApplication(sys.argv)

# this should look like a single line plot -- i.e the curves should be identical
cal_plot = SimplePlotWidget(freqs, [chirp_curve_rms, chirp_curve_peak])
curve_plot = SimplePlotWidget(tone_frequencies, rms_curve_spec_peak, rgb(0,8), legendstr="RMS spec peak")
curve_plot.appendRows(tone_frequencies, peak_curve_spec_peak, rgb(1,8), legendstr="peak spec peak")
curve_plot.appendRows(tone_frequencies, rms_curve_amp_rms, rgb(2,8), legendstr="RMS signal RMS")
curve_plot.appendRows(tone_frequencies, peak_curve_amp_rms, rgb(3,8), legendstr="peak signal RMS")
curve_plot.appendRows(tone_frequencies, rms_curve_amp_peak, rgb(4,8), legendstr="RMS signal peak")
curve_plot.appendRows(tone_frequencies, peak_curve_amp_peak, rgb(5,8), legendstr="peak signal peak")
curve_plot.appendRows(tone_frequencies, rms_curve_summed, rgb(6,8), legendstr="RMS summed spec")
curve_plot.appendRows(tone_frequencies, peak_curve_summed, rgb(7,8), legendstr="peak summed spec")

cal_plot.show()
curve_plot.show()

sys.exit(app.exec_())
