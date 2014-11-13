from os.path import dirname

from QtWrapper import QtGui, QtCore

from vocal_parameters_form import Ui_VocalParameterWidget
from spikeylab.gui.stim.abstract_component_editor import AbstractComponentWidget
from spikeylab.tools.audiotools import spectrogram
from spikeylab.gui.stim.components.order_dlg import OrderDialog

class VocalParameterWidget(AbstractComponentWidget, Ui_VocalParameterWidget):
    vocalFilesChanged = QtCore.Signal(object, list)
    def __init__(self, component, parent=None):
        super(VocalParameterWidget, self).__init__(parent)
        self.setupUi(self)

        # grey out parameters determined by file, not to be altered by user
        self.common.durSpnbx.setEnabled(False)
        self.common.risefallSpnbx.setEnabled(False)
        # self.colormap_changed = self.ui.specPreview.colormap_changed
        self.common.valueChanged.connect(self.valueChanged.emit)
        self.inputWidgets = {'intensity': self.common.dbSpnbx}
        self.audioExtentions = ['wav', 'call1']
        # save old function so we can call it
        self.stashedSelectionChanged = self.filelistView.selectionChanged
        # but I want to hook up to this slot, as there is no signal
        self.filelistView.selectionChanged = self.fileSelectionChanged
        self.fileorder = []
        self.setComponent(component)
        
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

    def selectMany(self, paths):
        selection = self.filelistView.selectionModel()

        for path in paths:
            idx = self.filemodel.index(path)
            selection.select(idx, QtGui.QItemSelectionModel.Select)
        self.fileorder = paths

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
        if len(self.fileorder) > 0:
            self._component.setFile(self.fileorder[0])
        self._component.setBrowseDir(str(self.dirmodel.rootPath()))

        self.attributesSaved.emit(self._component.__class__.__name__, self._component.stateDict())

        selected = self.filelistView.selectedIndexes()
        paths = []
        for idx in selected:
            paths.append(str(self.filemodel.filePath(idx)))

        self.vocalFilesChanged.emit(self._component, self.fileorder)

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

    def fileSelectionChanged(self, selected, deselected):
        # like super kinda
        self.stashedSelectionChanged(selected, deselected)

        allselected = self.filelistView.selectedIndexes()
        # display spectrogram of file
        allpaths = [str(self.filemodel.fileInfo(idx).absoluteFilePath()) for idx in allselected]
        spath = allpaths[0]
        if not any(map(spath.lower().endswith, self.audioExtentions)):
            return # not an audio file

        dur = self.specPreview.fromFile(spath)
        self.common.setDuration(dur)
        self.currentWavFile = spath
        self.nfiles.setNum(len(allselected))

        if len(allselected) < 2:
            self.orderBtn.setEnabled(False)
        else:
            self.orderBtn.setEnabled(True)

        #remove deselected files from order
        self.fileorder = [x for x in self.fileorder if x in allpaths]

        # add any to file order not in it already
        for path in allpaths:
            if path not in self.fileorder:
                self.fileorder.append(path)

    def setContentFocus(self):
        pass

    def setSpecArgs(self, *args, **kwargs):
        self.specPreview.setSpecArgs(*args, **kwargs)

    def updateColormap(self):
        self.specPreview.updateColormap()

    def setOrder(self):
        dlg = OrderDialog(self.fileorder)
        if dlg.exec_():
            self.fileorder = dlg.order()