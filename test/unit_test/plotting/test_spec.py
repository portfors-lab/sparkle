import os, time

import spikeylab.tools.audiotools as audiotools
from spikeylab.plotting.custom_plots import SpecWidget

from PyQt4.QtGui import QApplication

import test.sample as sample

PAUSE = 0.5

def test_spec_from_wav():

    spec, f, bins, fs = audiotools.spectrogram(sample.samplewav())
    fig = SpecWidget()
    fig.show()
    fig.update_data(spec, xaxis=bins, yaxis=f)

    QApplication.processEvents()
    time.sleep(PAUSE)

    fig.close()