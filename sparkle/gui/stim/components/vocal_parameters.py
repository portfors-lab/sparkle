from os.path import dirname

from sparkle.QtWrapper import QtCore, QtGui
from sparkle.gui.stim.abstract_component_editor import AbstractComponentWidget
from sparkle.gui.stim.components.order_dlg import OrderDialog
from sparkle.tools.audiotools import spectrogram
from vocal_parameters_form import Ui_VocalParameterWidget


class VocalParameterWidget(AbstractComponentWidget, Ui_VocalParameterWidget):
    vocalFilesChanged = QtCore.Signal(object, list)
    def __init__(self, component, parent=None):
        super(VocalParameterWidget, self).__init__(parent)
        self.setupUi(self)

        # grey out parameters determined by file, not to be altered by user
        self.durSpnbx.setEnabled(False)
        self.risefallSpnbx.setEnabled(False)
        # self.colormap_changed = self.ui.specPreview.colormap_changed
        self.dbSpnbx.valueChanged.connect(self.valueChanged.emit)
        self.risefallSpnbx.valueChanged.connect(self.valueChanged.emit)
        self.durSpnbx.setKeyboardTracking(False)
        self.risefallSpnbx.setKeyboardTracking(False)

        details = component.auto_details()
        self.risefallSpnbx.setMinimum(details['risefall']['min'])
        self.risefallSpnbx.setMaximum(details['risefall']['max'])
        self.dbSpnbx.setMinimum(details['intensity']['min'])
        self.dbSpnbx.setMaximum(details['intensity']['max'])

        self.tunit_fields.append(self.durSpnbx)
        self.tunit_fields.append(self.risefallSpnbx)

        self.inputWidgets = {'intensity': self.dbSpnbx, 'risefall': self.risefallSpnbx}
        self.audioExtentions = ['wav', 'call1']
        # save old function so we can call it
        self.stashedSelectionChanged = self.filelistView.selectionChanged
        # but I want to hook up to this slot, as there is no signal
        self.filelistView.selectionChanged = self.fileSelectionChanged
        self.filelistView.doubleClicked.connect(self.valueChanged.emit)
        self.fileorder = []
        self.setComponent(component)
        
    def setComponent(self, component):
        self.dbSpnbx.setValue(component.intensity())
        self.risefallSpnbx.setValue(component.risefall())
        
        self.currentWavFile = component.file()
        if self.currentWavFile is not None:
            wav_parent_dir = dirname(self.currentWavFile)
        else:
            wav_parent_dir = component.browsedir()

        self.setRootDirs(component.browsedir(), wav_parent_dir)

        if self.currentWavFile is not None:

            self.filelistView.setCurrentIndex(self.filemodel.index(self.currentWavFile))
            dur = self.specPreview.fromFile(self.currentWavFile)
            self.durSpnbx.setValue(dur)

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
        self._component.setIntensity(self.dbSpnbx.value())
        if len(self.fileorder) > 0:
            self._component.setFile(self.fileorder[0])
        self._component.setBrowseDir(str(self.dirmodel.rootPath()))
        self._component.setRisefall(self.risefallSpnbx.value())

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
        # like super kinda -- call the original slot
        self.stashedSelectionChanged(selected, deselected)

        allselected = self.filelistView.selectedIndexes()
        # display spectrogram of (first) file
        allpaths = [str(self.filemodel.fileInfo(idx).absoluteFilePath()) for idx in allselected]
        spath = allpaths[0]
        if not any(map(spath.lower().endswith, self.audioExtentions)):
            return # not an audio file

        dur = self.specPreview.fromFile(spath)
        self.durSpnbx.setValue(dur)
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

    def updateColormap(self):
        self.specPreview.updateColormap()

    def setOrder(self):
        dlg = OrderDialog(self.fileorder)
        if dlg.exec_():
            self.fileorder = dlg.order()
