import sip
sip.setapi('QVariant', 2)
sip.setapi('QString', 2)

from PyQt4 import QtGui

from stimeditor_form import Ui_StimulusEditor
from auto_parameters_editor import Parametizer
from spikeylab.stim.abstract_editor import AbstractEditorWidget
from spikeylab.plotting.pyqtgraph_widgets import SpecWidget

class StimulusEditor(AbstractEditorWidget):
    name = 'Custom'
    def __init__(self, parent=None):
        super(StimulusEditor,self).__init__(parent)
        self.ui = Ui_StimulusEditor()
        self.ui.setupUi(self)
        self.ui.trackview.installEventFilter(self.ui.template_box.trash())
        # self.setWindowModality(2) # application modal
    
    def setStimulusModel(self, model):
        self.ui.trackview.setModel(model)
        self.ui.nreps_spnbx.setValue(model.repCount())
        # parametizer grabs model from view
        self.ui.parametizer.setStimulusView(self.ui.trackview)
        self.ui.parametizer.hintRequested.connect(self.setHint)

    def setRepCount(self, count):
        self.ui.trackview.model().setRepCount(count)

    def preview(self):
        stim_signal, atten = self.ui.trackview.model().signal()

        fig = SpecWidget()
        fig.update_data(stim_signal, self.ui.trackview.model().samplerate())
        fig.set_title('Stimulus Preview')
        fig.show()
        self.preview_fig = fig

    def model(self):
        return self.ui.trackview.model()

    def setHint(self, message):
        self.ui.hint_txedt.setText(message)

    def closeEvent(self, event):
        msg = self.ui.trackview.model().verify()
        if msg:
            answer = QtGui.QMessageBox.question(self, 'Oh Dear!', 
                                'Problem: {}. Do you want to deal with this?'.format(msg),
                                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if answer == QtGui.QMessageBox.Yes:
                event.ignore()

if __name__ == "__main__":
    import sys, os
    from PyQt4 import QtGui
    from spikeylab.stim.stimulusmodel import StimulusModel
    from spikeylab.stim.types.stimuli_classes import *
    app = QtGui.QApplication(sys.argv)

    tone0 = PureTone()
    tone0.setDuration(0.02)
    tone1 = PureTone()
    tone1.setDuration(0.040)
    tone1.setFrequency(25000)
    tone2 = PureTone()
    tone2.setDuration(0.010)

    tone3 = PureTone()
    tone3.setDuration(0.03)
    tone4 = PureTone()
    tone4.setDuration(0.030)
    tone5 = PureTone()
    tone5.setDuration(0.030)

    vocal0 = Vocalization()
    test_file = os.path.join(os.path.expanduser('~'),r'Dropbox\daqstuff\M1_FD024\M1_FD024_syl_12.wav')
    vocal0.setFile(test_file)

    silence0 = Silence()
    silence0.setDuration(0.025)

    stim = StimulusModel()
    stim.setReferenceVoltage(100, 0.1)
    stim.insertComponent(tone2)
    stim.insertComponent(tone1)
    # stim.insertComponent(tone0)

    # stim.insertComponent(tone4, (1,0))
    # stim.insertComponent(tone5, (1,0))
    stim.insertComponent(vocal0, (1,0))

    stim.insertComponent(tone3, (1,0))
    # stim.insertComponent(silence0, (2,0))

    editor = StimulusEditor()
    editor.setStimulusModel(stim)

    # editor.ui.trackview.setModel(stim)

    editor.show()
    app.exec_()