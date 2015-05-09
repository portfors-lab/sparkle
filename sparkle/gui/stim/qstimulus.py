import logging
import os
import uuid

import numpy as np
import yaml

from sparkle.QtWrapper import QtCore, QtGui
from sparkle.gui.qconstants import AutoParamMode, BuildMode, CursorRole
from sparkle.gui.stim.components.qcomponents import wrapComponent
from sparkle.gui.stim.qauto_parameter_model import QAutoParameterModel
from sparkle.resources import cursors
from sparkle.stim import get_stimulus_editor
from sparkle.stim.reorder import order_function
from sparkle.stim.stimulus_model import StimulusModel
from sparkle.stim.types import get_stimuli_models
from sparkle.tools.audiotools import convolve_filter, impulse_response
from sparkle.tools.systools import get_src_directory


class QStimulusModel(QtCore.QAbstractItemModel):
    """Qt wrapper for :class:`StimulusModel<sparkle.stim.stimulus_model.StimulusModel>`"""
    samplerateChanged = QtCore.Signal(int)
    def __init__(self, stim, parent=None):
        super(QStimulusModel, self).__init__(parent)

        self._autoParams = QAutoParameterModel(stim.autoParams()) # ?!
        self._stim = stim #StimulusModel
        if stim.stimType() is not None:
            self.setEditor(get_stimulus_editor(stim.stimType()))
        else:
            self.editor = None

    def setAutoParams(self, params):
        """Sets the QAutoParameterModel for this stimulus"""
        self._autoParams = params

    def autoParams(self):
        """Gets the QAutoParameterModel for this stimulus"""
        return self._autoParams

    def headerData(self, section, orientation, role):
        """Returns empty string. Required by view see :qtdoc:`subclassing<qabstractitemmodel.subclassing>`"""
        return ''

    def rowCount(self, parent=QtCore.QModelIndex()):
        """Determines the numbers of rows the view will draw

        Required by view, see :qtdoc:`subclassing<qabstractitemmodel.subclassing>`
        """
        return self._stim.rowCount()

    def columnCount(self, parent=QtCore.QModelIndex()):
        """Determines the numbers of columns the view will draw

        Required by view, see :qtdoc:`subclassing<qabstractitemmodel.subclassing>`
        """
        if parent.isValid():
            return self._stim.columnCount(parent.row())
        else:
            return self._stim.columnCount()

    def columnCountForRow(self, row):
        """Wrapper for :meth:`StimulusModel<sparkle.stim.stimulus_model.StimulusModel.columnCountForRow>`"""
        return self._stim.columnCountForRow(row)

    def componentCount(self):
        """Wrapper for :meth:`StimulusModel<sparkle.stim.stimulus_model.StimulusModel.componentCount>`"""
        return self._stim.componentCount()

    def repCount(self):
        """Wrapper for :meth:`StimulusModel<sparkle.stim.stimulus_model.StimulusModel.repCount>`"""
        return self._stim.repCount()

    def setRepCount(self, count):
        """Wrapper for :meth:`StimulusModel<sparkle.stim.stimulus_model.StimulusModel.setRepCount>`"""
        self._stim.setRepCount(count)

    def traceCount(self):
        """Wrapper for :meth:`StimulusModel<sparkle.stim.stimulus_model.StimulusModel.traceCount>`"""
        return self._stim.traceCount()

    def data(self, index, role=QtCore.Qt.UserRole, mode=BuildMode):
        """Used by the view to determine data to present

        See :qtdoc:`QAbstractItemModel<QAbstractItemModel.data>`, 
        and :qtdoc:`subclassing<qabstractitemmodel.subclassing>`
        """
        if role == CursorRole:
            if index.isValid():
                if mode == BuildMode:
                    return cursors.openHand()
                elif mode == AutoParamMode:
                    return cursors.pointyHand()
                else:
                    raise ValueError("Invalid stimulus edit mode")
            else:
                return QtGui.QCursor(QtCore.Qt.ArrowCursor)

        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            component = self._stim.component(index.row(),index.column())
            return component.__class__.__name__
        elif role == QtCore.Qt.SizeHintRole:
            component = self._stim.component(index.row(),index.column())
            return component.duration() #* PIXELS_PER_MS * 1000
        elif role == QtCore.Qt.UserRole or role == QtCore.Qt.UserRole+1:  #return the whole python object
            if self._stim.columnCountForRow(index.row()) > index.column():
                component = self._stim.component(index.row(),index.column())
                if role == QtCore.Qt.UserRole:
                    component = wrapComponent(component)
            else:
                component = None
            return component

    def index(self, row, col, parent=QtCore.QModelIndex()):
        """Creates an index. An item must exist for the given *row* 
        and *col*

        :returns: :qtdoc:`QModelIndex`
        """ 
        if row < self._stim.rowCount() and col < self._stim.columnCountForRow(row):
            component = self._stim.component(row, col)
            return self.createIndex(row, col, component)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        return QtCore.QModelIndex()
        
    def insertComponent(self, index, comp):
        """Inserts new component *comp* at index"""
        # new component needs to be wrapped
        if self.columnCountForRow(index.row()) == 0:
            self.beginInsertRows(QtCore.QModelIndex(), index.row(), index.row())
            self._stim.insertComponent(comp, index.row(), index.column())
            self.endInsertRows()
        else:
            self._stim.insertComponent(comp, index.row(), index.column())

        self.samplerateChanged.emit(self._stim.samplerate())

    def insertItem(self, index, comp):
        """Alias for `insertComponent`, as required by AbstractDragView"""
        self.insertComponent(index, comp)

    def removeComponent(self, index):
        """Removes the component at *index* from the model. If the two last
        rows are now empty, trims the last row."""
        if index.row() ==  self.rowCount() -1  and self.columnCountForRow(index.row()) == 1:
            self.beginRemoveRows(QtCore.QModelIndex(), self._stim.rowCount()-1, 
                                 self._stim.rowCount()-1)
            self._stim.removeComponent(index.row(), index.column())
            self.endRemoveRows()
        else:
            self._stim.removeComponent(index.row(), index.column())

        # this could have affected the sample of this stimulus
        self.samplerateChanged.emit(self._stim.samplerate())

    def removeItem(self, index):
        """Alias for removeComponent"""
        self._stim.removeComponent(index.row(), index.column())

    def indexByComponent(self, component):
        """return a QModelIndex for the given *component*, or None if
        it is not in the model"""
        return self.index(*self._stim.indexByComponent(component))

    def setData(self, index, value, role=QtCore.Qt.UserRole):
        """Sets the component at *index* to *value*"""
        # item must already exist at provided index
        self._stim.overwriteComponent(value, index.row(), index.column())

        self.samplerateChanged.emit(self.samplerate())

    def dataEdited(self):
        self.samplerateChanged.emit(self.samplerate())
        self._stim.updateCalibration()

    def flags(self, index):
        """"Determines interaction allowed with table cells.

        See :qtdoc:`QAbstractItemModel<QAbstractItemModel.flags>`, 
        and :qtdoc:`subclassing<qabstractitemmodel.subclassing>`
        """
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def setEditor(self, editor):
        """Sets the editor class for this Stimulus"""
        self.editor = editor
        self._stim.setStimType(editor.name)

    def showEditor(self):
        """Creates and shows an editor for this Stimulus"""
        if self.editor is not None:
            editor = self.editor()
            editor.setModel(self)
            return editor
        else:
            logger = logging.getLogger('main')
            logger.warning('Erm, no editor available :(')

    def signal(self):
        """Wrapper for :meth:`StimulusModel<sparkle.stim.stimulus_model.StimulusModel.signal>`"""
        return self._stim.signal()

    def samplerate(self):
        """Wrapper for :meth:`StimulusModel<sparkle.stim.stimulus_model.StimulusModel.samplerate>`"""
        return self._stim.samplerate()

    def duration(self):
        """Wrapper for :meth:`StimulusModel<sparkle.stim.stimulus_model.StimulusModel.duration>`"""
        return self._stim.duration()

    def randomToggle(self, randomize):
        """Sets the reorder function on this StimulusModel to a randomizer
        or none, alternately"""
        if randomize:
            self._stim.setReorderFunc(order_function('random'), 'random')
        else:
            self._stim.reorder = None

    def reorder(self):
        """Returns the reorder fucntion for this stimulus"""
        return self._stim.reorder

    def updateComponentStartVals(self):
        """Wrapper for :meth:`StimulusModel<sparkle.stim.stimulus_model.StimulusModel.updateComponentStartVals>`"""
        self._stim.updateComponentStartVals()
        # emit data changed signal
        # model.stimChanged.connect(view.dataChanged)

    @staticmethod
    def loadFromTemplate(template, stim=None):
        """Initialized this stimulus from a saved *template*

        :param template: doc from a previously stored stimulus via :class:`templateDoc`
        :type template: dict
        """
        stim = StimulusModel.loadFromTemplate(template, stim=stim)
        qstim = QStimulusModel(stim)
        qstim.setEditor(get_stimulus_editor(template['testtype']))
        return qstim

    def templateDoc(self):
        """Wrapper for :meth:`StimulusModel<sparkle.stim.stimulus_model.StimulusModel.templateDoc>`"""
        doc = self._stim.templateDoc()
        return doc

    def warning(self):
        """Wrapper for :meth:`StimulusModel<sparkle.stim.stimulus_model.StimulusModel.warning>`"""
        return self._stim.warning()

    def verify(self):
        """Wrapper for :meth:`StimulusModel<sparkle.stim.stimulus_model.StimulusModel.verify>`"""
        return self._stim.verify()

    def purgeAutoSelected(self):
        """Wrapper for :meth:`StimulusModel<sparkle.stim.stimulus_model.StimulusModel.purgeAutoSelected>`"""
        self._stim.purgeAutoSelected()

    def cleanComponents(self):
        """Wrapper for :meth:`StimulusModel<sparkle.stim.stimulus_model.StimulusModel.cleanComponents>`"""
        #removes any cache Qt classes in underlying data
        self._stim.cleanComponents()
