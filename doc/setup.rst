Installation / Setup
========================

The easiest way to get sparkle, and to get more stable releases, is to :ref:`download from PyPI using pip<PyPI>`.

Alternatively, to get the bleeding-edge version of sparkle, or to help with development, you need to :ref:`get a copy of the source code<install_from_github>` repository from Github.

Either way, if applicable, also see :ref:`Installing to Record Data<recording>`. (You can do this before or after installing sparkle)

.. _recording:

Installing to Record Data
>>>>>>>>>>>>>>>>>>>>>>>>>>
If you are installing Sparkle on a machine where you want to record, not just review data, you must have the hardware `DAQmx drivers`_ installed from National Instruments. Download and install according to their directions.

.. _DAQmx drivers: http://search.ni.com/nisearch/app/main/p/bot/no/ap/tech/lang/en/pg/1/sn/catnav:du,n8:3478.41,ssnav:sup/

.. _PyPI:

Install from PyPI
>>>>>>>>>>>>>>>>>>

Install Python + Tools
++++++++++++++++++++++
It is strongly recommended to install the free Anaconda_ python distribution instead of the download from python.org. This is because it comes with a lot of the 3rd party scientific packages you need in one easy download and install process. If you are on Windows, it will save a lot of headaches when installing packages. 

Install Sparkle
++++++++++++++++
After you install Anaconda, open up a command terminal and enter:

Windows (need admin rights):

    $ pip install sparkle

Unix:

    $ sudo pip install sparkle

Run Sparkle
++++++++++++

Then you should be able to call sparkle from the command line:

    $ sparkle

Creating a shortcut (Windows 7):
---------------------------------

You can also find sparkle under the start menu, type sparkle into the search bar, and it should come up. You can run it from here. To create a shortcut, drag the start menu entry onto the desktop.

.. _install_from_github:

Install from Github
>>>>>>>>>>>>>>>>>>>>

If you know what you are doing, the source is on Github_.

.. _Github: https://github.com/portfors-lab/sparkle

Get Git
+++++++++

Download and install Git_ using the installer downloaded from the Git website, or using your package manager (Unix).
    
Downloading SPARKLE
+++++++++++++++++++
Once you have git, use your command line (Git bash recommended for Windows) to navigate to where you want the SPARKLE source code to live.

Copy the url from Github_, and clone it to your local machine, (or, if you want to contribute, you can fork_ sparkle, and clone your fork) e.g. for HTTPS (recommended)::

    $ git clone https://github.com/portfors-lab/sparkle.git

This will create a directory :code:`sparkle` in your current directory.

.. _fork: https://help.github.com/articles/fork-a-repo/

Install Python and packages
+++++++++++++++++++++++++++++

Install Using Anaconda
----------------------
It is strongly recommended to install the free Anaconda_ python distribution instead of the download from python.org. This is because it comes with a lot of the 3rd party scientific packages you need in one easy download and install process. If you are on Windows, it will save a lot of headaches when installing packages.

In fact, you will only need one or two (if recording) additional packages, which you can get by the command (Git bash or powershell)::

    $ pip install pyqtgraph

If you installed the device drivers to record data, also install the python wrappers via the command::

    $ pip install pydaqmx

You can now move on to :ref:`running`

.. _manual dependencies:

Install Dependencies Manually
-----------------------------
If you did not install Anaconda (for example you want to use a virtualenv), you will need to install a few things from their various sources.

If you are on Unix, you should already have python installed by default on your machine. Make sure it is some subversion of python 2.7::

    $ python --version

If you get something other than :code:`Python 2.7.<#>`, you will need to install python 2.7 from the `Python website`_.

If you are on Windows, you will need to install python 2.7 from the `Python website`_.

You will also need to install:

* HDF5_
* PyQt_ (directions_)
* pip_ 

After that you can install the rest of sparkle by running::

    $ cat sparkle/requirements.txt | xargs pip install 


.. _Git : http://git-scm.com/downloads
.. _Anaconda : http://continuum.io/downloads
.. _Python website : https://www.python.org/downloads/
.. _HDF5 : http://www.hdfgroup.org/downloads
.. _PyQt : http://www.riverbankcomputing.com/software/pyqt/download
.. _pip: http://pip.readthedocs.org/en/latest/installing.html
.. _directions : http://pyqt.sourceforge.net/Docs/PyQt4/installation.html


Installing in a Virtualenv
----------------------------

Virtualenv is not necessary to run SPARKLE. If you don't know what it is, don't worry about it for now.

For the most part, the above instructions still apply if you want to use a virtualenv. Windows is a pain in my experience. Installing anaconda will give you the virtualenv and pip packages, but you will need to find out how to install things via pip or easy_install to get the correct packages into the virtualenv.

For notes on setting this up in windows, and for installing the non-pip installable packages, see :doc:`Virtualenv notes<dev_env>`.

.. _running:

Running SPARKLE
+++++++++++++++++
    
Setting the PYTHONPATH
-----------------------
To run sparkle with python from anywhere outside of the sparkle root directory you will need to set the pythonpath.

e.g. for Mac/Linux:

    $ export PYTHONPATH="$PYTHONPATH:/absolute/path/to/sparkle"

or for Windows (on Git bash):

    $ export PYTHONPATH="$PYTHONPATH;C:\\absolute\\path\\to\\sparkle" 

Run
-----

Once you have all the dependencies installed, now you can actually run SPARKLE! Via the command line, change directory into the root folder of SPARKLE (this is the first 'sparkle' folder, not 'sparkle/sparkle'). You can now run::

    $ python sparkle/gui/run.py

This should launch a dialog asking you to choose a data file. See the :doc:`guide\index`.


Creating a shortcut (Windows):
-------------------------------     
To create a shortcut on the desktop (or anywhere really) to launch Sparkle from source, first create a plain text file, and let's call it 'sparkle.bat'. In this file add the following two lines, replacing as necessary::

    set PYTHONPATH=<path to sparkle>
    <path to python executable> <path to sparkle\sparkle\gui\run.py>

e.g. ::

    set PYTHONPATH=C:\shared\sparkle
    C:\Python27\python C:\shared\sparkle\sparkle\gui\run.py

Then you can create a shortcut to that script by right clicking and selecting `Create Shortcut`. Move the shortcut to the desktop (or other desired location). There is an .ico file in the `sparkle/resources` folder intended to be used as the icon for this shortcut, which you can set through the shortcut properties.

Building the documentation locally
+++++++++++++++++++++++++++++++++++

    $ cd doc
    $ sphinx-apidoc -f -o ref/auto ../sparkle
    $ make html

You may need additional packages to build the doc, install via pip as necessary.