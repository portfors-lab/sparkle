from PyQt4 import QtGui

class AbstractEditorWidget(QtGui.QWidget):
    scales = [0.001, 1000] # time, frequency scaling factors
    funit_labels = []
    tunit_labels = []
    funit_fields = []
    tunit_fields = []

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
