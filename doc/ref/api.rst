=================
Spikeylab API
=================

The program can be divided into two parts: 

* The GUI which interacts with the user to get inputs and presents results. Saves user input values.
* The back-end which takes inputs and communicates with hardware to present stimuli and record results. Holds all state information related to stimuli and data. Handles all data file operations. Can be run without the GUI interface, but designed to be used with it.

The top-level class for the buisness logic is :class:`AcquisitionManager<spikeylab.run.acquisition_manager>`. This class divvies up tasks it recieves from the Main UI class to the different acquisition runner modules.

The top-level class for the GUI is :class:`MainWindow<spikeylab.gui.control.MainWindow>`. To run this with a data file dialog (recommended) run the main method of :mod:`spikeylab.gui.control`.

Backend Structure
------------------
Runner classes
+++++++++++++++
The :class:`AcquisitionManager<spikeylab.run.acquisition_manager>` contains runner classes for the different types of data acquisition that the system is capable of. It also contains some shared state and resources between the different acqusition runner classes such as communication queues. Only one acqusition operation may be in progress at any time.

The different acquisition operations that the program runs are:

* Explore (a.k.a Search) mode, run by :class:`SearchRunner<spikeylab.run.search_runner.SearchRunner>`. Allows on going, on-the-fly, windowed, acquisition. I.e. the stimulus may be changed in the after acquistion has begun. Data gathered in this mode is not currently saved to file.
* Protocol (a.k.a Experimental) mode, run by :class:`ProtocolRunner<spikeylab.run.protocol_runner.ProtocolRunner>`. Allows for a pre-defined list of stimlui to be presented for windowed acquisition. Stimuli cannot be changed once acquisition has begun, although it may be interrupted and halted before finishing.
* Calibration mode, consists of two types a tone curve or a single stimulus which are run separately by :class:`CalibrationCurveRunner<spikeylab.run.calibration_runner.CalibrationCurveRunner>` and :class:`CalibrationRunner<spikeylab.run.calibration_runner.CalibrationRunner>` respectively. Both are predefined, windowed acquisition, for the purpose of speaker calibration, intended to be run before the start of any other operation, but may be run at any time.
* Chart mode, run by :class:`ChartRunner<spikeylab.run.chart_runner.ChartRunner>`. Allows for continuous, on going acqusition. For future development.

All of these runner classes share a common superclass :class:`AbstractAcquisitionRunner<spikeylab.run.abstract_acquisition.AbstractAcquisitionRunner>`:

.. image:: runnerUML.png


Stimulus Classes
++++++++++++++++

The main container for an individual stimulus is the :class:`StimulusModel<spikeylab.stim.stimulusmodel>`. The stimulus is composed of a 2D array (nested lists) of components which are any subclass of :class:`AbstractStimulusComponent<spikeylab.stim.abstract_stimulus>`. These classes are required to implement a signal function, which is used by StimulusModel to sum its components to get the total signal for the desired stimulus. This allows for creation of any stimulus imaginable through the ability to overlap components, and to define custom component classes.

On its own, a StimulusModel represents a single stimlulus signal (the sum of it's components). To create auto-tests (automatic component manipulation, e.g. a tuning curve), The StimlulusModel uses the information held in its :class:`AutoParameterModel<spikeylab.stim.auto_parameter_model>` attribute to modify itself in a loop, and collect all the resultant signals, yielding a list of signals to generate.

Any number of StimulusModels can be collected in a list via a :class:`ProtocolModel<spikeylab.run.protocol_model>`, to be generated independent of each other, in sequence.

Visually, the hierarchy of Stimulus Assembly is as follows:

.. image:: stimulusUML.png

The list of StimlusModels inside of a ProtocolModel, and the list of Components inside of a SimulusModel can, in fact, be empty (and are upon initialization), but cannot be when run by a runner class; i.e. an empty stimulus is considered an error. 

GUI Structure
-------------



Reference API
--------------

.. toctree::
   :maxdepth: 3

   auto/modules.rst
