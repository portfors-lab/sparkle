Channels
========

The analog input and output channels are selected from the drop-down boxes in the upper right of the interface.

Options
=======

The options menu allows the you to specify a number of system wide settings.

Save Options
------------
* *Save Format* ... actually only hdf5 works, so just pick that
* *Save File Location* select a folder to where data and calibrations will be saved to
* *Save Name Template* the filename (without extension) for datafiles to be saved as. If there is already a file with that name in the provided save file location, the filename will auto-increment.

Set Calibration
---------------
see :ref:`calibration`

Set Scale
---------
Scale options for time and frequency inputs. Affects entire interface.

Spectrogram Parameters
----------------------
Input parameters for spectrogram generation on all spectrogram plots in the program. Colormap isn't working :( .

Plot Display
============

The data display consists of a several plots to visualize both the generated stimulus and the recorded response. It is in a dockable window, that may remain attached to the control interface to float freely, with the ability of full-screen mode. The plots within the display can also be resized. Right click any of the plots to reset the zoom.

Recording Trace
---------------
The plot in the bottom left displays the response trace. Use the mouse wheel to increse or decrease zoom for the voltage value (gain). left click and drage to move the trace vertically within the plot. The xaxis will update with the widow size specified on the control interface.

There is a red threshold line which can be grabbed and dragged. It has a linked field on the control interface which will update, and likewise if you manually enter a value into this field the line will update on the plot. This is the spike detection threshold.

A raster of detected spikes will appear if the recording traces crosses over threshold. The detected spikes are sorted into bins, of size determined by the bin size field on the control interface. The raster points appear between set coordinate bounds. To change these limits right click on the plot and select *edit raster bounds*.

the small blue trace in the upper left of the response plot is the stimulus signal.

Stimulus Spectrogram
--------------------
Spectrogram of the stimulus presented, in the same time scale as the response trace

Stimulus FFT
------------
The sideways plot on the right is the spectrum analysis of the stimulus signal. Pressing ctr will allow you to zoom using a bounding box. Other wise clicking and dragging pans the plot, and mouse when affect the gain.

PSTH
=====
Online display of spike detection histogram. Note that the metrics below the plot are calculating averages from the previous set of repetitions, not what is currently displayed in the plot!

Data Files
==========
Recorded data is saved to data files in HDF5 format. Each protcol list is a group, and under the groups are tests, which are number sequentially, with numbers continuing across groups. Each test is a dataset with the dimensions no. of traces x no. of repetitions x samples. Stimulus data is saved as an attribute of each dataset and is a json list of dictionarys, with each entry providing enough information to be able to recreate the stimulus. There will be a better description here in the future.

Names
=====
Considering the following Names for the Program
* ADA : Auditory Data Acqusition (Also the name of first programmer Ada Lovelace)
* SONIC : Spiffy Otologic Neuron Investigation Companion
* Neuroread
* Sonic Sparkle High-Five