import numpy as np
import uuid
from scipy.interpolate import interp1d

from spikeylab.stim.auto_parameter_model import AutoParameterModel
from spikeylab.tools.audiotools import calc_spectrum
from spikeylab.stim.types import get_stimuli_models
from spikeylab.stim import get_stimulus_editor
from spikeylab.stim.reorder import order_function

from PyQt4 import QtGui, QtCore

import matplotlib.pyplot as plt

DEFAULT_SAMPLERATE = 500000

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

        # 2D array of simulus components track number x component number
        self._segments = [[]]
        # add an empty place to place components into new track
        self._auto_params = AutoParameterModel(self)

        # reference for what voltage == what intensity
        self.calv = None
        self.caldb = None
        self.calibration_vector = None
        self.calibration_frequencies = None

        self.stimid = uuid.uuid1()

        self.editor = None
        self.reorder = None
        self.reorder_name = None

    def setReferenceVoltage(self, caldb, calv):
        # make sure these are python types, so json encoding doesn't get throw
        # error later
        self.caldb = caldb
        self.calv = calv

    def setCalibration(self, db_boost_array, frequencies):
        # use supplied array of intensity adjustment to adjust tone output
        if db_boost_array is not None and frequencies is not None and \
                            db_boost_array.shape != frequencies.shape:
            print u"ERROR: calibration array and frequency array must have same dimensions"
            return

        self.calibration_vector = db_boost_array
        self.calibration_frequencies = frequencies

    def setSamplerate(self, fs):
        print 'attempting to set samplerate on fixed rate stimulus'

    def samplerate(self):
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
        elif len(set(rates)) == 1:
            return rates[0]
        else:
            return DEFAULT_SAMPLERATE

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

    def data(self, index, role=QtCore.Qt.UserRole):
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
        # also clear auto parameters
        self._auto_params.clearParameters()

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
            if value.samplerate() is not None:
                # print 'emitting samplerate change', value.samplerate()
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
            if p['start'] > p['stop']:
                step = -1*p['step']
            else:
                step = p['step']
            if step == 0:
                if p['start'] == p['stop']:
                    step = 1
                else:
                    return 0
            ntraces = ntraces*(len(np.arange(p['start'], p['stop'], step)) + 1)
        return ntraces

    def loopCount(self):
        """The number of times to run through a set of autoparameters"""
        return self._nloops

    def setLoopCount(self, count):
        self._nloops = count

    def repCount(self):
        return self._nreps

    def setRepCount(self, count):
        if count > 0:
            self._nreps = count

    def contains(self, stimtype):
        for track in self._segments:
            for component in track:
                if component.__class__.__name__ == stimtype:
                    return True
        return False

    def autoParamRanges(self, params=None):
        """Return the expanded auto parameters, individually"""
        if params is None:
            params = self._auto_params.allData()

        steps = []
        for p in params:
            # inclusive range
            if p['step'] > 0:
                if p['start'] > p['stop']:
                    step = -1*p['step']
                else:
                    step = p['step']
            steps.append(np.append(np.arange(p['start'], p['stop'], step),p['stop']))

        return steps
        
    def expandFunction(self, func, args=[]):
        # initilize array to hold all varied parameters
        params = self._auto_params.allData()

        steps = self.autoParamRanges(params)
        ntraces = 1
        for p in steps:
            ntraces = ntraces*len(p)
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
            stim_list.append(func(*args))

        # now reset the components to start value
        for ip, param in enumerate(params):
            comp_inds = self._auto_params.selection(param)
            for index in comp_inds:
                component = self.data(index, QtCore.Qt.UserRole)
                component.set(param['parameter'], varylist[0][ip])


        return stim_list

    def setReorderFunc(self, func, name=None):
        self.reorder = func
        self.reorder_name = name

    def expandedStim(self):
        """
        Apply the autoparameters to this stimulus and return a list of
        the resulting stimuli, and a complimentary list of doc dictionaries
        """
        signals = self.expandFunction(self.signal)
        docs = self.expandFunction(self.doc)

        if self.reorder:
            order = self.reorder(docs)
            signals = [signals[i] for i in order]
            docs = [docs[i] for i in order]

        return signals, docs

    def templateDoc(self):
        """
        JSON/YAML/XML template to recreate this stimulus in another session
        """
        doc = self.doc(False)
        auto_parameter_doc = self._auto_params.doc()
        doc['autoparameters'] = auto_parameter_doc
        doc['reorder'] = self.reorder_name
        return doc

    @staticmethod
    def loadFromTemplate(template, stim=None):
        if stim is None:
            stim = StimulusModel()
        stim.setRepCount(template['reps'])
        # don't set calibration details - this should be the same application wide
        stim.setEditor(get_stimulus_editor(template['testtype']))
        component_classes = get_stimuli_models()
        for comp_doc in template['components']:
            comp = get_component(comp_doc['stim_type'], component_classes)
            comp.loadState(comp_doc) # ignore extra dict entries
            stim.insertComponent(comp, comp_doc['index'])

        AutoParameterModel.loadFromTemplate(template['autoparameters'], stim)
        stim.setReorderFunc(order_function(template['reorder']), template['reorder'])

        return stim

    def duration(self):
        durs = []
        for track in self._segments:
            durs.append(sum([comp.duration() for comp in track]))
            
        return max(durs)

    def signal(self):
        """Return the current stimulus in signal representation"""
        samplerate = self.samplerate()
        track_signals = []
        max_db = max([comp.intensity() for t in self._segments for comp in t])
        # everything is maxed up to calibration dB and attenuated from there
        atten = self.caldb - max_db
        if atten < 0:
            atten = 0
        # print 'caldb:', self.caldb, 'max db:', max_db, 'atten:', atten
        for track in self._segments:
            track_list = []
            for component in track:
                track_list.append(component.signal(fs=samplerate, 
                                                   atten=atten, 
                                                   caldb=self.caldb, 
                                                   calv=self.calv))
            if len(track_list) > 0:   
                track_signals.append(np.hstack(track_list))

        # track_signals = sorted(track_signals, key=len, reverse=True)
        full_len = len(max(track_signals, key=len))
        total_signal = np.zeros((full_len,))
        for track in track_signals:
            total_signal[0:len(track)] += track

        total_signal = self.apply_calibration(total_signal, samplerate)

        return total_signal, atten

    def apply_calibration(self, signal, fs):
        if self.calibration_vector is not None and self.calibration_frequencies is None :
            # calibration magic happens here!

            print 'applying transfer vector'
            original = signal
            X = np.fft.rfft(signal)
            frange = [50000, 100000]
            npts = len(signal)
            fs = self.samplerate()
            f = np.arange(npts/2+1)/(float(npts)/fs)
            f0 = np.where(f==frange[0])[0]
            f1 = np.where(f==frange[1])[0]
            # f2 = npts - f1
            # f3 = npts - f0
            print 'point values', X[f0], X[f1],# X[f2], X[f3], np.real(X[1:(npts/2)]).shape, np.real((X[(npts/2)+1:])[::-1]).shape
            # X[:f0] = X[:f0]*0
            # fq = np.arange(npts)/(float(npts)/fs)
            # X[f1:] = X[f1:]*0
            # print 'x symmetrical', np.all(np.real(X[1:(npts/2)]) == np.real((X[(npts/2)+1:])[::-1]))
            # print 'h symmetrical', np.real(self.calibration_vector[1:(npts/2)]) == np.real((self.calibration_vector[(npts/2)+1:])[::-1])
            XdeconvH = X.copy()
            XdeconvH[f0:f1].real /= self.calibration_vector[f0:f1]
            # XdeconvH[f2:f3] = X[f2:f3]/self.calibration_vector[f2:f3]
            # how do I get real values back from ifft??????
            print 'X shape', X.shape, f0, f1#, f2, f3
            # print 'xdivh symmetrical', np.real(XdeconvH[1:npts/2]) == np.real((XdeconvH[(npts/2)+1:])[::-1])
            # signal = np.fft.ifft(XdeconvH)
            adjusted_signal = np.fft.irfft(XdeconvH)


            plt.figure()
            plt.subplot(211)
            plt.plot(np.real(X))
            plt.subplot(212)
            plt.plot(np.imag(X))
            fig = plt.figure()
            plt.subplot(211)
            plt.plot(f, np.real(XdeconvH))
            plt.subplot(212)
            plt.plot(f, np.imag(XdeconvH))
            plt.title("adjusted")
            plt.show()

            return adjusted_signal

        elif self.calibration_vector is not None and self.calibration_frequencies is not None :
            print 'interpolated calibration', self.calibration_frequencies
            X = np.fft.rfft(signal)
            frange = [5000, 100000]
            npts = len(signal)
            fs = self.samplerate()
            f = np.arange(npts/2+1)/(float(npts)/fs)
            f0 = (np.abs(f-frange[0])).argmin()
            f1 = (np.abs(f-frange[1])).argmin()

            cal_func = interp1d(self.calibration_frequencies, self.calibration_vector)
            frange = f[f0:f1]
            H = cal_func(frange)
            # convert to voltage scalar
            # change calibration  vector to attenuation, and remove 100 - H
            H = 10**((100 - H).astype(float)/20)
            # print H.shape, X.shape
            Xadjusted = X.copy()
            Xadjusted[f0:f1] *= H

            adjusted_signal = np.fft.irfft(Xadjusted)

            # plt.figure()
            # plt.subplot(211)
            # plt.plot(f, np.real(X))
            # plt.subplot(212)
            # plt.plot(frange, H)
            # fig = plt.figure()
            # plt.subplot(211)
            # plt.plot(f, np.real(Xadjusted))
            # plt.subplot(212)
            # plt.plot(f, np.imag(Xadjusted))
            # plt.title("adjusted")
            # plt.show()

            return adjusted_signal
        else:
            return signal

    def doc(self, starttime=True):
        samplerate = self.samplerate()
        doc_list = []
        for row, track in enumerate(self._segments):
            start_time = 0
            for col, component in enumerate(track):
                info = component.stateDict()
                info['stim_type'] = component.name
                if starttime:
                    info['start_s'] = start_time
                else:
                    info['index'] = (row, col)
                start_time += info['duration']

                doc_list.append(info)

        if self.editor is not None:
            testtype = self.editor.name
        else:
            testtype = None
        return {'samplerate_da':samplerate, 'reps': self._nreps, 
                'calv': self.calv, 'caldb':self.caldb, 'components': doc_list,
                'testtype': testtype}

    def stimType(self):
        if self.editor is not None:
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

    def contains_pval(self, param_name, value):
        """Returns true is the given value is in the auto parameters"""
        params = self._auto_params.allData()
        steps = self.autoParamRanges(params)
        pnames = [p['parameter'] for p in params]
        if param_name in pnames:
            pidx = pnames.index(param_name)
            return value in steps[pidx]
        else:
            return False

    def verify_expanded(self, samplerate):
        results = self.expandFunction(self.verify_components, args=(samplerate,))
        msg = [x for x in results if x]
        if len(msg) > 0:
            return msg[0]
        else:
            return 0

    def verify_components(self, samplerate):
        # flatten list of components
        components = [comp for track in self._segments for comp in track]
        for comp in components:
            msg = comp.verify(samplerate=samplerate)
            if msg:
                return msg
        return 0

    def verify(self, window_size=None):
        msg = self._auto_params.verify()
        if msg:
            return msg
        if self.traceCount() == 0:
            return "Test is empty"
        if window_size is not None:
            durations = self.expandFunction(self.duration)
            # ranges are linear, so we only need to test first and last
            if durations[0] > window_size or durations[-1] > window_size:
                return "Stimulus duration exceeds window duration"
        msg = self.verify_expanded(self.samplerate())
        if msg:
            return msg
        if self.caldb is None or self.calv is None:
            return "Test reference voltage not set"
        return 0

def get_component(comp_name, class_list):
    for comp_class in class_list:
        if comp_class.name == comp_name:
            return comp_class()
    else:
        return None