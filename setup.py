from setuptools import setup, find_packages

setup(name="sparkle",
      version='0.1.0',
      description="Sound Presentation And Recording Kit for Laboratories of Electrophysiology",
      url="https://github.com/portfors-lab/sparkle",
      author='Amy Boyle',
      author_email="amy@amyboyle.ninja",
      licence="GPLv3",
      packages=find_packages(exclude=['test']),
      install_requires=['numpy',
                        'matplotlib',
                        'scipy',
                        'PyYAML',
                        'h5py',
                        'pyqtgraph',
                        ],
      extras_require={'record': ['pydaqmx'],
                      'doc': ['sphinx-rtd-theme','Sphinx']},
      package_data={'':['*.conf', '*.jpg', '*.png']},
      entry_points={'console_scripts':['sparkle=sparkle.gui.run:main']}
    )