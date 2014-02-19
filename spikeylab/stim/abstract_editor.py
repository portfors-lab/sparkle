import os
import json

from PyQt4 import QtGui, QtCore

class AbstractEditorWidget(QtGui.QWidget):
    scales = [0.001, 1000] # time, frequency scaling factors
    funit_labels = []
    tunit_labels = []
    funit_fields = []
    tunit_fields = []
    valueChanged = QtCore.pyqtSignal()
    save_folder = os.path.expanduser('~')

    def setFScale(self, fscale, setup=False):
        """
        Updates the frequency unit labels, and stores unit to
        to convert input before returning values in correct scale.
        """
        oldscale = float(self.scales[1])
        self.scales[1] = fscale
        if fscale == 1000:
            for lbl in self.funit_labels:
                try:
                    lbl.setText('kHz')
                except:
                    pass
        elif fscale == 1:
            for lbl in self.funit_labels:
                try:
                    lbl.setText('Hz')
                except:
                    pass
        else:
            raise Exception(u"Invalid frequency scale:"+str(self.fscale))
        if not setup:
            for field in self.funit_fields:
                try:
                    field.setValue(field.value()*(oldscale/fscale))
                except:
                    pass

    def setTScale(self, tscale, setup=False):
        """
        Updates the time unit labels, and stores unit to
        to convert input before returning values in correct scale.
        """
        oldscale = float(self.scales[0])
        self.scales[0] = tscale
        if tscale == 0.001:
            for lbl in self.tunit_labels:
                try:
                    lbl.setText('ms')
                except:
                    pass
        elif tscale == 1:
            for lbl in self.tunit_labels:
                try:
                    lbl.setText('s')
                except:
                    pass
        else:
            raise Exception(u"Invalid time scale:"+str(self.tscale))

        if not setup:
            for field in self.tunit_fields:
                try:
                    field.setValue(field.value()*(oldscale/tscale))
                except:
                    pass

    def saveStimulus(self):
        # manually instead of static function for testing purposes
        self.dialog = QtGui.QFileDialog(self, u"Save Stimulus Setup to File", 
                                    self.save_folder, "Stimulus Settings (*.json)")
        self.dialog.setLabelText(QtGui.QFileDialog.Accept, 'Save')

        if self.dialog.exec_():
            fname = self.dialog.selectedFiles()[0]

        if fname is not None:
            if not fname.endswith('.json'):
                fname = fname + '.json'
            template = self.model().templateDoc()
            with open(fname, 'w') as jf:
                json.dump(template, jf)

    def model(self):
        """Return the model for which this editor is acting on """
        raise NotImplementedError