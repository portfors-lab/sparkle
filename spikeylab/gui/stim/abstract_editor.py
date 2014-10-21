import sip
from QtWrapper import QtGui, QtCore

class AbstractEditorWidget(QtGui.QWidget):
    """Abstract class to share class variables for all editor widgets,
    mainly for the purpose of managing scaling changes across the GUI"""
    scales = [0.001, 1000] # time, frequency scaling factors
    """Default values for time, frequency"""
    # holds a reference to all frequency and time fields and labels
    # so they can be updated if a scaling change occurs
    funit_labels = [] 
    tunit_labels = []
    funit_fields = []
    tunit_fields = []
    valueChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super(AbstractEditorWidget, self).__init__(parent)
        self.setWindowModality(QtCore.Qt.ApplicationModal)

    @staticmethod
    def purgeDeletedWidgets():
        """Finds old references to unit labels and deletes them"""
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

