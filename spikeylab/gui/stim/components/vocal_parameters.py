from os.path import dirname

from PyQt4 import QtGui, QtCore

from vocal_parameters_form import Ui_VocalParameterWidget
from spikeylab.gui.stim.abstract_parameters import AbstractParameterWidget
from spikeylab.tools.audiotools import spectrogram

class VocalParameterWidget(AbstractParameterWidget, Ui_VocalParameterWidget):
    vocalFilesChanged = QtCore.pyqtSignal(object, list)
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)

        # grey out parameters determined by file, not to be altered by user
        self.common.durSpnbx.setEnabled(False)
        self.common.risefallSpnbx.setEnabled(False)
        # self.colormap_changed = self.ui.specPreview.colormap_changed
        self.common.valueChanged.connect(self.valueChanged.emit)
        self.inputWidgets = {'intensity': self.common.dbSpnbx}
        self.audioExtentions = ['wav']

    def setComponent(self, component):
        self.common.setFields(component)

        self.currentWavFile = component.file()
        if self.currentWavFile is not None:
            wav_parent_dir = dirname(self.currentWavFile)
        else:
            wav_parent_dir = component.browsedir()

        self.setRootDirs(component.browsedir(), wav_parent_dir)

        if self.currentWavFile is not None:

            self.filelistView.setCurrentIndex(self.filemodel.index(self.currentWavFile))
            dur = self.specPreview.fromFile(self.currentWavFile)
            self.common.setDuration(dur)

        self._component = component

    def setRootDirs(self, treeroot, listroot):
        # set up wav file directory finder paths
        self.dirmodel = QtGui.QFileSystemModel(self)
        self.dirmodel.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllDirs)
        self.filetreeView.setModel(self.dirmodel)
        self.filetreeView.setRootIndex(self.dirmodel.setRootPath(treeroot))
        self.filetreeView.setCurrentIndex(self.dirmodel.index(listroot))
        self.filetreeView.hideColumn(1)
        self.filetreeView.hideColumn(2)
        self.filetreeView.header().setStretchLastSection(False)
        self.filetreeView.header().setResizeMode(0, QtGui.QHeaderView.Stretch) 

        self.filemodel = QtGui.QFileSystemModel(self)
        self.filemodel.setFilter(QtCore.QDir.Files)
        filters = ['*.'+x for x in self.audioExtentions]
        self.filemodel.setNameFilters(filters)
        self.filelistView.setModel(self.filemodel)
        self.filelistView.setRootIndex(self.filemodel.setRootPath(listroot))

        self.wavrootdirLnedt.setText(treeroot)

    def getTreeRoot(self):
        return self.dirmodel.rootPath()

    def getListRoot(self):
        return self.filemodel.rootPath()

    def saveToObject(self):
        self._component.setIntensity(self.common.intensityValue())
        self._component.setFile(self.currentWavFile)
        self._component.setBrowseDir(str(self.dirmodel.rootPath()))

        self.attributesSaved.emit(self._component.__class__.__name__, self._component.stateDict())

        selected = self.filelistView.selectedIndexes()
        paths = []
        for idx in selected:
            paths.append(self.filemodel.filePath(idx))
        self.vocalFilesChanged.emit(self._component, paths)

    def component(self):
        return self._component

    def browseWavdirs(self):
        wavdir = QtGui.QFileDialog.getExistingDirectory(self, 'select root folder', self.wavrootdirLnedt.text())
        self.filetreeView.setRootIndex(self.dirmodel.setRootPath(wavdir))
        self.filelistView.setRootIndex(self.filemodel.setRootPath(wavdir))
        self.wavrootdirLnedt.setText(wavdir)

    def wavdirSelected(self, modelIndex):
        spath = self.dirmodel.fileInfo(modelIndex).absoluteFilePath()
        self.filelistView.setRootIndex(self.filemodel.setRootPath(spath))

    def wavfileClicked(self, modelIndex):
        # display spectrogram of file
        spath = str(self.dirmodel.fileInfo(modelIndex).absoluteFilePath())
        if not any(map(spath.lower().endswith, self.audioExtentions)):
            return # not an audio file

        dur = self.specPreview.fromFile(spath)
        self.common.setDuration(dur)
        self.currentWavFile = spath

    def setContentFocus(self):
        pass

    def setSpecArgs(self, *args, **kwargs):
        self.specPreview.setSpecArgs(*args, **kwargs)

    def updateColormap(self):
        self.specPreview.updateColormap()
