Setting Up The Development Environment
=======================================

This program was developed to work on the windows platform. However, it has also been successfully installed to review data on Linux and Mac machines. The following describes my process for setting up the necessary packages to work on on the project in a virtualenv.

Of course, you will want to install Python 2.7, pip and virtualenv first.

Unix should be straight forward, noting the following paragraph about PyQt.

The trickiest part is installing PyQt in a virtualenv. I actually wrote a couple blog posts about how to do this in both Linux_ and Windows_.

.. _Linux : http://amyboyle.ninja/Python-Qt-and-virtualenv-in-linux/
.. _Windows : http://amyboyle.ninja/Python-Qt-and-virtualenv-in-windows/


Windows
--------
Because installing some python packages from source on windows is painful, if not impossible, downloading the exe installers for those difficult packages is the way to go.

At the time of writing there is a `great web page`_, maintained by Christoph Gohlke, which contains a nearly comprehensive listing of binary packages for python scientific libraries

.. _Anaconda Python distribution: http://continuum.io/downloads
.. _great web page: http://www.lfd.uci.edu/~gohlke/pythonlibs/

So download the binaries for the following packages:

* numpy
* scipy
* matplotlib
* h5py
* pywin32

I put all of the .exe files in the same folder with the name *easybin*, but where you store them is up to you.

With the virtualenv active run ``easy_install thepackage.exe`` for each package.

The PyQt package is trickier. Use Gohlke's site to download the installer.

Run the installer, but instead of installing to your global site-packages folder install to some other location. I made a separate folder under my home folder to hold binaries that I want to use in virtualenv.

Then just copy the files that were installed into your desired virtualenv’s site-packages directory.

The rest of the necessary packages are installable via pip:

* nose
* pydaqmx
* pyaml
* pyqtgraph
* qtbot

I also used IPython notebook during the development process, for that you will need (via pip):

* ipython
* pygments
* about
* pypandoc -- also install pandoc outwith python
* pyzmq -- used $env:vs90comntools = $env:vs100comntools
