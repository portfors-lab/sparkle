import os, shutil
from PyQt4 import QtGui

tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), u"tmp")
app = None

def setup_package():
    if not os.path.exists(tempfolder):
        os.mkdir(tempfolder)
    global app
    app = QtGui.QApplication([])

def teardown_package():
    shutil.rmtree(tempfolder, ignore_errors=True)
    global app
    app.exit(0)
    app = None