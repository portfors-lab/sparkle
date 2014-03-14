import logging
import numpy as np

from spikeylab.tools.util import create_unique_path
from spikeylab.main.protocol_acquisition import Experimenter
from spikeylab.stim.factory import CCFactory
from spikeylab.io.players import FinitePlayer
from spikeylab.tools.audiotools import spectrogram, calc_spectrum, get_fft_peak, calc_db

class CalibrationExperimenter(Experimenter):
    def __init__(self):
        super(CalibrationExperimenter, self).__init__()

        self.savefolder = None
        self.savename = None

        self.player = FinitePlayer()

        calibration_stimulus = self.protocol_model.data(self.protocol_model.index(0,0))
        CCFactory.init_stim(calibration_stimulus)

        save_data = True
        self.group_name = 'group_0'

    def set_save_params(self, savefolder, savename):
        """Folder and filename where raw experiment data will be saved to

        :param savefolder: folder for experiment data
        :type savefolder: str
        :param samename: filename template, without extention for individal experiment files
        :type savename: str
        """
        self.savefolder = savefolder
        self.savename = savename

    def stash_calibration(self, attenuations, freqs, frange):
        self.calibration_vector = attenuations
        self.calibration_freqs = freqs
        self.calibration_frange = frange

    def apply_calibration(self, apply_cal):
        self.apply_cal = apply_cal

    def set_duration(self, dur):
        self.protocol_model.data(self.protocol_model.index(0,0)).data(self.calibration_stimulus.index(0,0)).setDuration(dur)

    def _initialize_run(self):
        self.current_dataset_name = 'calibration'
        self.calibration_frequencies = []
        self.calibration_indexes = []
       
        if self.savefolder is None or self.savename is None:
            print "You must first set a save folder and filename"
        fname = create_unique_path(self.savefolder, self.savename)
        logger = logging.getLogger('main')
        logger.info('calibration file name %s' % fname)

        self.datafile = AcquisitionData(fname)

        info = {'samplerate_ad': self.player.aisr}
        self.datafile.set_metadata('', info)

        self.player.set_aochan(self.aochan)
        self.player.set_aichan(self.aichan)

        if self.apply_cal:
            self.protocol_model.setCalibration(self.calibration_vector, self.calibration_freqs, self.calibration_frange)
        else:
            self.protocol_model.setCalibration(None, None, None)

    def _initialize_test(self, test):
        test.setReorderFunc(self.reorder_traces)
        self.datafile.init_group(self.current_dataset_name)
        self.datafile.init_data(self.current_dataset_name, mode='calibration',
                                dims=(test.traceCount(), test.repCount()),
                                nested_name='fft_peaks')
        self.datafile.init_data(self.current_dataset_name, mode='calibration',
                                dims=(test.traceCount(), test.repCount()),
                                nested_name='vmax')

    def _process_response(self, response, trace_info, irep):
        freq, spectrum = calc_spectrum(recorded_tone, self.player.aisr)

        f = trace_info['components'][0]['frequency'] #only the one component (PureTone)
        db = trace_info['components'][0]['intensity']
        # print 'f', f, 'db', db
        if irep == 0:
            if db == self.caldb:
                self.calibration_frequencies.append(f)
                self.calibration_indexes.append(self.trace_counter)
            self.trace_counter +=1
            self.peak_avg = []
        
        # spec_max, max_freq = get_fft_peak(spectrum, freq)
        spec_peak_at_f = spectrum[freq == f]
        if len(spec_peak_at_f) != 1:
            print u"COULD NOT FIND TARGET FREQUENCY ",f
            print 'target', f, 'freqs', freq
            spec_peak_at_f = np.array([-1])
            # self._halt = True

        # vmax = np.amax(abs(recorded_tone))
        vmax = np.sqrt(np.mean(pow(recorded_tone,2)))*1.414 #rms

        self.datafile.append(self.current_dataset_name, spec_peak_at_f, 
                             nested_name='fft_peaks')
        self.datafile.append(self.current_dataset_name, np.array([vmax]), 
                             nested_name='vmax')

        self.signals.response_collected.emit(self.aitimes, recorded_tone)
        self.signals.calibration_response_collected.emit((f, db), spectrum, freq, spec_peak_at_f[0], vmax)
        
        # calculate resultant dB and emit
        self.peak_avg.append(vmax)
        if irep == self.nreps-1:
            mean_peak = np.mean(self.peak_avg)
            if f == self.calf and db == self.caldb:
                # this really needs to happend first
                self.calpeak = mean_peak
            resultdb = calc_db(vmax, self.calpeak) + self.caldb
            self.signals.average_response.emit(f, db, resultdb)

    def process_calibration(self, save=True):
        """processes the data gathered in a calibration run (does not work if multiple
            calibrations), returns resultant dB"""
        print 'process the calibration'
        dataset_name = 'calibration'

        vfunc = np.vectorize(calc_db)

        peaks = np.mean(abs(self.datafile.get('fft_peaks')), axis=1)
        vmaxes = np.mean(abs(self.datafile.get('vmax')), axis=1)

        # print 'calibration frequencies', self.calibration_frequencies
        cal_index = self.calibration_indexes[self.calibration_frequencies.index(self.calf)]

        cal_peak = peaks[cal_index]
        cal_vmax = vmaxes[cal_index]

        # print 'vfunc inputs', vmaxes, self.caldb, cal_vmax
        resultant_dB = vfunc(vmaxes, cal_vmax) * -1 #db attenuation
        # print 'results', resultant_dB

        print 'calibration frequences', self.calibration_frequencies, 'indexes', self.calibration_indexes
        print 'resultant_dB', resultant_dB

        print 'The maximum dB SPL is', max(resultant_dB)

        calibration_vector = resultant_dB[self.calibration_indexes].squeeze()
        # save a vector of only the calibration intensity results
        fname = self.datafile.filename
        if save:
            self.datafile.init_data(dataset_name, mode='calibration',
                                    dims=calibration_vector.shape,
                                    nested_name='calibration_intensities')
            self.datafile.append(dataset_name, calibration_vector,
                                 nested_name='calibration_intensities')

            relevant_info = {'frequencies':self.calibration_frequencies, 'calibration_dB':self.caldb,
                             'calibration_voltage': self.calv}
            self.datafile.set_metadata(u'calibration_intensities',
                                       relevant_info)
            self.datafile.close()
            self.signals.calibration_file_changed.emit(fname)
            print 'finished calibration :))))))))'
        else:
            # delete the data saved to file thus far.
            self.datafile.close()
            os.remove(fname)
            print 'calibration aborted'
        return resultant_dB, fname

    def reorder_traces(self, doclist):
        # Pick out the calibration frequency and put it first
        order = range(len(doclist))
        for i, trace in enumerate(doclist):
            if trace['components'][0]['frequency'] == self.calf and trace['components'][0]['intensity'] == self.caldb:
                order.pop(i)
                order.insert(0,i)
                return order
        else:
            #did not find calibration frequency, raise Error
            raise Exception('calibration frequency and intensity not found in stimulus')