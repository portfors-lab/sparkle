import numpy as np
import uuid

from spikeylab.stim.auto_parameter_model import AutoParameterModel

from PyQt4 import QtGui, QtCore


class StimulusModel(QtCore.QAbstractItemModel):
    """
    Model to represent any stimulus the system will present. 
    Holds all relevant parameters
    """
    samplerateChanged = QtCore.pyqtSignal(int)
    def __init__(self, parent=None):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self._nreps = 1 # reps of each unique stimulus
        self._nloops = 1 # reps of entire expanded list of autoparams
        self._samplerate = 400000

        # 2D array of simulus components track number x component number
        self._segments = [[]]
        # add an empty place to place components into new track
        self._auto_params = AutoParameterModel(self)

        # reference for what voltage == what intensity
        self.calv = 0.1
        self.caldb = 100

        self.stimid = uuid.uuid1()

        self.editor = None

    def setSamplerate(self, fs):
        self._samplerate = fs

    def samplerate(self):
        return self._samplerate

    def setAutoParams(self, params):
        self._auto_params = params

    def autoParams(self):
        return self._auto_params

    def headerData(self, section, orientation, role):
        return ''

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._segments)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            print 'querying column count by parent'
            wholerow = parent.internalPointer()
            return len(wholerow)
        else:
            column_lengths = [len(x) for x in self._segments]
            return max(column_lengths)

    def columnCountForRow(self, row):
        return len(self._segments[row])

    def data(self, index, role):
        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            component = self._segments[index.row()][index.column()]
            return component.__class__.__name__
        elif role == QtCore.Qt.SizeHintRole:
            component = self._segments[index.row()][index.column()]
            return component.duration() #* PIXELS_PER_MS * 1000
        elif role >= QtCore.Qt.UserRole:  #return the whole python object
            if len(self._segments[index.row()]) > index.column():
                component = self._segments[index.row()][index.column()]
            else:
                component = None
            return component

    def printStimulus(self):
        """This is for purposes of documenting what was presented"""

    def index(self, row, col, parent=QtCore.QModelIndex()):
        # need to convert row, col to correct element, however still have heirarchy?
        if parent.isValid():
            print 'valid parent', parent.row(), parent.col()
            print 'Still trying to use tree!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            prow = self._segments.index(parent.internalPointer())
            return self.createIndex(prow, row, self._segments[prow][row])
        else:
            if row < len(self._segments) and col < len(self._segments[row]):
                return self.createIndex(row, col, self._segments[row][col])
            else:
                return QtCore.QModelIndex()

    def parentForRow(self, row):
        # get the whole row
        return self.createIndex(row, -1, self._segments[row])

    def parent(self, index):
        if index.column() == -1:
            return QtCore.QModelIndex()
        else:
            return self.createIndex(index.row(), -1, self._segments[index.row()])

    def insertComponent(self, comp, rowcol=(0,0)):
        # parent = self.parentForRow(rowcol[0])
        # convert to index or done already?
        # self.beginInsertRows(parent, rowcol[1], rowcol[1])
        # parent.internalPointer().insert(rowcol[1], comp)
        # self.endInsertRows()
        self._segments[rowcol[0]].insert(rowcol[1], None)
        self.setData(self.index(rowcol[0],rowcol[1]), comp)

        if len(self._segments[-1]) > 0:
            self.beginInsertRows(QtCore.QModelIndex(), len(self._segments), len(self._segments))
            self._segments.append([])
            self.endInsertRows()


    def removeComponent(self, rowcol):
        parent = self.parentForRow(rowcol[0])

        self.beginRemoveRows(parent, rowcol[1], rowcol[1])
        parent.internalPointer().pop(rowcol[1])
        self.endRemoveRows()

        if len(self._segments[-2]) == 0:
            self.beginRemoveRows(QtCore.QModelIndex(), len(self._segments)-1, len(self._segments)-1)
            self._segments.pop(len(self._segments)-1)
            self.endRemoveRows()

    def insertItem(self, index, item):
        self.insertComponent(item, (index.row(), index.column()))

    def removeItem(self, index):
        self.removeComponent((index.row(), index.column()))

    def clearComponents(self):
        self._segments = [[]]

    def indexByComponent(self, component):
        """return a QModelIndex for the given component, or None if
        it is not in the model"""
        for row, rowcontents in enumerate(self._segments):
            if component in rowcontents:
                column = rowcontents.index(component)
                return self.index(row, column)

    def setData(self, index, value, role=QtCore.Qt.UserRole):
        # item must already exist at provided index
        self._segments[index.row()][index.column()] = value

        if value.__class__.__name__ == 'Vocalization':
            rates = []
            for track in self._segments:
                for component in track:
                    # special case, where component is a wav file:
                    # it will set the master samplerate to match its own
                    if component.__class__.__name__ == 'Vocalization':
                        if component.samplerate() is not None:
                            rates.append(component.samplerate())

            if len(set(rates)) > 1:
                raise Exception("Wav files with different sample rates in same stimulus")
            if value.samplerate() is not None:
                self._samplerate = value.samplerate()
                print 'emitting samplerate change', value.samplerate()
                self.samplerateChanged.emit(value.samplerate())


    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def traceCount(self):
        """The number of unique stimului for this stimulus object"""
        nsegs = sum([len(track) for track in self._segments])
        if nsegs == 0:
            return 0
        params = self._auto_params.allData()
        steps = []
        ntraces = 1
        for p in params:
            steps.append(np.arange(p['start'], p['stop'], p['step']))
            ntraces = ntraces*len(steps[-1])
        return ntraces

    def loopCount(self):
        """The number of times to run through a set of autoparameters"""
        return self._nloops

    def setLoopCount(self, count):
        self._nloops = count

    def repCount(self):
        return self._nreps

    def setRepCount(self, count):
        self._nreps = count

    def contains(self, stimtype):
        for track in self._segments:
            for component in track:
                if component.__class__.__name__ == stimtype:
                    return True
        return False

    def expandFucntion(self, func):
        # initilize array to hold all varied parameters
        params = self._auto_params.allData()
        steps = []
        ntraces = 1
        for p in params:
            steps.append(np.arange(p['start'], p['stop'], p['step']))
            ntraces = ntraces*len(steps[-1])

        varylist = [[None for x in range(len(params))] for y in range(ntraces)]
        x = 1
        for iset, step_set in enumerate(steps):
            for itrace in range(ntraces):
                idx = (itrace / x) % len(step_set)
                varylist[itrace][iset] = step_set[idx]
            x = x*len(step_set)
            
        # now create the stimuli according to steps
        # go through list of modifing parameters, update this stimulus,
        # and then save current state to list
        stim_list = []
        for itrace in range(ntraces):
            for ip, param in enumerate(params):
                comp_inds = self._auto_params.selection(param)
                for index in comp_inds:
                    component = self.data(index, QtCore.Qt.UserRole)
                    component.set(param['parameter'], varylist[itrace][ip])
            # copy of current stim state, or go ahead and turn it into a signal?
            # so then would I want to formulate some doc here as well?
            stim_list.append(func())

        # now reset the components to start value
        for ip, param in enumerate(params):
            comp_inds = self._auto_params.selection(param)
            for index in comp_inds:
                component = self.data(index, QtCore.Qt.UserRole)
                component.set(param['parameter'], varylist[0][ip])

        return stim_list

    def expandedStim(self):
        """
        Apply the autoparameters to this stimulus and return a list of
        the resulting stimuli
        """
        stim_list = self.expandFucntion(self.signal)
        return stim_list

    def expandedDoc(self):
        """
        dictionary representation of exactly what was presented. 
        Contains only JSON compatable types
        """
        doc_list = self.expandFucntion(self.doc)
        return doc_list

    def templateDoc(self):
        """
        JSON/YAML/XML template to recreate this stimulus in another session
        """

    def signal(self):
        """Return the current stimulus in signal representation"""
        track_signals = []
        max_db = max([comp.intensity() for t in self._segments for comp in t])
        caldb = 100
        atten = caldb - max_db
        for track in self._segments:
            # nsamples = sum([comp.duration() for comp in track])*self.samplerate
            # track_signal = np.zeros((nsamples,))
            track_list = []
            for component in track:
                track_list.append(component.signal(self._samplerate, atten))
            if len(track_list) > 0:   
                track_signals.append(np.hstack(track_list))

        # track_signals = sorted(track_signals, key=len, reverse=True)
        full_len = len(max(track_signals, key=len))
        total_signal = np.zeros((full_len,))
        for track in track_signals:
            total_signal[0:len(track)] += track

        return total_signal, atten

    def doc(self):
        doc_list = []
        for track in self._segments:
            start_time = 0
            for component in track:
                info = component.stateDict()
                info['stim_type'] = component.name
                info['start_s'] = start_time
                start_time += info['duration']
                # must convert any numpy types to python types to be json serializable
                for key, value in info.items():
                    if type(value).__module__ == 'numpy':
                        info[key] = np.asscalar(value)
                doc_list.append(info)

        return {'samplerate_da':self._samplerate, 'reps': self._nreps, 

                'calv': self.calv, 'caldb':self.caldb, 'components': doc_list}

    def stimType(self):
        return self.editor.name

    def setEditor(self, editor):
        self.editor = editor

    def showEditor(self):
        if self.editor is not None:
            editor = self.editor()
            editor.setStimulusModel(self)
            return editor
        else:
            print 'Erm, no editor available :('