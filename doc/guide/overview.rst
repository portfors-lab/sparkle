.. _acqsettings:

Acquisition Settings
====================
* Channels: The analog input and output channels (Stim and AI) are selected from the drop-down boxes in the upper right of the interface. They should match the channels you are using on the hardware.

* Acq. Sample rate: The rate at which data points are recorded from the electrode

* Window size: Duration of the recording window, must meet or exceed the length of the stimulus

* Threshold: Spike detection voltage threshold, for use in producing the spike raster plot and PSTH. Updating values in this field will update the red threshold line on the data display.

* Spike bin size: Time bin size to sort over-threshold spikes into, for the raster plot and PSTH.

* Rep rate: (Repetition rate) Presentation rate of consecutive stimuli. If this rate exceeds the rate allowable for the recording window length, repetitions will be presented immediately after each other (with some down-time for resetting).

* Mode: Windowed mode is finite chunks of recording, and Chart is continuous acquisition.


Options
=======

The options menu allows the you to specify a number of system wide settings.

Change Data File
------------
Allow you to change location where data will save to. Can load a previous file, or create a new one.

Calibration Parameters
-----------------------
Set the current calibration, and parameters for calculating new calibrations.
see :ref:`calibration`

Set Scale
---------
Scale options for time and frequency inputs. Affects entire interface.

Spectrogram Parameters
----------------------
Input parameters for spectrogram generation on all spectrogram plots in the program.

View
====
Show hidden parts of the interface, and setup stimulus details to display


Plot Display
============

The data display consists of a several plots to visualize both the generated stimulus and the recorded response. It is in a dockable window, that may remain attached to the control interface to float freely, with the ability of full-screen mode. The plots within the display can also be resized. Right click any of the plots to reset the zoom. There is a different display for calibration and data collection.

Zooming behaviour is consistent across all plots. The mouse wheel may be used to zoom in and out the y-axis, with the center of the zoom being where the mouse pointer's current location. Holding ``ctrl`` will zoom the x-axis. Likewise, click and drag will pan the y-axis, and holding ``ctrl`` will pan the x-axis. Right click and drag will create a bounding-box zoom. More options are available by right clicking the plots to display a pop-up menu.

Calibration Display
-------------------
For both the generated and recorded signal, there is a spectrogram, a time signal plot, and a spectrum of the signal. When using calibrated signals, the generated signal display the signal after calibration, i.e. what is actually delievered to the DAC card. This display is meant for use when investigating calibration only, and may cause the Interface to be less responsive, especially for longer stimlui.

Data Collection Display
-----------------------
Recording Trace
~~~~~~~~~~~~~~~~
The plot in the bottom left displays the response trace.The xaxis will update with the widow size specified on the control interface.

There is a red threshold line which can be grabbed and dragged. It has a linked field on the control interface which will update, and likewise if you manually enter a value into this field the line will update on the plot. This is the spike detection threshold, that will affect the spikes counts in the raster plot and PSTH. This threshold is not saved to the data file.

A raster of detected spikes will appear if the recording traces crosses over threshold. The detected spikes are sorted into bins, of size determined by the bin size field on the control interface. The raster points appear between set coordinate bounds. To change these limits right click on the plot and select *edit raster bounds*.

the small blue trace in the upper left of the response plot is the stimulus signal.

Stimulus Spectrogram
~~~~~~~~~~~~~~~~~~~~
Spectrogram of the stimulus presented, in the same time scale as the response trace

Stimulus FFT
~~~~~~~~~~~~
The sideways plot on the right is the spectrum analysis of the stimulus signal, in dB SPL.

PSTH
=====
Online display of spike detection histogram, using the user-chosen threshold. Note that the metrics below the plot are calculating averages from the previous set of repetitions, not what is currently displayed in the plot!

Data Files
==========
Recorded data is saved to data files in HDF5 format. Each protcol list is a group, and under the groups are tests, which are numbered sequentially, with numbers continuing across groups. Each test is a dataset with the dimensions no. of traces x no. of repetitions x samples. Stimulus data is saved as an attribute of each dataset, and is a JSON list of dictionarys, with each entry providing enough information to be able to recreate the stimulus. There will be a better description here in the future...

Other Settings
===============
Semi-permanent setting loaded once at program start are located in the :ref:`settings`.

Names
=====
Considering the following Names for the Program

* ADA : Auditory Data Acqusition (Also the name of first programmer Ada Lovelace)

* SONIC : Spiffy Otologic Neuron Investigation Companion

* Neuroread

* Sonic Sparkle High-Five

* Spikeylab