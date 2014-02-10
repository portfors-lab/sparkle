import time, sys
import numpy as np

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

from PyQt4 import QtCore, QtGui
from spikeylab.plotting.plotz import ScrollingPlot

app = None
def setUp():
    global app
    app = QtGui.QApplication(sys.argv)

def tearDown():
    global app
    app.exit(0)

def test_scrollplot_mpl():
    fig = ScrollingPlot(1, 0.01)
    fig.show()

    npts = 1000
    segment = 10
    amp = 1
    x = np.linspace(0, 2*np.pi, segment*10)
    stim = amp * np.sin(x)
    for iseg in range(0,int(npts/segment)):
        fig.append(stim[np.mod(iseg,10)*10:np.mod(iseg+1,10)*10-1])
        QtGui.QApplication.processEvents()
        #time.sleep(0.01)

    fig.close()
