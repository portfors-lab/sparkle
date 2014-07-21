import os, yaml
import uuid
import numpy as np
import logging

from spikeylab.stim.qauto_parameter_model import QAutoParameterModel
from spikeylab.tools.audiotools import impulse_response, convolve_filter
from spikeylab.stim.types import get_stimuli_models
from spikeylab.stim import get_stimulus_editor
from spikeylab.stim.reorder import order_function
from spikeylab.tools.systools import get_src_directory
from spikeylab.stim.stimulusmodel import StimulusModel

from PyQt4 import QtCore

src_dir = get_src_directory()
# print 'src_dir', src_dir
with open(os.path.join(src_dir,'settings.conf'), 'r') as yf:
    config = yaml.load(yf)
DEFAULT_SAMPLERATE = config['default_genrate']
MAXV = config['max_voltage']

class QStimulusModel(QtCore.QAbstractItemModel):
    """
    Model to represent any stimulus the system will present. 
    Holds all relevant parameters
    """
    samplerateChanged = QtCore.pyqtSignal(int)
    def __init__(self, stim, parent=None):
        QtCore.QAbstractItemModel.__init__(self, parent)

        self._autoParams = QAutoParameterModel(stim.autoParams()) # ?!
        self._stim = stim #StimulusModel
        if stim.stimType() is not None:
            self.setEditor(get_stimulus_editor(stim.stimType()))
        else:
            self.editor = None

    def setAutoParams(self, params):
        self._autoParams = params

    def autoParams(self):
        return self._autoParams

    def headerData(self, section, orientation, role):
        return ''

    def rowCount(self, parent=QtCore.QModelIndex()):
        return self._stim.rowCount()

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return self._stim.columnCount(parent.row())
        else:
            return self._stim.columnCount()

    def columnCountForRow(self, row):
        return self._stim.columnCountForRow(row)

    def componentCount(self):
        return self._stim.componentCount()

    def repCount(self):
        return self._stim.repCount()

    def setRepCount(self, count):
        self._stim.setRepCount(count)

    def traceCount(self):
        return self._stim.traceCount()

    def data(self, index, role=QtCore.Qt.UserRole):
        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            component = self._stim.component(index.row(),index.column())
            return component.__class__.__name__
        elif role == QtCore.Qt.SizeHintRole:
            component = self._stim.component(index.row(),index.column())
            return component.duration() #* PIXELS_PER_MS * 1000
        elif role >= QtCore.Qt.UserRole:  #return the whole python object
            if self._stim.columnCountForRow(index.row()) > index.column():
                component = self._stim.component(index.row(),index.column())
                if role == QtCore.Qt.UserRole +1:
                    # filters out any qt classes to make serializable
                    component.clean()
            else:
                component = None
            return component

    def printStimulus(self):
        """This is for purposes of documenting what was presented"""

    def index(self, row, col, parent=QtCore.QModelIndex()):
        if row < self._stim.rowCount() and col < self._stim.columnCountForRow(row):
            component = self._stim.component(row, col)
            return self.createIndex(row, col, component)
        else:
            return QtCore.QModelIndex()

    # def parentForRow(self, row):
    #     # get the whole row
    #     return self.createIndex(row, -1, self._segments[row])

    def parent(self, index):
        return QtCore.QModelIndex()
        
        # if index.column() == -1:
        #     return QtCore.QModelIndex()
        # else:
        #     print 'index', index.row(), index.column()
        #     raise Exception("No parents allowed!")
            # return self.createIndex(index.row(), -1, self._segments[index.row()])

    def insertComponent(self, index):
        comp = index.internalPointer()
        self._stim.insertComponent(comp, index.row(), index.column())

        if self.columnCountForRow(-1) > 0:
            self.beginInsertRows(QtCore.QModelIndex(), self._stim.rowCount(), self._stim.rowCount())
            self._stim.insertEmptyRow()
            self.endInsertRows()

        self.samplerateChanged.emit(self._stim.samplerate())

    def removeComponent(self, index):
        # parent = self.parentForRow(rowcol[0])

        # self.beginRemoveRows(parent, rowcol[1], rowcol[1])
        self._stim.removeComponent(index.row(), index.column())
        # self.endRemoveRows()

        if self.columnCountForRow(-2) == 0:
            self.beginRemoveRows(QtCore.QModelIndex(), self._stim.rowCount()-1, self._stim.rowCount()-1)
            self._stim.removeLastRow()
            self.endRemoveRows()

        # this could have affected the sample of this stimulus
        self.samplerateChanged.emit(self._stim.samplerate())


    def insertItem(self, index, item):
        self._stim.insertComponent(item, index.row(), index.column())

    def removeItem(self, index):
        self._stim.removeComponent(index.row(), index.column())

    def indexByComponent(self, component):
        """return a QModelIndex for the given component, or None if
        it is not in the model"""
        return self.index(*self._stim.indexByComponent(component))

    def setData(self, index, value, role=QtCore.Qt.UserRole):
        # item must already exist at provided index
        self._stim.overwriteComponent(value, index.row(), index.column())

        self.samplerateChanged.emit(self.samplerate())

    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def setEditor(self, editor):
        self.editor = editor
        self._stim.setStimType(editor.name)

    def showEditor(self):
        if self.editor is not None:
            editor = self.editor()
            editor.setStimulusModel(self)
            return editor
        else:
            logger = logging.getLogger('main')
            logger.warning('Erm, no editor available :(')

    def signal(self):
        return self._stim.signal()

    def samplerate(self):
        return self._stim.samplerate()

    def duration(self):
        return self._stim.duration()

    def randomToggle(self, randomize):
        if randomize:
            self._stim.setReorderFunc(order_function('random'), 'random')
        else:
            self._stim.reorder = None

    def reorder(self):
        return self._stim.reorder

    def updateComponentStartVals(self):
        self._stim.updateComponentStartVals()
        # emit data changed signal
        # model.stimChanged.connect(view.dataChanged)

    @staticmethod
    def loadFromTemplate(template, stim=None):
        stim = StimulusModel.loadFromTemplate(template, stim=stim)
        qstim = QStimulusModel(stim)
        qstim.setEditor(get_stimulus_editor(template['testtype']))
        return qstim

    def templateDoc(self):
        doc = self._stim.templateDoc()
        return doc

    def verify(self):
        return self._stim.verify()
