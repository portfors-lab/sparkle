import os, yaml
import uuid
import numpy as np

from spikeylab.stim.auto_parameter_model import AutoParameterModel
from spikeylab.tools.audiotools import calc_spectrum, smooth, calc_impulse_response, convolve_filter, tukey
from spikeylab.stim.types import get_stimuli_models
from spikeylab.stim import get_stimulus_editor
from spikeylab.stim.reorder import order_function
from spikeylab.tools.systools import get_src_directory

from PyQt4 import QtGui, QtCore

import matplotlib.pyplot as plt

src_dir = get_src_directory()
print 'src_dir', src_dir
with open(os.path.join(src_dir,'settings.conf'), 'r') as yf:
    config = yaml.load(yf)
DEFAULT_SAMPLERATE = config['default_genrate']
USE_RMS = config['use_rms']

class StimulusModel(QtCore.QAbstractItemModel):
    """
    Model to represent any stimulus the system will present. 
    Holds all relevant parameters
    """
    samplerateChanged = QtCore.pyqtSignal(int)
    kernel_cache = {} # persistent across all existing StimulusModels
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
        self.impulse_response = None
        self.maxv = 9.5
        self.minv = 0.005

        self._attenuation_vector = None
        self._cal_frequencies = None
        self._cal_frange = None

        self.stimid = uuid.uuid1()

        self.editor = None
        self.reorder = None
        self.reorder_name = None
        self.user_tag = '' # user enter tag

    def setUserTag(self, tag):
        self.user_tag = tag

    def userTag(self):
        return self.user_tag

    def setReferenceVoltage(self, caldb, calv):
        # make sure these are python types, so json encoding doesn't get throw
        # error later
        self.caldb = caldb
        self.calv = calv

    def setCalibration(self, db_boost_array, frequencies, frange):
        # use supplied array of intensity adjustment to adjust tone output
        if db_boost_array is not None and frequencies is not None:
            if db_boost_array.shape != frequencies.shape:
                print u"ERROR: calibration array and frequency array must have same dimensions"
                return
            if frange is None:
                frange = (frequencies[0], frequencies[-1])

            print 'setting calibration with samplerate', self.samplerate()
            fs = self.samplerate()
            if fs in StimulusModel.kernel_cache:
                print '---->using cached filter'
                self.impulse_response = StimulusModel.kernel_cache[fs]
            else:
                print '---->calculating new filter', self.kernel_cache
                self.impulse_response = calc_impulse_response(fs, db_boost_array, frequencies, frange)
                # mutable type so will affect data structure persistently
                StimulusModel.kernel_cache[fs] = self.impulse_response

            # calculate for the default samplerate, if not already, since
            # we are very likely to need it, and it's better to have this done
            # up front, than cause lag in the UI later
            if DEFAULT_SAMPLERATE not in StimulusModel.kernel_cache:
                StimulusModel.kernel_cache[DEFAULT_SAMPLERATE] = calc_impulse_response(DEFAULT_SAMPLERATE, db_boost_array, frequencies, frange)

            # hang on to these for re-calculating impulse response on samplerate change
            self._attenuation_vector = db_boost_array
            self._cal_frequencies = frequencies
            self._cal_frange = frange

        else:
            self.impulse_response = None

    def updateCalibration(self):
        self.setCalibration(self._attenuation_vector, self._cal_frequencies, self._cal_frange)

    @staticmethod
    def clear_cache():
        StimulusModel.kernel_cache = {}

    def setSamplerate(self, fs):
        raise Exception('attempting to set samplerate on fixed rate stimulus')

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

    def componentCount(self):
        return sum([self.columnCountForRow(x) for x in range(self.rowCount())])

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
                if role == QtCore.Qt.UserRole +1:
                    # filters out any qt classes to make serializable
                    component.clean()
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

        # this could have affected the sample of this stimulus
        self.samplerateChanged.emit(self.samplerate())


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
                # update calibration
                self.updateCalibration()
        self.samplerateChanged.emit(self.samplerate())

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
                start = p['start']
                stop = p['stop']
                if start > stop:
                    step = p['step']*-1
                else:
                    step = p['step']
                nsteps = np.ceil(np.around(abs(start - stop), 4) / p['step'])
                # print 'start, stop, steps', start, stop, nsteps
                # print 'linspace inputs', start, start+step*(nsteps-1), nsteps
                step_tmp = np.linspace(start, start+step*(nsteps-1), nsteps)
                if step_tmp[-1] != stop:
                    step_tmp = np.append(step_tmp,stop)
                # print 'step range', step_tmp
                steps.append(np.around(step_tmp,4))
            else:
                assert p['start'] == p['stop']
                steps.append([p['start']])

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
                    # print 'setting component parameter {} to {}'.format(param['parameter'], varylist[itrace][ip])
                    component.set(param['parameter'], np.around(varylist[itrace][ip],4))
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
        print "Getting expanded stim................................"
        # 3 loops now -- could be done in one...
        signals = self.expandFunction(self.signal)
        docs = self.expandFunction(self.doc)

        overloads = []
        for s, d in zip(signals, docs):
            d['overloaded_attenuation'] = s[2]
            overloads.append(s[2])

        # remove the undesired attenuation argument
        signals = [sig[0:2] for sig in signals]

        if self.reorder:
            order = self.reorder(docs)
            signals = [signals[i] for i in order]
            docs = [docs[i] for i in order]

        return signals, docs, overloads

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
        stim.setUserTag(template.get('user_tag', ''))
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
        # atten = self.caldb - max_db
        atten = 0
        if max_db > self.caldb:
            raise Exception("Stimulus intensity over maxium")
        # print 'caldb:', self.caldb, 'max db:', max_db, 'atten:', atten
        for track in self._segments:
            track_list = []
            for component in track:
                track_list.append(component.signal(fs=samplerate, 
                                                   atten=0, 
                                                   caldb=self.caldb, 
                                                   calv=self.calv))
            if len(track_list) > 0:   
                track_signals.append(np.hstack(track_list))

        # track_signals = sorted(track_signals, key=len, reverse=True)
        full_len = len(max(track_signals, key=len))
        total_signal = np.zeros((full_len,))
        for track in track_signals:
            total_signal[0:len(track)] += track

        total_signal = convolve_filter(total_signal, self.impulse_response)

        undesired_attenuation = 0

        maxv = self.maxv

        # sig_max = max(abs(total_signal))
        # if sig_max > self.calv:
        #     over_db = 20 * np.log10(sig_max/self.calv)
        #     allowance = float(min(over_db, atten))
        #     scalev = (10 ** (allowance/20)*self.calv)
        #     total_signal = total_signal/scalev
        #     print 'sigmax {}, over_db {}, allowance {}, scalev {}'.format(sig_max, over_db, allowance, scalev)
        #     atten -= allowance

        sig_max = np.max(abs(total_signal))
        if sig_max > maxv:
            # scale stim down to outputable max
            total_signal = (total_signal/sig_max)*maxv
            attenuated = 20 * np.log10(sig_max/maxv)

            if attenuated <= atten:
                atten = atten - attenuated
            else:
                undesired_attenuation = attenuated - atten
                atten = 0
                # log this, at least to console!
                print("WARNING: STIMULUS AMPLTIUDE {:.2f}V EXCEEDS MAXIMUM({}V), RESCALING. \
                    UNDESIRED ATTENUATION {:.2f}dB".format(sig_max, self.maxv, undesired_attenuation))
        elif sig_max < self.minv and sig_max !=0:
            before_rms = np.sqrt(np.mean(pow(total_signal,2)))
            total_signal = (total_signal/sig_max)*self.minv
            after_rms = np.sqrt(np.mean(pow(total_signal,2)))
            attenuated = -20 * np.log10(before_rms/after_rms)
            # print 'signal below min, adding {} attenuation'.format(attenuated)
            atten += attenuated

        return total_signal, atten, undesired_attenuation

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
        return {'samplerate_da':samplerate, 'reps': self._nreps, 'user_tag': self.user_tag,
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
