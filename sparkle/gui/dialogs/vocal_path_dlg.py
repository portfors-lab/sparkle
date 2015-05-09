import os

from sparkle.QtWrapper import QtCore, QtGui
from vocal_path_dlg_form import Ui_VocalPathDialog


class VocalPathDialog(QtGui.QDialog):
    """Dialog for collecting user comments per protocol run"""
    def __init__(self, paths=[]):
        super(VocalPathDialog, self).__init__()
        self.ui = Ui_VocalPathDialog()
        self.ui.setupUi(self)

        self.setWindowTitle("Set Stimulus file locations")

        root_dir = os.path.abspath(os.sep)
        self.dirmodel = QtGui.QFileSystemModel(self)
        self.dirmodel.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllDirs)
        self.ui.filetreeView.setModel(self.dirmodel)
        self.ui.filetreeView.setRootIndex(self.dirmodel.setRootPath(root_dir))
        self.ui.filetreeView.hideColumn(1)
        self.ui.filetreeView.hideColumn(2)
        self.ui.filetreeView.hideColumn(3)
        self.ui.filetreeView.header().setResizeMode(0, QtGui.QHeaderView.Stretch) 

        self.ui.addBtn.clicked.connect(self.addPath)
        self.ui.removeBtn.clicked.connect(self.removePath)

        self.ui.filelist.addItems(paths)            

    def addPath(self):
        allselected = self.ui.filetreeView.selectedIndexes()
        for selected in allselected:
            spath = self.dirmodel.fileInfo(selected).absoluteFilePath()
            # check to see that path is not a duplicate
            if not self.ui.filelist.findItems(spath, QtCore.Qt.MatchExactly):
                self.ui.filelist.addItem(spath)

    def removePath(self):
        allselected = self.ui.filelist.selectedIndexes()
        for selected in allselected:
            self.ui.filelist.takeItem(selected.row())

    def paths(self):
        paths = []
        for idx in range(self.ui.filelist.count()):
            paths.append(str(self.ui.filelist.item(idx).text()))

        return paths
