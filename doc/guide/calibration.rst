.. _calibration:

Speaker Calibration
===================

For the purposes of speaker frequency roll-off documentation and compensation.

The input fields are the same as for a :ref:`tuning_curve`. There are a bunch of metrics at the top, which you may or may not care about, that get updated as the program runs through the calibration curve. The calibration works by recording back a played tone, and calculating the achieved decibel level.

#. It is import to first get a verified decibel level at reference frequency. Place a microphone 10cm away from the speaker you are calibrating. Using the decibel meter, pick a frequency (a lower one) and decibel level, and adjust gain to make sure you are getting back the desired frequency.

#. Set the reference frequency and dB you used in the program under the menu *Options/Set Calibration...*. Here you also set the reference voltage, which you may want to change. This is the voltage level that the program will consider as necessary to generate the specified dB level. This dialog is also where you can set previous calibrations. If you are saving a calibration, it does not matter if a file is selected or not, it will create a new one.

#. Press the start button, the plot display will update to two FFT plots representing the stimulus generated and the recorded tone that was played back.

* Save calibration check box saves the calibration data to file, in the save folder location under the name 'calibration#.hdf5', where # is an incrementing number.

* If you are saving the calibration, it will be automatically set as the calibration for the program, when the calibration curve finishes. Of course, this doesn't actually do anything right now.

* a live plot of the recorded dB SPL values is generated in place of where the PSTH plot otherwise resides.

* Test calibration is not functional at this time, it won't do anything cool if you check it.

* If you abort the calibration before completion, it will not be saved.