from os.path import dirname

from vocal_parameters_form import Ui_VocalParameterWidget
from spikeylab.stim.abstract_parameters import AbstractParameterWidget
from spikeylab.tools.audiotools import spectrogram
from PyQt4 import QtGui, QtCore

class VocalParameterWidget(AbstractParameterWidget, Ui_VocalParameterWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)

        # grey out parameters determined by file, not to be altered by user
        self.common.dur_spnbx.setEnabled(False)
        self.common.risefall_spnbx.setEnabled(False)
        # self.colormap_changed = self.ui.spec_preview.colormap_changed

    def setComponent(self, component):
        self.common.setFields(component)

        self.current_wav_file = component.file()
        if self.current_wav_file is not None:
            wav_parent_dir = dirname(self.current_wav_file)
        else:
            wav_parent_dir = component.browsedir()

        self.setRootDirs(component.browsedir(), wav_parent_dir)

        if self.current_wav_file is not None:

            self.filelist_view.setCurrentIndex(self.filemodel.index(self.current_wav_file))
            dur = self.spec_preview.from_file(self.current_wav_file)
            self.common.setDuration(dur)

        self._component = component

    def setRootDirs(self, treeroot, listroot):
        # set up wav file directory finder paths
        self.dirmodel = QtGui.QFileSystemModel(self)
        self.dirmodel.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllDirs)
        self.filetree_view.setModel(self.dirmodel)
        self.filetree_view.setRootIndex(self.dirmodel.setRootPath(treeroot))
        self.filetree_view.setCurrentIndex(self.dirmodel.index(listroot))
        self.filetree_view.hideColumn(1)
        self.filetree_view.hideColumn(2)
        self.filetree_view.header().setStretchLastSection(False)
        self.filetree_view.header().setResizeMode(0, QtGui.QHeaderView.Stretch) 

        self.filemodel = QtGui.QFileSystemModel(self)
        self.filemodel.setFilter(QtCore.QDir.Files)
        self.filelist_view.setModel(self.filemodel)
        self.filelist_view.setRootIndex(self.filemodel.setRootPath(listroot))

        self.wavrootdir_lnedt.setText(treeroot)

    def getTreeRoot(self):
        return self.dirmodel.rootPath()

    def getListRoot(self):
        return self.filemodel.rootPath()

    def saveToObject(self):
        self._component.setIntensity(self.common.intensityValue())
        self._component.setFile(self.current_wav_file)
        # self._component.setDuration(self.common.durationValue())
        # self._component.setSamplerate(self.common.samplerateValue())

        self._component.setBrowseDir(self.dirmodel.rootPath())

    def component(self):
        return self._component

    def browse_wavdirs(self):
        wavdir = QtGui.QFileDialog.getExistingDirectory(self, 'select root folder', self.wavrootdir_lnedt.text())
        self.filetree_view.setRootIndex(self.dirmodel.setRootPath(wavdir))
        self.filelist_view.setRootIndex(self.filemodel.setRootPath(wavdir))
        self.wavrootdir_lnedt.setText(wavdir)

    def wavdir_selected(self, model_index):
        spath = self.dirmodel.fileInfo(model_index).absoluteFilePath()
        self.filelist_view.setRootIndex(self.filemodel.setRootPath(spath))

    def wavfile_clicked(self, model_index):
        # display spectrogram of file
        spath = self.dirmodel.fileInfo(model_index).absoluteFilePath()
        dur = self.spec_preview.from_file(spath)
        self.common.setDuration(dur)
        self.current_wav_file = spath

    def setContentFocus(self):
        pass

    def set_spec_args(self, *args, **kwargs):
        self.spec_preview.set_spec_args(*args, **kwargs)

    def update_colormap(self):
        self.spec_preview.update_colormap()
