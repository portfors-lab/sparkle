import sip

from sparkle.QtWrapper import QtCore, QtGui


class AbstractEditorWidget(QtGui.QFrame):
    """Abstract class to share class variables for all editor widgets,
    mainly for the purpose of managing scaling changes across the GUI"""
    _scales = ['ms', 'kHz'] # time, frequency scaling factors
    """Default values for time, frequency"""
    # holds a reference to all frequency and time fields and labels
    # so they can be updated if a scaling change occurs
    funit_fields = []
    tunit_fields = []
    valueChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super(AbstractEditorWidget, self).__init__(parent)
        self.setWindowModality(QtCore.Qt.ApplicationModal)

    @staticmethod
    def purgeDeletedWidgets():
        """Finds old references to stashed fields and deletes them"""
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

    @staticmethod
    def updateScales(tscale, fscale):
        AbstractEditorWidget._scales[0] = tscale
        AbstractEditorWidget._scales[1] = fscale
        