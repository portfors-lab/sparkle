SPARKLE 
========================================================================================================
**S**ound **P**resentation **A**nd **R**ecording **K**it for **L**aboratories of **E**lectrophysiology 

Sparkle is a data acquisition system designed for auditory neuroscience research. It allows for the assembly and presentation of auditory stimuli (sounds) with simultaneous recording from a single brain electrode. It is designed to be highly customized to the requirements of the Portfors' hearing research lab. It is primarily a GUI intended to facilitate ease-of-use during experiments.

The system will generate synthesized signals (tones, chrips, etc), as well as play recording files (.wavs). Data is saved to HDF5 format.

Installation notes, user guide and developer docs are available on [Read the Docs](http://sparkle.readthedocs.org/en/latest/index.html)

Running
-------

To get up and running, first install the requirements. Anaconda distribution of python is recommended, but if you want to do it manually (for example to use a virtualenv), you will need to install [HDF5][hdf5] and [PyQt][pyqt] yourself.

If you want to record data with sparkle you must also download the National Instruments device drivers separately.

To install the rest of the dependencies, and create an executable script run:

    $ python setup.py install

If this is successful, you can now run sparkle:

    $ sparkle

See [the documentation][setupdoc] for more in-depth details on setup

[pyqt]: http://www.riverbankcomputing.com/software/pyqt/download
[hdf5]: http://www.hdfgroup.org/downloads
[setupdoc]: http://sparkle.readthedocs.org/en/latest/setup.html

Contributions/ bugs
-------------------

Submit bug reports by creating an issue, please provide as much detail as possible.

Contributions are welcome, you can email me if you have any questions before submitting a pull request.

Maintained by Amy Boyle amy@amyboyle.ninja