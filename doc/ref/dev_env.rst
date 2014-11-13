Setting Up The Development Environment
=======================================

This program was developed to work on the windows platform. However, development work was also done on a Fedora machine, so it is demonstrated to work in Linux too. The following describes my process for setting up the necessary packages to workon on the project in a virtualenv.

Of course, you will want to install Python 2.7 and virtualenv first.

The use of virtualenv is not required, but recommended, particularly if you plan on having any other python projects.

The project is under Git version control and is currently in a private repo on BitBucket (owned by Amy Boyle). This can, if necessary (in the event that Amy is not available), be copied from the local installation on the rig machine, and worked on/maintained/pushed to a different owner's remote repo from there. (If you are reading this, you found the repo)

Windows
--------
Because installing some python packages from source on windows is painfull, if not impossible, downloading the exe installers for those difficult packages is the way to go.

At the time of writing there is a `great web page`_, maintained by Christoph Gohlke, which contains a nearly comprehensive listing of binary packages for python scientific libraries

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
* pyuserinput

I also used IPython notebook during the development process, for that you will need (via pip):

* ipython
* pygments
* about
* pypandoc -- also install pandoc outwith python
* pyzmq -- used $env:vs90comntools = $env:vs100comntools

Linux
------

You should be able to install everything via pip, with the exception of PyQt, which I wrote a `blog post`_ about.

.. _blog post: http://amyboyle.ninja/Python-Qt-and-virtualenv-in-linux/