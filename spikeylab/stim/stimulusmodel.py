import os
import uuid
import logging
import copy

import yaml
import numpy as np

from spikeylab.stim.auto_parameter_model import AutoParameterModel
from spikeylab.tools.audiotools import impulse_response, convolve_filter
from spikeylab.stim.types import get_stimuli_models
from spikeylab.stim.reorder import order_function
from spikeylab.tools.systools import get_src_directory

src_dir = get_src_directory()
# print 'src_dir', src_dir
with open(os.path.join(src_dir,'settings.conf'), 'r') as yf:
    config = yaml.load(yf)
DEFAULT_SAMPLERATE = config['default_genrate']
MAXV = config['max_voltage']

class StimulusModel():
    """
    Model to represent any stimulus the system will present. 
    Holds all relevant parameters
    """
    kernelCache = {} # persistent across all existing StimulusModels
    def __init__(self):
        self._nreps = 1 # reps of each unique stimulus
        self._nloops = 1 # reps of entire expanded list of autoparams

        # 2D array of simulus components track number x component number
        self._segments = [[]]
        # add an empty place to place components into new track
        self._autoParams = AutoParameterModel()
        
        # reference for what voltage == what intensity
        self.calv = None
        self.caldb = None
        self.impulseResponse = None
        self.minv = 0.005

        self._attenuationVector = None
        self._calFrequencies = None
        self._calFrange = None

        self.stimid = uuid.uuid1()

        self.reorder = None
        self.reorderName = None
        self._userTag = '' # user enter tag
        self._stimType = None

    def setUserTag(self, tag):
        self._userTag = tag

    def userTag(self):
        return self._userTag

    def setStimType(self, t):
        self._stimType = t

    def stimType(self):
        return self._stimType

    def setReferenceVoltage(self, caldb, calv):
        # make sure these are python types, so json encoding doesn't get throw
        # error later
        self.caldb = caldb
        self.calv = calv

    def setCalibration(self, dbBoostArray, frequencies, frange):
        # use supplied array of intensity adjustment to adjust tone output
        if dbBoostArray is not None and frequencies is not None:
            logger = logging.getLogger('main')
            if dbBoostArray.shape != frequencies.shape:
                logger.debug("ERROR: calibration array and frequency array must have same dimensions")
                return
            if frange is None:
                frange = (frequencies[0], frequencies[-1])

            logger.debug('setting calibration with samplerate {}'.format(self.samplerate()))
            fs = self.samplerate()
            if fs in StimulusModel.kernelCache:
                logger.debug('---->using cached filter')
                self.impulseResponse = StimulusModel.kernelCache[fs]
            else:
                logger.debug('---->calculating new filter for fs {}'.format(fs))
                self.impulseResponse = impulse_response(fs, dbBoostArray, frequencies, frange)
                # mutable type so will affect data structure persistently
                StimulusModel.kernelCache[fs] = self.impulseResponse

            # calculate for the default samplerate, if not already, since
            # we are very likely to need it, and it's better to have this done
            # up front, than cause lag in the UI later
            if DEFAULT_SAMPLERATE not in StimulusModel.kernelCache:
                StimulusModel.kernelCache[DEFAULT_SAMPLERATE] = impulse_response(DEFAULT_SAMPLERATE, dbBoostArray, frequencies, frange)

            # hang on to these for re-calculating impulse response on samplerate change
            self._attenuationVector = dbBoostArray
            self._calFrequencies = frequencies
            self._calFrange = frange

        else:
            self.impulseResponse = None

    def updateCalibration(self):
        self.setCalibration(self._attenuationVector, self._calFrequencies, self._calFrange)

    @staticmethod
    def clearCache():
        StimulusModel.kernelCache = {}

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
        self._autoParams = params

    def autoParams(self):
        return self._autoParams

    def headerData(self, section, orientation, role):
        return ''

    def rowCount(self):
        return len(self._segments)

    def columnCount(self, row=None):
        if row is not None:
            wholerow = self._segments[row]
            return len(wholerow)
        else:
            column_lengths = [len(x) for x in self._segments]
            return max(column_lengths)

    def columnCountForRow(self, row):
        try:
            return len(self._segments[row])
        except IndexError:
            return None

    def componentCount(self):
        return sum([self.columnCountForRow(x) for x in range(self.rowCount())])

    def component(self, row, col):
        try:
            comp = self._segments[row][col]
        except:
            # invalid index
            print 'Invalid index'
            return None
        return comp

    def printStimulus(self):
        """This is for purposes of documenting what was presented"""

    def insertComponent(self, comp, row=0, col=0):
        if row > len(self._segments) -1:
            self.insertEmptyRow()
        self._segments[row].insert(col, comp)

        if comp.__class__.__name__ == 'Vocalization':
            if comp.samplerate() is not None:
                # update calibration
                self.updateCalibration()

    def overwriteComponent(self, comp, row, col):
        self._segments[row][col] = comp

        if comp.__class__.__name__ == 'Vocalization':
            if comp.samplerate() is not None:
                # update calibration
                self.updateCalibration()

    def insertEmptyRow(self):
        self._segments.append([])

    def removeLastRow(self):
        print 'remove last row'
        self._segments.pop(len(self._segments)-1)

    def removeComponent(self, row,col):
        self._segments[row].pop(col)

        if self.columnCountForRow(-2) == 0 and self.columnCountForRow(-1) == 0:
            self._segments.pop(len(self._segments)-1)

    def clearComponents(self):
        self._segments = [[]]
        # also clear auto parameters
        self._autoParams.clearParameters()

    def indexByComponent(self, component):
        """return a QModelIndex for the given component, or None if
        it is not in the model"""
        for row, rowcontents in enumerate(self._segments):
            if component in rowcontents:
                column = rowcontents.index(component)
                return (row, column)

    def traceCount(self):
        """The number of unique stimului for this stimulus object"""
        nsegs = sum([len(track) for track in self._segments])
        if nsegs == 0:
            return 0
        ntraces = 1
        for irow in range(self._autoParams.nrows()):
            ntraces = ntraces*self._autoParams.numSteps(irow)
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

    def purgeAutoSelected(self):
        params = self._autoParams.allData()
        for p in params:
            comps_to_remove = []
            for comp in p['selection']:
                if self.indexByComponent(comp) is None:
                    comps_to_remove.append(comp)
            for orphaned in comps_to_remove:
                p['selection'].remove(orphaned)

    def cleanComponents(self):
        for row in self._segments:
            for comp in row:
                comp.clean()

    def autoParamRanges(self):
        """Return the expanded auto parameters, individually"""
        return self._autoParams.ranges()
        # params = self._autoParams.allData()

        
    def expandFunction(self, func, args=[]):
        # initilize array to hold all varied parameters
        params = self._autoParams.allData()

        steps = self.autoParamRanges()
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
                for component in param['selection']:
                    # print 'setting component parameter {} to {}'.format(param['parameter'], varylist[itrace][ip])
                    component.set(param['parameter'], np.around(varylist[itrace][ip],4))
            # copy of current stim state, or go ahead and turn it into a signal?
            # so then would I want to formulate some doc here as well?
            stim_list.append(func(*args))

        # now reset the components to start value
        for ip, param in enumerate(params):
            for component in param['selection']:
                component.set(param['parameter'], varylist[0][ip])

        return stim_list

    def setReorderFunc(self, func, name=None):
        self.reorder = func
        self.reorderName = name

    def expandedStim(self):
        """
        Apply the autoparameters to this stimulus and return a list of
        the resulting stimuli, and a complimentary list of doc dictionaries
        """
        logger = logging.getLogger('main')
        logger.debug("Generating Expanded Stimulus")

        # 3 loops now -- could be done in one...
        signals = self.expandFunction(self.signal)
        docs = self.expandFunction(self.componentDoc)

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
        doc = dict(self.componentDoc(False).items() + self.testDoc().items())

        # go through auto-parameter selected components and use location index
        autoparams = copy.deepcopy(self._autoParams.allData())
        for p in autoparams:
            selection = p['selection']
            serializable_selection = []
            for component in selection:
                idx = self.indexByComponent(component)
                serializable_selection.append(idx)
            p['selection'] = serializable_selection

        doc['autoparameters'] = autoparams
        doc['reorder'] = self.reorderName
        return doc

    @staticmethod
    def loadFromTemplate(template, stim=None):
        if stim is None:
            stim = StimulusModel()
        stim.setRepCount(template['reps'])
        stim.setUserTag(template.get('user_tag', ''))
        # don't set calibration details - this should be the same application wide
        component_classes = get_stimuli_models()
        for comp_doc in template['components']:
            comp = get_component(comp_doc['stim_type'], component_classes)
            comp.loadState(comp_doc) # ignore extra dict entries
            stim.insertComponent(comp, *comp_doc['index'])

        # revert from location based selection to component list
        autoparams = template['autoparameters']
        for p in autoparams:
            selection = p['selection']
            component_selection = []
            for index in selection:
                component = stim.component(*index)
                component_selection.append(component)
            p['selection'] = component_selection

        stim.autoParams().setParameterList(autoparams)
        stim.setReorderFunc(order_function(template['reorder']), template['reorder'])
        stim.setStimType(template['testtype'])
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
        # atten = self.caldb - max_db
        atten = 0
        # if max_db > self.caldb:
        #     raise Exception("Stimulus intensity over maxium")
        # print 'caldb:', self.caldb, 'max db:', max_db, 'atten:', atten, 'calv', self.calv
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

        total_signal = convolve_filter(total_signal, self.impulseResponse)

        undesired_attenuation = 0

        # sig_max = max(abs(total_signal))
        # if sig_max > self.calv:
        #     over_db = 20 * np.log10(sig_max/self.calv)
        #     allowance = float(min(over_db, atten))
        #     scalev = (10 ** (allowance/20)*self.calv)
        #     total_signal = total_signal/scalev
        #     print 'sigmax {}, over_db {}, allowance {}, scalev {}'.format(sig_max, over_db, allowance, scalev)
        #     atten -= allowance

        sig_max = np.max(abs(total_signal))
        if sig_max > MAXV:
            # scale stim down to outputable max
            total_signal = (total_signal/sig_max)*MAXV
            attenuated = 20 * np.log10(sig_max/MAXV)

            if attenuated <= atten:
                atten = atten - attenuated
            else:
                undesired_attenuation = attenuated - atten
                atten = 0
                logger = logging.getLogger('main')
                logger.warning("STIMULUS AMPLTIUDE {:.2f}V EXCEEDS MAXIMUM({}V), RESCALING. \
                    UNDESIRED ATTENUATION {:.2f}dB".format(sig_max, MAXV, undesired_attenuation))
        elif sig_max < self.minv and sig_max !=0:
            before_rms = np.sqrt(np.mean(pow(total_signal,2)))
            total_signal = (total_signal/sig_max)*self.minv
            after_rms = np.sqrt(np.mean(pow(total_signal,2)))
            attenuated = -20 * np.log10(before_rms/after_rms)
            # print 'signal below min, adding {} attenuation'.format(attenuated)
            atten += attenuated

        return total_signal, atten, undesired_attenuation

    def componentDoc(self, starttime=True):
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

        return {'samplerate_da':samplerate, 'components' : doc_list}

    def testDoc(self):
        return {'reps': self._nreps, 'user_tag': self._userTag,
                'calv': self.calv, 'caldb':self.caldb, 'testtype': self._stimType}

    def updateComponentStartVals(self):
        """Go through selected components for each auto parameter and set the start value"""
        for param in self._autoParams.allData():
            for component in param['selection']:
                component.set(param['parameter'], param['start'])

    def containsPval(self, paramName, value):
        """Returns true is the given value is in the auto parameters"""
        params = self._autoParams.allData()
        steps = self.autoParamRanges()
        pnames = [p['parameter'] for p in params]
        if paramName in pnames:
            pidx = pnames.index(paramName)
            return value in steps[pidx]
        else:
            return False

    def warning(self):
        signals, docs, overs = self.expandedStim()
        if np.any(np.array(overs) > 0):
            msg = 'Stimuli in this test are over the maximum allowable \
                voltage output. They will be rescaled with a maximum \
                undesired attenuation of {:.2f}dB.'.format(np.amax(overs))
            return msg
        return 0

    def verifyExpanded(self, samplerate):
        results = self.expandFunction(self.verifyComponents, args=(samplerate,))
        msg = [x for x in results if x]
        if len(msg) > 0:
            return msg[0]
        else:
            return 0

    def verifyComponents(self, samplerate):
        # flatten list of components
        components = [comp for track in self._segments for comp in track]
        for comp in components:
            msg = comp.verify(samplerate=samplerate)
            if msg:
                return msg
        return 0

    def verify(self, windowSize=None):
        msg = self._autoParams.verify()
        if msg:
            return msg
        if self.traceCount() == 0:
            return "Test is empty"
        if windowSize is not None:
            durations = self.expandFunction(self.duration)
            # ranges are linear, so we only need to test first and last
            if durations[0] > windowSize or durations[-1] > windowSize:
                return "Stimulus duration exceeds window duration"
        msg = self.verifyExpanded(self.samplerate())
        if msg:
            return msg
        if self.caldb is None or self.calv is None:
            return "Test reference voltage not set"
        return 0

    def __eq__(self, other):
        if self.stimid == other.stimid:
            return True
        else:
            return False


def get_component(comp_name, class_list):
    for comp_class in class_list:
        if comp_class.name == comp_name:
            return comp_class()
    else:
        return None
