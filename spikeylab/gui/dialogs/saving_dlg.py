import os

from PyQt4 import QtGui

class SavingDialog(QtGui.QFileDialog):
    def __init__(self, defaultFile=None, *args, **kwargs):
        QtGui.QFileDialog.__init__(self, *args, **kwargs)
        self.setNameFilter("data files (*.hdf5 *.h5)")
        self.setLabelText(QtGui.QFileDialog.Reject, 'Quit')
        self.setLabelText(QtGui.QFileDialog.Accept, '---')
        self.setWindowTitle("Select Data Save Location")

        # reverse engineer to get a hold of file name line edit
        layout = self.layout()
        for i in range(layout.count()):
            try:
                w = layout.itemAt(i).widget()
                if isinstance(w, QtGui.QLineEdit):
                    w.textChanged.connect(self.update_label)
            except:
                # wasn't a widget
                pass

        if defaultFile is not None:
            self.selectFile(defaultFile)
            self.setLabelText(QtGui.QFileDialog.Reject, 'Cancel')

    def update_label(self):
        current_file = str(self.selectedFiles()[0])
        if not current_file.endswith('.hdf5') and not current_file.endswith('.h5'):
            current_file += '.hdf5'
        if os.path.isfile(current_file):
            self.setLabelText(QtGui.QFileDialog.Accept, 'Reload')
        elif os.path.isdir(current_file):
            self.setLabelText(QtGui.QFileDialog.Accept, 'Open')
        else:
            self.setLabelText(QtGui.QFileDialog.Accept, 'Create')

    def getfile(self):
        current_file = str(self.selectedFiles()[0])
        if not current_file.endswith('.hdf5') and not current_file.endswith('.h5'):
            current_file += '.hdf5'
        if os.path.isfile(current_file):
            fmode = 'a'
        else:
            fmode = 'w-'
        return current_file, fmode