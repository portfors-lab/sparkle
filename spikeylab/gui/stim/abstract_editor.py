import os
import json

import sip
from PyQt4 import QtGui, QtCore

class AbstractEditorWidget(QtGui.QWidget):
    scales = [0.001, 1000] # time, frequency scaling factors
    funit_labels = []
    tunit_labels = []
    funit_fields = []
    tunit_fields = []
    valueChanged = QtCore.pyqtSignal()
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

    @staticmethod
    def purgeDeletedWidgets():

        toremove = []
        for label in AbstractEditorWidget.funit_labels:
            if sip.isdeleted(label):
                toremove.append(label)
        for label in toremove:
            AbstractEditorWidget.funit_labels.remove(label)

        toremove = []
        for label in AbstractEditorWidget.tunit_labels:
            if sip.isdeleted(label):
                toremove.append(label)
        for label in toremove:
            AbstractEditorWidget.tunit_labels.remove(label)

        toremove = []
        for field in AbstractEditorWidget.funit_fields:
            if sip.isdeleted(field):
                toremove.append(field)
        for field in toremove:
            AbstractEditorWidget.funit_fields.remove(field)

        toremove = []
        for field in AbstractEditorWidget.tunit_fields:
            if sip.isdeleted(field):
                toremove.append(field)
        for field in toremove:
            AbstractEditorWidget.tunit_fields.remove(field)
