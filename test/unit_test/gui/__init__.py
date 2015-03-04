import os, shutil
import numpy as np
from QtWrapper import QtGui

tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), u"tmp")

def setup_package():
    if not os.path.exists(tempfolder):
        os.mkdir(tempfolder)
    np.warnings.filterwarnings('ignore', "All-NaN axis encountered", RuntimeWarning)


def teardown_package():
    shutil.rmtree(tempfolder, ignore_errors=True)
    np.warnings.resetwarnings()