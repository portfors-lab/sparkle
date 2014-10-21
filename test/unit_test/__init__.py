import sip
sip.setdestroyonexit(0)
from QtWrapper import QtGui
app = None

# executes once before all tests
def setup():
    global app
    app = QtGui.QApplication([])

def teardown():
    global app
    app.exit(0)
    app = None
