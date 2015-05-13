from sparkle.QtWrapper import QtGui
from specgram_dlg_form import Ui_SpecDialog


class SpecDialog(QtGui.QDialog):
    """Dialog for setting parameters for spectrogram calculation"""
    def __init__(self, parent=None, defaultVals=None):
        super(SpecDialog, self).__init__(parent)
        self.ui = Ui_SpecDialog()
        self.ui.setupUi(self)

        if defaultVals is not None:
            self.ui.nfftSpnbx.setValue(defaultVals[u'nfft'])
            funcs = [str(self.ui.windowCmbx.itemText(i)).lower() for i in xrange(self.ui.windowCmbx.count())]
            func_index = funcs.index(defaultVals[u'window'])
            self.ui.windowCmbx.setCurrentIndex(func_index)
            self.ui.overlapSpnbx.setValue(defaultVals['overlap'])

        # by not creating a copy, this may cause changes if the caller is using
        # the dict defaultVals
        self.vals = defaultVals

    def values(self):
        """Gets the parameter values

        :returns: dict of inputs:
        |        *'nfft'*: int -- length, in samples, of FFT chunks
        |        *'window'*: str -- name of window to apply to FFT chunks
        |        *'overlap'*: float -- percent overlap of windows 
        """
        self.vals['nfft'] = self.ui.nfftSpnbx.value()
        self.vals['window'] = str(self.ui.windowCmbx.currentText()).lower()
        self.vals['overlap'] = self.ui.overlapSpnbx.value()
        return self.vals
