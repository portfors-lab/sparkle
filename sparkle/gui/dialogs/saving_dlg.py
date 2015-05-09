import os

from sparkle.QtWrapper import QtGui


class SavingDialog(QtGui.QFileDialog):
    """Dialog for setting the current data file"""
    def __init__(self, defaultFile=None, *args, **kwargs):
        super(SavingDialog, self).__init__(*args, **kwargs)
        self.setNameFilter("data files (*.hdf5 *.h5 *.pst *.raw)")
        self.setLabelText(QtGui.QFileDialog.Reject, 'Quit')
        self.setLabelText(QtGui.QFileDialog.Accept, '---')
        self.setWindowTitle("Select Data Save Location")

        # reverse engineer to get a hold of file name line edit
        layout = self.layout()
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if isinstance(item, QtGui.QWidgetItem):
                w = item.widget()
                if isinstance(w, QtGui.QLineEdit):
                    w.textChanged.connect(self.update_label)

        if defaultFile is not None:
            self.selectFile(defaultFile)
            self.setLabelText(QtGui.QFileDialog.Reject, 'Cancel')

    def update_label(self):
        """Updates the text on the accept button, to reflect if the 
        name of the data file will result in opening an existing file,
        or creating a new one"""
        current_file = str(self.selectedFiles()[0])
        if not '.' in current_file.split(os.path.sep)[-1]:
            # add hdf5 extention if none given
            current_file += '.hdf5'
        if os.path.isfile(current_file):
            self.setLabelText(QtGui.QFileDialog.Accept, 'Reload')
        elif os.path.isdir(current_file):
            self.setLabelText(QtGui.QFileDialog.Accept, 'Open')
        else:
            self.setLabelText(QtGui.QFileDialog.Accept, 'Create')

    def getfile(self):
        """Gets the full file path of the entered/selected file

        :returns: str -- the name of the data file to open/create
        """
        current_file = str(self.selectedFiles()[0])
        if os.path.isfile(current_file):
            print 'current_file', current_file
            if current_file.endswith('.raw') or current_file.endswith('.pst'):
                fmode = 'r'
            else:
                fmode = 'a'
        else:
            if not current_file.endswith('.hdf5') and not current_file.endswith('.h5'):
                current_file += '.hdf5'
            fmode = 'w-'
        return current_file, fmode
