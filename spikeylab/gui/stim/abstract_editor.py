import sip
from PyQt4 import QtGui, QtCore

class AbstractEditorWidget(QtGui.QWidget):
    scales = [0.001, 1000] # time, frequency scaling factors
    funit_labels = []
    tunit_labels = []
    funit_fields = []
    tunit_fields = []
    valueChanged = QtCore.pyqtSignal()
    
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

