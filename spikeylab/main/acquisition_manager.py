import logging

from spikeylab.tools.util import create_unique_path
from spikeylab.data.dataobjects import AcquisitionData, load_calibration_file


class AcquisitionManager():
    def __init__(self):

        self.datafile = None
        self.savefolder = None
        self.savename = None

        self.explorer = Explorer()
        self.protocoler =  ProtocolExperimenter()
        self.calibrator = CalibrationExperimenter()
        self.charter = ChartExperimenter()

    def stimuli_list(self):
        return self.explorer.stimuli_list()

    def set_calibration(self, cal_fname, frange=None):
        if cal_fname is None:
            calibration_vector, calibration_freqs, frange = None, None, None
        else:    
            try:
                cal = load_calibration_file(cal_fname)
            except:
                print "Error: unable to load calibration data from file: ", cal_fname
                raise
            calibration_vector, calibration_freqs = cal
        self.explorer.set_calibration(calibration_vector, calibration_freqs, frange)
        self.protocoler.set_calibration(calibration_vector, calibration_freqs, frange)
        self.charter.set_calibration(calibration_vector, calibration_freqs, frange)
        self.calibrator.stash_calibration(calibration_vector, calibration_freqs, frange)

    def set_calibration_duration(self, dur):
        self.calibrator.set_duration(dur)

    def create_data_file(self):
        # find first available file name
        if self.savefolder is None or self.savename is None:
            print "You must first set a save folder and filename"
        fname = create_unique_path(self.savefolder, self.savename)
        self.datafile = AcquisitionData(fname)

        self.explorer.set_params('datafile'=self.datafile)
        self.protocoler.set_params('datafile'=self.datafile)
        self.charter.set_params('datafile'=self.datafile)

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

    def set_calibration_file_name(self, savename):
        """Filename for which to save calibrations to"""
        self.calibrator.set_save_params(self.savefolder, savename)

    def set_params(self, **kwargs):
        self.explorer.set_params(**kwargs)
        self.protocoler.set_params(**kwargs)
        self.calibrator.set_params(**kwargs)
        self.charter.set_params(**kwargs)

    def set_stim_by_index(self, index):
        return self.explorer.set_stim_by_index(index)

    def current_stim(self):
        return self.explorer.current_signal()

    def explore_stim_names(self):
        return self.explorer.stim_names()

    def run_explore(self, interval):
        return self.explorer.run(interval)

    def run_protocol(self, interval):
        return self.protocoler.run(interval)

    def run_calibration(self, interval, applycal):
        self.calibrator.applycal(applycal)
        return self.calibrator.run(interval)

    def process_calibration(self, save=True):
        results, fname = self.calibrator.process_calibration(save)
        if save:
            self.set_calibration(fname)
        return results

    def close_data(self):
        if self.datafile is not None:
            self.datafile.close()