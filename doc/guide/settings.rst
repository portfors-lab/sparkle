.. _settings:

Settings Configuration File
===========================

This file holds a number of settings that have been deemed semi-permanent. They have been obsured from the user, as they are unlikely to need to be changed often. This file resides in the top-most folder of the project, and is titled `settings.conf`. It is a YAML formatted file, with the following values:

* microphone_calibration_db -- The intensity that the microphone calibrator device ouputs.

* default_genrate -- The default samplerate for output, in Hz. This will be all stimuli, apart from stimuli based from recordings (e.g. vocalizations), which will be generated at the rate which they were recorded at.

* use_rms -- Where to use the root mean square value of audio signals to determine amplitude, used in intensity calculation. If this is false, absolute voltage peak is used.

* device_name -- Name of the National Instruments data acquistiion card to use

* max_voltage -- Maximum voltage that the program should try to output through the DAC card. Stimuli beyond this value will get scaled down.

* reference_voltage -- Voltage (V) to use for setting an intensity reference point in the program together with the reference frequency

* reference_frequency -- Frequency (Hz) to use for setting an intensity reference point in the program together with the reference voltage

* use_attenutaor -- whether an attenuator is available to assist in producing smaller signals