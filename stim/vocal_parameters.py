from vocal_parameters_form import Ui_VocalParameterWidget

from audiolab.tools.audiotools import spectrogram
from PyQt4 import QtGui, QtCore

class VocalParameterWidget(QtGui.QWidget, Ui_VocalParameterWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)

        self.tscale = 0.001 # display in ms
        self.fscale = 1000

        # grey out parameters determined by file, not to be altered by user
        self.common.dur_spnbx.setEnabled(False)
        self.common.risefall_spnbx.setEnabled(False)

    def setComponent(self, component):
        self.common.setFields(component)

        # set up wav file directory finder paths
        self.dirmodel = QtGui.QFileSystemModel(self)
        self.dirmodel.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllDirs)
        self.filetree_view.setModel(self.dirmodel)
        self.filetree_view.setRootIndex(self.dirmodel.setRootPath(component.browsedir(0)))
        self.filetree_view.hideColumn(1)
        self.filetree_view.hideColumn(2)
        self.filetree_view.header().setStretchLastSection(False)
        self.filetree_view.header().setResizeMode(0, QtGui.QHeaderView.Stretch) 

        self.filemodel = QtGui.QFileSystemModel(self)
        self.filemodel.setFilter(QtCore.QDir.Files)
        self.filelist_view.setModel(self.filemodel)
        self.filelist_view.setRootIndex(self.filemodel.setRootPath(component.browsedir(1)))

        self.current_wav_file = component.file()
        # spec, f, bins, fs = spectrogram(self.current_wav_file)
        # self.spec_preview.update_data(spec, xaxis=bins, yaxis=f)
        self.spec_preview.update_file(self.current_wav_file)

        self.wavrootdir_lnedt.setText(component.browsedir(0))

        self._component = component

    def saveToObject(self):
        self._component.setIntensity(self.common.intensityValue())
        self._component.setFile(self.current_wav_file)
        # self._component.setDuration(self.common.durationValue())
        # self._component.setSamplerate(self.common.samplerateValue())

        self._component.setBrowseDir(self.dirmodel.rootPath(),0)
        self._component.setBrowseDir(self.filemodel.rootPath(),1)

    def component(self):
        return self._component

    def browse_wavdirs(self):
        wavdir = QtGui.QFileDialog.getExistingDirectory(self, 'select root folder', self.wavrootdir)
        self.filetree_view.setRootIndex(self.dirmodel.setRootPath(wavdir))
        self.filelist_view.setRootIndex(self.filemodel.setRootPath(wavdir))
        self.wavrootdir_lnedt.setText(wavdir)

    def wavdir_selected(self, model_index):
        spath = self.dirmodel.fileInfo(model_index).absoluteFilePath()
        self.filelist_view.setRootIndex(self.filemodel.setRootPath(spath))

    def wavfile_selected(self, model_index):
        pass
    #     """ On double click of wav file, load into display """
    #     # display spectrogram of file
    #     spath = self.dirmodel.fileInfo(model_index).absoluteFilePath()
    #     spec, f, bins, fs = spectrogram(spath)
    #     self.ui.display.update_spec(spec, xaxis=bins, yaxis=f)

    #     sr, wavdata = wv.read(spath)
    #     freq, spectrum = calc_spectrum(wavdata,sr)

    #     self.ui.display.update_fft(freq, spectrum)
    #     t = np.linspace(0,(float(len(wavdata))/sr), len(wavdata))
    #     print 'stim time lims', t[0], t[-1]
    #     self.ui.display.update_signal(t, wavdata)

    #     self.current_wav_file = spath

    #     if self.ui.tab_group.currentWidget().objectName() == 'tab_explore':
    #         aochan = self.ui.aochan_box.currentText()
    #         aichan = self.ui.aichan_box.currentText()
    #         acq_rate = self.ui.aisr_spnbx.value()*self.fscale
    #         winsz = float(self.ui.windowsz_spnbx.value())*0.001
    #         self.acqmodel.set_explore_params(wavfile=self.current_wav_file, aochan=aochan, aichan=aichan,
    #                                          acqtime=winsz, aisr=acq_rate)
    #         print 'win size', winsz
    #         self.ui.display.set_xlimits((0,winsz))
    #     # self.current_gen_rate = sr
    #     # self.current_wav_signal = wavdata

    def wavfile_clicked(self, model_index):
        # display spectrogram of file
        spath = self.dirmodel.fileInfo(model_index).absoluteFilePath()
        # spec, f, bins, fs = spectrogram(spath)
        # self.spec_preview.update_data(spec,xaxis=bins,yaxis=f)
        dur = self.spec_preview.update_file(spath)
        self.common.setDuration(dur)
        self.current_wav_file = spath
