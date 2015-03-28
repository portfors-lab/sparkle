.. _review:

*******************
Reviewing Data
*******************

To veiw data that have already been gathered, navigate to the *Review* tab. The tables here will be populated on file load, and each time a new test group finishes. Supported formats for review are Sparkle (HDF5) and Batlab. To add support for another format, see :ref:`newformat`

Batlab files will open read-only, and attempts to record new data with a Batlab file open will result in an error. Both the .pst and .raw files must be co-located and share the same name. Selecting one file will prompt sparkle to find it's matching file.

File Contents Overview
----------------------

In the top left are two ways to get a glance at all the data in the file.

    * File tree : shows the heirachial structure of the file
    * Test table : shows only datasets, flattened into a single table

Clicking on an item in the file overview area will populate the other review fields. Everything here responds to single-click, and if a test is large, it may take a second or two to parse the stimulus data information.

If you select a data set, the stimulus table will populate with a list of all the traces for the test. Clicking on one of these will show the data in the data display plot, as it appeared when gathered. It may be flicked through using the arrow button, using key board arrow keys.

Reviewing traces
----------------

The *play* button will automatically cycle through all the reps, from first to last, of the currently selected trace. *play all* will automatically cycle through every rep of every trace starting from first to last.

the *overlay* button will show all reps in the currenlty selected trace at the same time.

Stimulus Files
---------------

If Sparkle encouters a vocalization stimulus file with an invalid file path, the response recording will still show, but the stimulus plots will be empty. To set directories to search for vocalization file name in go to the *Options* menu and select *Vocalizations path...*.