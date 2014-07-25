import sip
sip.setapi('QVariant', 2)
sip.setapi('QString', 2)

from PyQt4 import QtGui

from stimeditor_form import Ui_StimulusEditor
from auto_parameters_editor import Parametizer
from spikeylab.stim.abstract_editor import AbstractEditorWidget
from spikeylab.plotting.pyqtgraph_widgets import SpecWidget

class StimulusEditor(AbstractEditorWidget):
    """Interface for editing stimuli in any way possible. Assemble components,
        assign auto-tests"""
    name = 'Custom'
    def __init__(self, parent=None):
        super(StimulusEditor,self).__init__(parent)
        self.ui = Ui_StimulusEditor()
        self.ui.setupUi(self)
        self.ui.trackview.installEventFilter(self.ui.templateBox.trash())
        
        # component selection update connections
        self.ui.trackview.componentSelected.connect(self.ui.parametizer.view().componentSelection)
        self.ui.parametizer.view().parameterChanged.connect(self.ui.trackview.updateSelectionModel)

        # when the auto-parameter editor is toggled show/hide changes the edit mode of the StimulusView
        self.ui.parametizer.visibilityChanged.connect(self.ui.trackview.setMode)
        
        # self.setWindowModality(2) # application modal
    
    def setStimulusModel(self, model):
        """Set the QStimulusModel for the StimulusView"""
        self.ui.trackview.setModel(model)
        self.ui.nrepsSpnbx.setValue(model.repCount())

        self.ui.parametizer.hintRequested.connect(self.setHint)
        self.ui.parametizer.randomizeCkbx.toggled.connect(model.randomToggle)
        self.ui.parametizer.randomizeCkbx.setChecked(bool(model.reorder()))

        # extract the QAutoParameterModel from the QStimulusModel and 
        # set in the AutoParameterView
        autoParamModel = model.autoParams()
        self.ui.parametizer.setModel(autoParamModel)
        # whether the auto parameters are emtpy 
        # affects the enable-ness of the StimlusView
        autoParamModel.emptied.connect(self.ui.trackview.emptySelection)

    def setRepCount(self, count):
        self.ui.trackview.model().setRepCount(count)

    def preview(self):
        """Assemble the current components in the QStimulusModel and generate a spectrogram 
        plot in a separate window"""
        msg = self.ui.trackview.model().verify()
        if msg:
            answer = QtGui.QMessageBox.warning(self, "Bummer", 'Problem: {}.'.format(msg))
            return
        stim_signal, atten, ovld = self.ui.trackview.model().signal()

        fig = SpecWidget()
        fig.updateData(stim_signal, self.ui.trackview.model().samplerate())
        fig.setTitle('Stimulus Preview')
        fig.show()
        self.previewFig = fig

    def model(self):
        """Returns the QStimulusModel for this editor"""
        return self.ui.trackview.model()

    def setHint(self, message):
        self.ui.hintTxedt.setText(message)

    def closeEvent(self, event):
        self.ui.trackview.model().cleanComponents()
        self.ui.trackview.model().purgeAutoSelected()
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
    from spikeylab.stim.qstimulus import QStimulusModel
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
    # test_file = os.path.join(os.path.expanduser('~'),r'Dropbox\daqstuff\M1_FD024\M1_FD024_syl_12.wav')
    # vocal0.setFile(test_file)

    silence0 = Silence()
    silence0.setDuration(0.025)

    stim = StimulusModel()
    stim.setReferenceVoltage(100, 0.1)
    stim.insertComponent(tone2)
    stim.insertComponent(tone1)
    # stim.insertComponent(tone0)

    # stim.insertComponent(tone4, (1,0))
    # stim.insertComponent(tone5, (1,0))
    stim.insertEmptyRow()
    stim.insertComponent(vocal0, 1,0)

    stim.insertComponent(tone3, 1,0)
    # stim.insertComponent(silence0, (2,0))

    qstim = QStimulusModel(stim)
    editor = StimulusEditor()
    editor.setStimulusModel(qstim)

    # editor.ui.trackview.setModel(stim)

    editor.show()
    app.exec_()