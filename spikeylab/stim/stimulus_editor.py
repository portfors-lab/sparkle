import sip
sip.setapi('QVariant', 2)
sip.setapi('QString', 2)

from PyQt4 import QtGui

from stimeditor_form import Ui_StimulusEditor
from auto_parameters_editor import Parametizer
from spikeylab.stim.abstract_editor import AbstractEditorWidget

# from spikeylab.plotting.custom_plots import SpecWidget
from spikeylab.plotting.mpl_spec_widget import SpecWidget
from matplotlib import mlab

class StimulusEditor(AbstractEditorWidget):
    name = 'Rawr!'
    def __init__(self, parent=None):
        super(StimulusEditor,self).__init__(parent)
        self.ui = Ui_StimulusEditor()
        self.ui.setupUi(self)
        self.ui.trackview.installEventFilter(self.ui.template_box.trash())
        # self.setWindowModality(2) # application modal
    
    def setStimulusModel(self, model):
        self.ui.trackview.setModel(model)
        self.ui.aosr_spnbx.setValue(model.samplerate()/self.scales[1])
        self.ui.nreps_spnbx.setValue(model.repCount())
        model.samplerateChanged.connect(self.updateSamplerate)
        # parametizer grabs model from view
        self.ui.parametizer.setStimulusView(self.ui.trackview)

    def setRepCount(self, count):
        print 'set rep count'
        self.ui.trackview.model().setRepCount(count)

    def updateSamplerate(self, fs):
        # still need to handle units?!
        print 'updating to', fs/self.scales[1]
        self.ui.aosr_spnbx.setValue(fs/self.scales[1])

    def setModelSamplerate(self):
        fs = self.ui.aosr_spnbx.value()
        self.ui.trackview.model().setSamplerate(fs*self.scales[1])

    def preview(self):
        stim_signal, atten = self.ui.trackview.model().signal()
        # import matplotlib.pyplot as plt
        # nfft = 512
        # Pxx, freqs, bins, im = plt.specgram(stim_signal, NFFT=nfft, Fs=375000, noverlap=int(nfft*0.9),
        #                       pad_to=nfft*2)
        # # print fig, spec
        # plt.imshow(Pxx)
        # plt.show()

        fig = SpecWidget()
        fig.update_data(stim_signal, self.ui.trackview.model().samplerate())
        # fig.set_title('Stimulus Preview')
        fig.show()
        self.asdkjfasdfk = fig

    def signal(self):
        
        stim_signal_list = self.ui.trackview.model().expandedStim()
        stim_doc = self.ui.trackview.model().expandedDoc()
        print 'stim list', len(stim_list)
        print 'stim doc', stim_doc
        return stim_signal_list

if __name__ == "__main__":
    import sys, os
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