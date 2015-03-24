from sparkle.data.hdf5data import HDF5Data
from sparkle.data.batlabdata import BatlabData

def open_acqdata(filename, user='unknown', filemode='w-'):
    if filename.lower().endswith((".hdf5", ".h5")):
        return HDF5Data(filename, user, filemode)
    elif filename.lower().endswith((".pst", ".raw")):
        return BatlabData(filename, user, filemode)
    else:
        print "File format not supported: ", filename