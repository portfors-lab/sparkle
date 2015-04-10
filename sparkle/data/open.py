from sparkle.data.batlabdata import BatlabData
from sparkle.data.hdf5data import HDF5Data


def open_acqdata(filename, user='unknown', filemode='w-'):
    """Opens and returns the correct AcquisitionData object according to filename extention.

    Supported extentions:
    * .hdf5, .h5 for sparkle data
    * .pst, .raw for batlab data. Both the .pst and .raw file must be co-located and share the same base file name, but only one should be provided to this function
    
    see :class:`AcquisitionData<sparkle.data.acqdata.AcquisitionData>`

    examples (if data file already exists)::

        data = open_acqdata('myexperiment.hdf5', filemode='r')
        print data.dataset_names()

    for batlab data::

        data = open('mouse666.raw', filemode='r')
        print data.dataset_names()
    """
    if filename.lower().endswith((".hdf5", ".h5")):
        return HDF5Data(filename, user, filemode)
    elif filename.lower().endswith((".pst", ".raw")):
        return BatlabData(filename, user, filemode)
    else:
        print "File format not supported: ", filename
