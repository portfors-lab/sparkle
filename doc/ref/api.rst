=================
Spikeylab API
=================

GUI stuff
-----------------
The program can be divided into two parts: 

* The GUI which interacts with the user to get inputs and presents results. Saves user input values.
* The back-end which takes inputs and communicates with hardware to present stimuli and record results. Holds all state information related to stimuli and data.


The top-level class for the buisness logic is :class:`AcquisitionManager<spikeylab.main.acquisition_manager>`. This class divvies up tasks it recieves from the Main UI class to the different acquisition runner modules.

.. toctree::
   :maxdepth: 3

   auto/modules.rst
