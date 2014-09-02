import os
import json

from PyQt4 import QtGui

from spikeylab.gui.stim.abstract_editor import AbstractEditorWidget

class AbstractStimulusWidget(AbstractEditorWidget):

    saveFolder = os.path.expanduser('~')

    def saveStimulus(self):
        # manually instead of static function for testing purposes
        self.dialog = QtGui.QFileDialog(self, u"Save Stimulus Setup to File", 
                                    self.saveFolder, "Stimulus Settings (*.json)")
        self.dialog.setLabelText(QtGui.QFileDialog.Accept, 'Save')

        if self.dialog.exec_():
            fname = str(self.dialog.selectedFiles()[0])

            if fname is not None:
                if not fname.endswith('.json'):
                    fname = fname + '.json'
                template = self.model().templateDoc()
                with open(fname, 'w') as jf:
                    json.dump(template, jf)
        else:
            print 'stim not saved'

    def model(self):
        """Return the model for which this editor is acting on """
        raise NotImplementedError

    def closeEvent(self, event):
        self.ok.setText("Checking...")
        QtGui.QApplication.processEvents()
        self.model().cleanComponents()
        self.model().purgeAutoSelected()
        msg = self.model().verify()
        if not msg:
            msg = self.model().warning()
        if msg:
            answer = QtGui.QMessageBox.question(self, 'Oh Dear!', 
                                'Problem: {}. Do you want to deal with this?'.format(msg),
                                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if answer == QtGui.QMessageBox.Yes:
                event.ignore()
        self.ok.setText("OK")
