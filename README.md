SPIKEYLAB
=========

SSHF is a data acquisition system designed for auditory neuroscience research. It allows for the assembly and presentation of auditory stimuli (sounds) with simultaneous recording from a single brain electrode. It is designed to be highly customized to the requirements of the Portfors' hearing research lab. It is primarily a GUI intended to facilitate ease-of-use during experiments.

The system will generate synthesized signals (tones, chrips, etc), as well as play recording files (.wavs). Data is saved to HDF5 format.

Running
-------

To get up and running, first install the requirements:

    $ pip install -r requirements.txt

Then run the main GUI module:

    $ python spikeylab/gui/run.py

To build the documentation:

    $ cd doc
    $ make html


Contributions/ bugs
-------------------

Submit bug reports by creating an issue, please provide as much detail as possible.

Contributions are welcome, you can email me if you have any questions before submitting a pull request.

Maintained by Amy Boyle amy@amyboyle.ninja