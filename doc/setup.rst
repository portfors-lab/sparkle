Installation / Setup
========================

If you know what you are doing, the source is on Github_.


Installing to Record data
--------------------------
If you are instally Sparkle on a machine where you want to record, not just review data, you must have the hardware `DAQmx drivers`_ installed from National Instruments. Download and install according to their directions.

.. _DAQmx drivers: http://search.ni.com/nisearch/app/main/p/bot/no/ap/tech/lang/en/pg/1/sn/catnav:du,n8:3478.41,ssnav:sup/
    
Install on Windows
--------------------

Get Git
+++++++++

Download and install Git_ using the installer downloaded from the Git website.

Downloading SPARKLE
+++++++++++++++++++
Once you have git, use your command line (Git bash recommended) to navigate to where you want the SPARKLE source code to live.

Copy the url from Github_, and clone it to your local machine, e.g. for HTTPS (recommended)::

    $ git clone https://github.com/portfors-lab/sparkle.git

Download Python and packages
+++++++++++++++++++++++++++++

It is strongly recommended to install the free Anaconda_ python distribution instead of the download from python.org. This is because it comes with a lot of the 3rd party scientific packages you need in one easy download and install process. It will save a lot of headaches when installing packages on windows.

In fact, you will only need one or two (if recording) additional packages, which you can get by the command (Git bash or powershell)::

    $ pip install pyqtgraph

If you installed the device driver to record data, also install the python wrappers via the command::

    $ pip install pydaqmx

Otherwise, if you did not install Anaconda you can run (after installing pip yourself)::

    $ pip install -r requirements.txt

And good luck troubleshooting from there ;)... you will also need PyQt_ which is not available via pip.

.. _Git : http://git-scm.com/downloads
.. _Anaconda : http://continuum.io/downloads
.. _PyQt : http://www.riverbankcomputing.com/software/pyqt/download


Install on Unix
------------------

Get Git
+++++++++

Download and install Git_ using the installer from the Git website, or using your package manager.

Downloading SPARKLE
+++++++++++++++++++
Once you have git, use your command line to navigate to where you want the SPARKLE source code to live.

Copy the url from Github_, and clone it to your local machine, e.g. for HTTPS (recommended)::

    $ git clone https://github.com/portfors-lab/sparkle.git

Download Python and packages
+++++++++++++++++++++++++++++

You should already have python installed by default on your machine. Make sure it is some subversion of python 2.7::

    $ python --version

If you get something other than :code:`Python 2.7.<#>`, you will need to install python 2.7 from the `Python website`_.

To install Sparkle's dependencies, from the sparkle root directory, run::

    $ pip install -r requirements.txt

You will also need to install PyQt, which is not available on pip. You may be able to install it via or package manager. Or, follow the directions_ in the PyQt docs, to install from source.

.. _Python website : https://www.python.org/downloads/
.. _directions : http://pyqt.sourceforge.net/Docs/PyQt4/installation.html


Installing in a Virtualenv
----------------------------

Virtualenv is not necessary to run SPARKLE. If you don't know what it is, don't worry about it for now.

For the most part, all these instructions still apply if you want to use a virtualenv. Windows is a pain in my experience. Installing anaconda will give you the virtualenv package, but you will need to find out how to install things via pip or easy_install to get the correct packages into the virtualenv. Unix should straight forward, noting the following paragraph about PyQt.

The trickiest part is installing PyQt in a virtualenv. I actually wrote a couple blog posts about how to do this in both Linux_ and Windows_.

.. _Linux : http://amyboyle.ninja/Python-Qt-and-virtualenv-in-linux/
.. _Windows : http://amyboyle.ninja/Python-Qt-and-virtualenv-in-windows/

Running SPARKLE
------------------
Once you have all the dependencies installed, now you can actually run SPARKLE! Via the command line, change directory into the root folder of SPARKLE (this is the first 'sparkle' folder, not 'sparkle/sparkle'). You can now run::

    $ python sparkle/gui/run.py

This should launch a dialog asking you to choose a data file. See the :doc:`guide\index`.

.. _Github: https://github.com/portfors-lab/sparkle

Creating a shortcut (Windows):
-------------------------------
To create a shortcut on the desktop (or anywhere really) to launch Sparkle from source, first create a plain text file, and let's call it 'sparkle.bat'. In this file add the following two lines, replacing as necessary::

    set PYTHONPATH=<path to sparkle>
    <path to python executable> <path to sparkle\sparkle\gui\run.py>

e.g. ::

    set PYTHONPATH=C:\shared\sparkle
    C:\Python27\python C:\shared\sparkle\sparkle\gui\run.py

Then you can create a shortcut to that script by right clicking and selecting `Create Shortcut`. Move the shortcut to the desktop (or other desired location). There is an .ico file in the `sparkle/resources` folder intended to be used as the icon for this shortcut, which you can set through the shortcut properties.