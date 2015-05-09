from auto_parameters_editor import Parametizer
from sparkle.QtWrapper import QtGui
from sparkle.gui.plotting.pyqtgraph_widgets import SpecWidget
from sparkle.gui.stim.abstract_stim_editor import AbstractStimulusWidget
from stimulus_editor_form import Ui_StimulusEditor


class StimulusEditor(AbstractStimulusWidget):
    """Interface for editing stimuli in any way possible. Assemble components,
        assign auto-tests"""
    name = 'Custom'
    _rep_default_cache = [1] # list (mutable) so we can share between instances
    def __init__(self, parent=None):
        super(StimulusEditor,self).__init__(parent)
        self.ui = Ui_StimulusEditor()
        self.ui.setupUi(self)
        self.ui.trackview.installEventFilter(self.ui.templateBox.trash())
        
        # component selection update connections
        self.ui.trackview.componentSelected.connect(self.ui.parametizer.view().componentSelection)
        self.ui.parametizer.view().parameterChanged.connect(self.ui.trackview.updateSelectionModel)
        self.ui.trackview.countChanged.connect(self.updateTraceCount)
        self.ui.trackview.hintRequested.connect(self.setHint)

        # when the auto-parameter editor is toggled show/hide changes the edit mode of the StimulusView
        self.ui.parametizer.visibilityChanged.connect(self.ui.trackview.setMode)
        self.ui.parametizer.visibilityChanged.connect(self.setModeLabel)
        self.ui.parametizer.hintRequested.connect(self.setHint)

        for label in self.ui.templateBox.labels():
            label.dragActive.connect(self.ui.trackview.showBorder)

        self.ok = self.ui.okBtn

    def setModel(self, model):
        """Sets the QStimulusModel *model* for the StimulusView"""
        # disconnect old signals
        try:
            self.ui.parametizer.randomizeCkbx.toggled.disconnect()
            self.ui.parametizer.randomizeCkbx.disconnect()
        except TypeError:
            # disconnecting without any current connections throws error
            pass

        self.ui.trackview.setModel(model)
        self.ui.nrepsSpnbx.setValue(model.repCount())

        self.ui.parametizer.randomizeCkbx.toggled.connect(model.randomToggle)
        self.ui.parametizer.randomizeCkbx.setChecked(bool(model.reorder()))

        # extract the QAutoParameterModel from the QStimulusModel and 
        # set in the AutoParameterView
        autoParamModel = model.autoParams()
        self.ui.parametizer.setModel(autoParamModel)
        # whether the auto parameters are emtpy 
        # affects the enable-ness of the StimlusView
        autoParamModel.emptied.connect(self.ui.trackview.emptySelection)
        autoParamModel.countChanged.connect(self.updateTraceCount)
        self.updateTraceCount()

    def setRepCount(self, count):
        """Sets the repetition *count* for the stimulus model"""
        self._rep_default_cache[0] = count
        self.ui.trackview.model().setRepCount(count)

    @staticmethod
    def defaultReps():
        return StimulusEditor._rep_default_cache[0]

    def updateTraceCount(self):
        """Updates the trace count label with the data from the model"""
        self.ui.ntracesLbl.setNum(self.ui.trackview.model().traceCount())

    def preview(self):
        """Assemble the current components in the QStimulusModel and generate a spectrogram 
        plot in a separate window"""
        msg = self.ui.trackview.model().verify()
        if msg:
            answer = QtGui.QMessageBox.warning(self, "Bummer", 'Problem: {}.'.format(msg))
            return
        stim_signal, atten, ovld = self.ui.trackview.model().signal()
        fig = SpecWidget()
        fig.setWindowModality(2) # application modal
        fig.updateData(stim_signal, self.ui.trackview.model().samplerate())
        fig.setTitle('Stimulus Preview')
        fig.show()
        self.previewFig = fig

    def model(self):
        """Returns the QStimulusModel for this editor"""
        return self.ui.trackview.model()

    def setHint(self, message):
        """Sets the hint text to *message*"""
        self.ui.hintTxedt.setText(message)

    def setModeLabel(self, mode):
        if mode == 0:
            self.ui.modeLbl.setText("BUILDING MODE")
        else:
            self.ui.modeLbl.setText("AUTO-PARAMETER MODE")

    def closeEvent(self, event):
        super(StimulusEditor, self).closeEvent(event)
        model = self.ui.trackview.model()
        autoParamModel = model.autoParams()

        # disconnect model signals
        try:
            autoParamModel.emptied.disconnect()
            autoParamModel.countChanged.disconnect()
        except TypeError:
            pass



if __name__ == "__main__":
    import sys, os
    from sparkle.QtWrapper import QtGui
    from sparkle.gui.stim.qstimulus import QStimulusModel
    from sparkle.stim.stimulus_model import StimulusModel
    from sparkle.stim.types.stimuli_classes import *
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
    stim.insertEmptyRow()
    stim.insertComponent(vocal0, 1,0)

    stim.insertComponent(tone3, 1,0)
    # stim.insertComponent(silence0, (2,0))

    ptype = 'duration'
    start = .1
    step = .2
    stop = 1.0

    parameter_model = stim.autoParams()
    parameter_model.insertRow(0)
    # select first component
    parameter_model.toggleSelection(0, stim.component(0,0))
    # set values for autoparams
    parameter_model.setParamValue(0, start=start, step=step, 
                                  stop=stop, parameter=ptype)

    qstim = QStimulusModel(stim)
    editor = StimulusEditor()
    editor.setModel(qstim)

    # editor.ui.trackview.setModel(stim)

    editor.show()
    app.exec_()
