.. _calibration:

Speaker Calibration
===================

For the purposes of speaker frequency roll-off documentation and compensation.

#. First set up the hardware. 
    - From the AO channel you are using on the ADC/DAC BNC router, route the output signal to an amplifier, then to the attenutator, and then to the speaker.
    - Place the microphone exactly 10cm away from the speaker. The microphone is highly directional, it is important that it is directly in front of, and facing the speaker, with the shield off. Connect the microphone preamplifier (the wand that the little microphone is screwed on to), to the measuring amplifier. Then route the signal through the Bessel Filter, and then to an AI channel on the ADC/DAC BNC router. See settings for individual pieces of electronics.


#. Get a verified decibel level at reference frequency. Using the decibel meter, pick a frequency (a lower one, e.g. 15kHz) and an appropriate voltage level (as yet undetermined, let's say 1.0V), and record the recieved intensity in dB SPL. Go to the *Calibration Parameters* menu, under the *Options* menu at the top menu bar on the program window. Input these settings into the fields here and click ok.
#. Input these settings in the program under the menu *Options/Calibration Parameters...*. This is the voltage level that the program will consider as necessary to generate the specified dB level. This dialog is also where you can set previous calibrations. If you are saving a calibration, it does not matter if a file is selected or not, it will create a new one.

# Go to the Calibration tab, if you are not there already. For saving a calibration most of the input values are fixed, so all you can change is the duration and number of repetions.

#. Press the start button, the plot display will update with the data from the ouput and recorded signals. After recording the program will take several seconds to calculate the filter it will be using. Finally a frequency roll-off plot of the speaker will appear.

* When you run a calibration it will be automatically set as the active calibration for the program.

* The program will automatically save the calibration to you data file under calibration\_# where number is an increasing counter for each time a calibration is run.

* You can switch the calibration, or set the calibration to none under *Options/Calibration Parameters...*


Calibration Tests
-----------------
You can evaluate the calibration that was run by selecting the *Test Calibration* option at the top of the tab. Currently 3 different stimli are available: 
    -White noise, a stimulus with equal intensity all frequencies
    -FM sweep (aka chirp) a stimulus with linear variation in frequency
    -Tone curve, which loops though a series of tones to record their intensity.    + The input fields are the same as for a :ref:`tuning_curve`
        +  a live plot of the recorded dB SPL values is generated in place of where the PSTH plot otherwise resides.