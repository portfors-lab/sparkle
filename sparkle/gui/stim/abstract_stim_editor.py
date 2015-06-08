import json
import os

from sparkle.QtWrapper import QtGui
from sparkle.gui.stim.abstract_editor import AbstractEditorWidget


class AbstractStimulusWidget(AbstractEditorWidget):
    """Abstract class for editors for :class:`QStimulusModels<sparkle.gui.stim.qstimulus.QStimulusModel>`"""
    saveFolder = os.path.expanduser('~')
    ok = None # must be implemented as a QPushButton to accept the edits
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
        """Returns the model for which this editor is acting on

        Must be implemented by subclass

        :returns: :class:`QStimulusModel<sparkle.gui.stim.qstimulus.QStimulusModel>`
        """
        raise NotImplementedError


    def setModel(self, model):
        """Sets the model for this editor
        
        Must be implemented by subclass

        :param model: Stimulus to edit
        :type model: :class:`QStimulusModel<sparkle.gui.stim.qstimulus.QStimulusModel>`
        """
        raise NotImplementedError

    def closeEvent(self, event):
        """Verifies the stimulus before closing, warns user with a
        dialog if there are any problems"""
        self.ok.setText("Checking...")
        QtGui.QApplication.processEvents()
        self.model().cleanComponents()
        self.model().purgeAutoSelected()
        msg = self.model().verify()
        if not msg:
            msg = self.model().warning()
        if msg:
            warnBox = QtGui.QMessageBox( QtGui.QMessageBox.Warning, 'Warning - Invalid Settings', '{}. Do you want to change this?'.format(msg) )
            yesButton = warnBox.addButton(self.tr('Edit'), QtGui.QMessageBox.YesRole)
            noButton = warnBox.addButton(self.tr('Ignore'), QtGui.QMessageBox.NoRole)
            warnBox.exec_()
            if warnBox.clickedButton() == yesButton:
                event.ignore()
        self.ok.setText("OK")
