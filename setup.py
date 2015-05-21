import sys
import os
import glob

from setuptools import setup, find_packages

setup(name="sparkle",
      version='0.0.2',
      description="Sound Presentation And Recording Kit for Laboratories of Electrophysiology",
      url="https://github.com/portfors-lab/sparkle",
      author='Amy Boyle',
      author_email="amy@amyboyle.ninja",
      license="GPLv3",
      packages=find_packages(exclude=['test', 'doc']),
      install_requires=[
                        'numpy',
                        'matplotlib',
                        'scipy',
                        'PyYAML',
                        'h5py',
                        'pyqtgraph',
                        'Sphinx',
                        'sphinx-rtd-theme',
                        ],
      extras_require={'record': ['pydaqmx'],},
      package_data={'':['*.conf', '*.jpg', '*.png']},
      entry_points={'console_scripts':['sparkle=sparkle.gui.run:main']},
      classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        ]
    )

# we have just installed sphinx, but we will need to update the system
# path to be able to import it.
site_packages = [path for path in sys.path if path.endswith('site-packages')]
for path in site_packages:
    if len(glob.glob(os.path.join(path, 'Sphinx*'))) > 0:
        sys.path.append(glob.glob(os.path.join(path, 'Sphinx*'))[0])

# now we should be able to import
from sphinx.apidoc import main

# build the auto-generated API doc using sphinx-apidoc
proj_root_dir = os.path.abspath(os.path.dirname(__file__))
auto_doc_dir = os.path.join(proj_root_dir, 'ref',' auto')
source_dir = os.path.join(proj_root_dir, 'sparkle')
argv = ['sphinx-apidoc', '-f', '-o', auto_doc_dir, source_dir]
main(argv=argv)
