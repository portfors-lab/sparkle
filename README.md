SPARKLE 
========================================================================================================
**S**ound **P**resentation **A**nd **R**ecording **K**it for **L**aboratories of **E**lectrophysiology 

Sparkle is a data acquisition system designed for auditory neuroscience research. It allows for the assembly and presentation of auditory stimuli (sounds) with simultaneous recording from a single brain electrode. It is designed to be highly customized to the requirements of the Portfors' hearing research lab. It is primarily a GUI intended to facilitate ease-of-use during experiments.

The system will generate synthesized signals (tones, chrips, etc), as well as play recording files (.wavs). Data is saved to HDF5 format.

Running
-------

To get up and running, first install the requirements. Anaconda distribution of python is recommended, but there is a requirements file in this repo if you want a list of libraries to install (for example in a virtualenv). In addition to Anaconda libraries, you will need pyqtgraph, and also pydaqmx if you want to record data.

Then run the main GUI module:

    $ python sparkle/gui/run.py

To build the documentation:

    $ cd doc
    $ sphinx-apidoc -f -o ref/auto ../sparkle
    $ make html

See the documentation for more in-depth details on setup

Contributions/ bugs
-------------------

Submit bug reports by creating an issue, please provide as much detail as possible.

Contributions are welcome, you can email me if you have any questions before submitting a pull request.

Maintained by Amy Boyle amy@amyboyle.ninja


Setting the PYTHONPATH
-----------------------
To run sparkle with python from anywhere outside of the sparkle root directory you will need to set the pythonpath.

e.g. for Mac/Linux:

    $ export PYTHONPATH="$PYTHONPATH:/absolute/path/to/sparkle"

or for Windows (on Git bash):

    $ export PYTHONPATH="$PYTHONPATH;C:\absolute\path\to\sparkle"