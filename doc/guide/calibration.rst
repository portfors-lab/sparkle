.. _calibration:

Speaker Calibration
===================

For the purposes of speaker frequency roll-off documentation and compensation. Also sets the reference intensity to determine the necessary signal amplitude to correctly deliver stimuli in dB SPL.

#. First set up the hardware. 

    - From the AO channel you are using on the ADC/DAC BNC router, route the output signal to an amplifier, then to the attenuator, and then to the speaker.
    - Place the microphone exactly 10cm away from the speaker. The microphone is highly directional, it is important that it is directly in front of, and facing the middle of the speaker, with the shield off. Connect the microphone preamplifier (the wand that the little microphone is screwed on to), to the measuring amplifier or conditioning amplifier (which ever is present). Then route the signal through the Bessel Filter, and then to an AI channel on the ADC/DAC BNC router.
    - For the measuring amplifier: Make sure the *Input Section Gain* and *Output Section Gain* are set to 0.
    - For the conditioning amplifier:

        * Transducer supply -> 200V polarized
        * Transducer set-up -> 4.07mV per channel (actually should be microphone calibrated sensitivity)

#. Navigate to the calibration tab.

#. For saving a calibration, most of the input values are fixed, so all you can change is the duration and number of repetitions. The duration of the stimulus is fixed to the window size, so you change the recording window to change the stimulus duration.

#. The microphone is calibrated first. Use the microphone calibrator thing that plays the tone. Place the end of the microphone into the equipment. Press the *calibrate* button on the line that says stuff about microphone calibration. When it has finished recording, remove the device, and replace the microphone at it's proper place w.r.t the speaker.

#. Press the start button, the plot display will update with the data from the ouput and recorded signals. A tone will be played first to attain the reference intensity, then followed by an upsweep to get the speaker transfer function. After recording, the program will take several seconds to calculate the filter it will be using. Finally a frequency roll-off plot of the speaker will appear.

#. Get a look at the efficacy of the calibration, by choosing the *Test Calibration* button and selecting one of the options from the drop down menu that is enabled. The closer to a flat spectrum recorded, the better.

* When you run a calibration it will be automatically set as the active calibration for the program.

* The program will automatically save the calibration to you data file under calibration\_# where number is an increasing counter for each time a calibration is run.

* You can switch the calibration, or set the calibration to none under *Options/Calibration Parameters...*

* To change the effective frequency range of a calibration, also see the *Options/Calibration Parameters...* menu.

* If you wish to change the calibration frequency or voltage, you will need to edit the :ref:`settings`.

Calibration Tests
-----------------

You can evaluate the calibration that was run by selecting the *Test Calibration* option at the top of the tab. Currently 3 different stimli are available: 

    - White noise, a stimulus with equal intensity all frequencies
    - FM sweep (aka chirp) a stimulus with linear variation in frequency
    - Tone curve, which loops though a series of tones to record their intensity.    

        + The input fields are the same as for a :ref:`tuning_curve`
        + A live plot of the recorded dB SPL values is generated in place of where the PSTH plot otherwise resides.