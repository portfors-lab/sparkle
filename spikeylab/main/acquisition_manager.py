import logging

from spikeylab.tools.util import create_unique_path
from spikeylab.data.dataobjects import AcquisitionData
from spikeylab.tools.qthreading import ProtocolSignals
from spikeylab.main.explore_acquisition import Explorer
from spikeylab.main.protocol_experimenter import ProtocolExperimenter
from spikeylab.main.chart_experimenter import ChartExperimenter
from spikeylab.main.calibration_experimenter_bs import CalibrationExperimenterBS
from spikeylab.main.calibration_experimenter import CalibrationExperimenter

class AcquisitionManager():
    def __init__(self):

        self.datafile = None
        self.savefolder = None
        self.savename = None

        self.signals = ProtocolSignals()

        self.explorer = Explorer(self.signals)
        self.protocoler =  ProtocolExperimenter(self.signals)
        self.bs_calibrator = CalibrationExperimenterBS(self.signals)
        self.tone_calibrator = CalibrationExperimenter(self.signals)
        self.charter = ChartExperimenter(self.signals)
        # charter should share protocol model with windowed
        self.charter.protocol_model = self.protocoler.protocol_model

        self.signals.samplerateChanged = self.explorer.stimulus.samplerateChanged
        self.selected_calibration_index = 0
        self.current_cellid = 0

    def increment_cellid(self):
        self.current_cellid +=1

    def stimuli_list(self):
        return self.explorer.stimuli_list()

    def set_calibration(self, datakey, calf=None, frange=None):
        if datakey is None:
            calibration_vector, calibration_freqs = None, None
        else:
            if calf is None:
                raise Exception('calibration reference frequency must be specified')    
            try:
                cal = self.datafile.get_calibration(datakey, calf)
            except:
                print "Error: unable to load calibration data from: ", datakey
                raise
            calibration_vector, calibration_freqs = cal
        print 'setting explore calibration'
        self.explorer.set_calibration(calibration_vector, calibration_freqs, frange, datakey)
        print 'setting protocol calibration'
        self.protocoler.set_calibration(calibration_vector, calibration_freqs, frange, datakey)
        print 'setting chart calibration'
        self.charter.set_calibration(calibration_vector, calibration_freqs, frange, datakey)
        print 'setting calibrator calibration'
        self.bs_calibrator.stash_calibration(calibration_vector, calibration_freqs, frange, datakey)
        print 'setting tone calibrator calibration'
        self.tone_calibrator.stash_calibration(calibration_vector, calibration_freqs, frange, datakey)

    def current_calibration(self):
        return self.bs_calibrator.stashed_calibration()

    def set_calibration_duration(self, dur):
        self.bs_calibrator.set_duration(dur)
        self.tone_calibrator.set_duration(dur)

    def set_calibration_reps(self, reps):
        self.bs_calibrator.set_reps(reps)
        self.tone_calibrator.set_reps(reps)

    def create_data_file(self, fname=None):
        # find first available file name
        if fname is None:
            if self.savefolder is None or self.savename is None:
                print "You must first set a save folder and filename"
            fname = create_unique_path(self.savefolder, self.savename)
        self.datafile = AcquisitionData(fname)

        self.explorer.set_params(datafile=self.datafile)
        self.protocoler.set_params(datafile=self.datafile)
        self.charter.set_params(datafile=self.datafile)
        self.bs_calibrator.set_params(datafile=self.datafile)
        self.tone_calibrator.set_params(datafile=self.datafile)

        logger = logging.getLogger('main')
        logger.info('Opened datafile: {}'.format(fname))

        return fname

    def load_data_file(self, fname):
        self.datafile = AcquisitionData(fname, filemode='a')

        self.explorer.set_params(datafile=self.datafile)
        self.protocoler.set_params(datafile=self.datafile)
        self.charter.set_params(datafile=self.datafile)
        self.bs_calibrator.set_params(datafile=self.datafile)
        self.tone_calibrator.set_params(datafile=self.datafile)
        self.set_calibration(None)

        logger = logging.getLogger('main')
        logger.info('Opened datafile: {}'.format(fname))

    def current_data_file(self):
        return self.datafile.filename

    def set_threshold(self, threshold):
        """Spike detection threshold

        :param threshold: electrical potential to determine spikes (V)
        :type threshold: float
        """
        self.explorer.set_threshold(threshold)
        self.protocoler.set_threshold(threshold)

    def set_save_params(self, savefolder, savename):
        """Folder and filename where raw experiment data will be saved to

        :param savefolder: folder for experiment data
        :type savefolder: str
        :param samename: filename template, without extention for individal experiment files
        :type savename: str
        """
        self.savefolder = savefolder
        self.savename = savename

    def set_params(self, **kwargs):
        self.explorer.set_params(**kwargs)
        self.protocoler.set_params(**kwargs)
        self.bs_calibrator.set_params(**kwargs)
        self.tone_calibrator.set_params(**kwargs)
        self.charter.set_params(**kwargs)

    def set_stim_by_index(self, index):
        self.explorer.set_stim_by_index(index)

    def current_stim(self):
        return self.explorer.current_signal()

    def explore_stim_names(self):
        return self.explorer.stim_names()

    def run_explore(self, interval):
        return self.explorer.run(interval)

    def setup_protocol(self, interval):
        return self.protocoler.setup(interval)

    def protocol_total_count(self):
        return self.protocoler.count()

    def run_protocol(self):
        return self.protocoler.run()

    def set_calibration_by_index(self, idx):
        self.selected_calibration_index = idx

    def calibration_total_count(self):
        if self.selected_calibration_index == 2:
            return self.tone_calibrator.count()
        else:
            return self.bs_calibrator.count()

    def run_calibration(self, interval, applycal):
        if self.selected_calibration_index == 2:
            self.tone_calibrator.apply_calibration(applycal)
            self.tone_calibrator.setup(interval)
            return self.tone_calibrator.run()
        else:
            self.bs_calibrator.set_stim_by_index(self.selected_calibration_index)
            self.bs_calibrator.apply_calibration(applycal)
            self.bs_calibrator.setup(interval)
            return self.bs_calibrator.run()

    def start_chart(self):
        self.charter.start_chart()

    def stop_chart(self):
        self.charter.stop_chart()

    def run_chart_protocol(self, interval):
        self.charter.setup(interval)
        return self.charter.run()

    def process_calibration(self, save=True, calf=20000):
        if self.selected_calibration_index == 2:
            results, calname, freq = self.tone_calibrator.process_calibration(save)
        else:
            results, calname, freq = self.bs_calibrator.process_calibration(save)
        return calname

    def halt(self):
        """Halt any/all running operations"""
        self.explorer.halt()
        self.protocoler.halt()
        self.bs_calibrator.halt()
        self.tone_calibrator.halt()
        self.charter.halt()

    def close_data(self):
        if self.datafile is not None:
            print 'closing datafile'
            self.datafile.close()

    def protocol_model(self):
        return self.protocoler.protocol_model

    def calibration_stimulus(self, mode):
        if mode == 'tone':
            return self.tone_calibrator.stimulus
        elif mode =='noise':
            return self.bs_calibrator.stimulus

    def explore_genrate(self):
        return self.explorer.stimulus.samplerate()

    def calibration_genrate(self):
        return self.bs_calibrator.stimulus.samplerate()

    def calibration_range(self):
        return self.tone_calibrator.stimulus.autoParamRanges()

    def calibration_template(self):
        temp = {}
        temp['tone_doc'] = self.tone_calibrator.stimulus.templateDoc()
        comp_doc = []
        for calstim in self.bs_calibrator.get_stims():
            comp_doc.append(calstim.stateDict())
        temp['noise_doc'] = comp_doc
        return temp

    def load_calibration_template(self, template):
        self.tone_calibrator.stimulus.clearComponents()
        self.tone_calibrator.stimulus.loadFromTemplate(template['tone_doc'], self.tone_calibrator.stimulus)
        comp_doc = template['noise_doc']
        for state, calstim in zip(comp_doc, self.bs_calibrator.get_stims()):
            calstim.loadState(state)

    def clear_protocol(self):
        self.protocoler.clear()

    def set_group_comment(self, comment):
        """Sets a comment for the last executed protocol group"""
        self.protocoler.set_comment(self.current_cellid, comment)