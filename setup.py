import sys
import os
import glob

from setuptools import setup, find_packages

setup(name="sparkle",
      version='0.2.0',
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
                        'pydaqmx',
                        ],
      package_data={'':['*.conf', '*.jpg', '*.png']},
      entry_points={'console_scripts':['sparkle=sparkle.gui.run:main']},
      classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        ]
    )
