from PyQt4 import QtGui, QtCore

from stimeditor_form import Ui_StimulusEditor

class StimulusEditor(QtGui.QWidget):
    def __init__(self, parent=None):
        super(StimulusEditor,self).__init__(parent)
        self.ui = Ui_StimulusEditor()
        self.ui.setupUi(self)

    def setStimulus(self, stimulus):
        pass

if __name__ == "__main__":
    import sys
    from spikeylab.stim.stimulusmodel import *
    app  = QtGui.QApplication(sys.argv)

    tone0 = PureTone()
    tone0.setDuration(0.02)
    tone1 = PureTone()
    tone1.setDuration(0.040)
    tone2 = PureTone()
    tone2.setDuration(0.010)

    tone3 = PureTone()
    tone3.setDuration(0.03)
    tone4 = PureTone()
    tone4.setDuration(0.030)
    tone5 = PureTone()
    tone5.setDuration(0.030)

    vocal0 = Vocalization()
    # vocal0.setFile(r'C:\Users\amy.boyle\Dropbox\daqstuff\M1_FD024\M1_FD024_syl_12.wav')
    vocal0.setFile(r'C:\Users\Leeloo\Dropbox\daqstuff\M1_FD024\M1_FD024_syl_12.wav')

    silence0 = Silence()
    silence0.setDuration(0.025)

    stim = StimulusModel()
    stim.insertComponent(tone2)
    stim.insertComponent(tone1)
    stim.insertComponent(tone0)

    stim.insertComponent(tone4, (1,0))
    stim.insertComponent(tone5, (1,0))
    stim.insertComponent(vocal0, (1,0))

    stim.insertComponent(tone3, (2,0))
    stim.insertComponent(silence0, (2,0))

    editor = StimulusEditor()
    editor.ui.trackview.setModel(stim)

    editor.show()
    app.exec_()