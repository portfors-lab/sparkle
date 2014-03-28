import logging

from spikeylab.tools.util import create_unique_path
from spikeylab.data.dataobjects import AcquisitionData, load_calibration_file
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
        
    def stimuli_list(self):
        return self.explorer.stimuli_list()

    def set_calibration(self, cal_fname, calf=None, frange=None):
        if cal_fname is None:
            calibration_vector, calibration_freqs, frange = None, None, None
        else:    
            try:
                cal = load_calibration_file(cal_fname, calf)
            except:
                print "Error: unable to load calibration data from file: ", cal_fname
                raise
            calibration_vector, calibration_freqs = cal
        self.explorer.set_calibration(calibration_vector, calibration_freqs, frange)
        self.protocoler.set_calibration(calibration_vector, calibration_freqs, frange)
        self.charter.set_calibration(calibration_vector, calibration_freqs, frange)
        self.bs_calibrator.stash_calibration(calibration_vector, calibration_freqs, frange)
        self.tone_calibrator.stash_calibration(calibration_vector, calibration_freqs, frange)

    def set_calibration_duration(self, dur):
        self.bs_calibrator.set_duration(dur)
        self.tone_calibrator.set_duration(dur)

    def set_calibration_reps(self, reps):
        self.bs_calibrator.set_reps(reps)
        self.tone_calibrator.set_reps(reps)

    def create_data_file(self):
        # find first available file name
        if self.savefolder is None or self.savename is None:
            print "You must first set a save folder and filename"
        fname = create_unique_path(self.savefolder, self.savename)
        self.datafile = AcquisitionData(fname)

        self.explorer.set_params(datafile=self.datafile)
        self.protocoler.set_params(datafile=self.datafile)
        self.charter.set_params(datafile=self.datafile)

        logger = logging.getLogger('main')
        logger.info('Opened datafile: {}'.format(fname))

        return fname

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
        self.bs_calibrator.set_save_params(folder=self.savefolder)
        self.tone_calibrator.set_save_params(folder=self.savefolder)

    def set_calibration_file_name(self, savename):
        """Filename for which to save calibrations to"""
        self.bs_calibrator.set_save_params(folder=self.savefolder, name=savename)
        self.tone_calibrator.set_save_params(folder=self.savefolder, name=savename)

    def set_params(self, **kwargs):
        self.explorer.set_params(**kwargs)
        self.protocoler.set_params(**kwargs)
        self.bs_calibrator.set_params(**kwargs)
        self.tone_calibrator.set_params(**kwargs)
        self.charter.set_params(**kwargs)

    def set_stim_by_index(self, index):
        return self.explorer.set_stim_by_index(index)

    def current_stim(self):
        return self.explorer.current_signal()

    def explore_stim_names(self):
        return self.explorer.stim_names()

    def run_explore(self, interval):
        return self.explorer.run(interval)

    def setup_protocol(self, interval):
        return self.protocoler.setup(interval)

    def run_protocol(self):
        return self.protocoler.run()

    def set_calibration_by_index(self, idx):
        self.selected_calibration_index = idx

    def run_calibration(self, interval, applycal):
        if self.selected_calibration_index == 0:
            self.tone_calibrator.apply_calibration(applycal)
            self.tone_calibrator.setup(interval)
            return self.tone_calibrator.run()
        else:
            self.bs_calibrator.set_stim_by_index(self.selected_calibration_index-1)
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

    def process_calibration(self, save=True):
        if self.selected_calibration_index == 0:
            results, fname, freq = self.tone_calibrator.process_calibration(save)
        else:
            results, fname, freq = self.bs_calibrator.process_calibration(save)
        
        if save:
            self.set_calibration(fname, freq)
        return fname

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

    def explore_genrate(self):
        return self.explorer.stimulus.samplerate()

    def calibration_genrate(self):
        return self.bs_calibrator.stimulus.samplerate()

    def calibration_range(self):
        return self.tone_calibrator.stimulus.autoParamRanges()

    def calibration_template(self):
        return self.tone_calibrator.stimulus.templateDoc()

    def load_calibration_template(self, template):
        self.tone_calibrator.stimulus.clearComponents()
        self.tone_calibrator.stimulus.loadFromTemplate(template, self.calibrator.stimulus)
