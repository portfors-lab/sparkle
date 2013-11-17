import os


def getdir():
    # simply return the path that this file is in
    return os.path.abspath(os.path.dirname(__file__))

def caldata_filename():
    # return the filename of the calibration dbspl vector
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), u"calibration_dbdata.npy")

def calfreq_filename():
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), u"calibration_frq.npy")

if __name__ == u"__main__":

    print u"the directory of this file is ", getdir()
