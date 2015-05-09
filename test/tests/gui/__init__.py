import sip
sip.setdestroyonexit(0)

import os, shutil
import numpy as np

from sparkle.QtWrapper import QtGui

tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), u"tmp")
app = None

# executes once before all tests
def setup():
    if not os.path.exists(tempfolder):
        os.mkdir(tempfolder)
    np.warnings.filterwarnings('ignore', "All-NaN axis encountered", RuntimeWarning)

    global app
    app = QtGui.QApplication([])

def teardown():
    shutil.rmtree(tempfolder, ignore_errors=True)
    np.warnings.resetwarnings()
    
    global app
    app.exit(0)
    app = None
