import os
import numpy as np

from audiolab.io.structures import BigStore

tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "tmp")

def test_continuous_data():

    fname = os.path.join(tempfolder,'savecont.hdf5')
    mydata = BigStore(fname, chunksize=2*8)

    acq_grab_size = 10
    total_samples = (2**16) +4
    for igrab in range(0,total_samples,acq_grab_size):
        grab = np.random.randint(-10,10,acq_grab_size)
        mydata.put(grab)

    mydata.consolidate()
    assert mydata.shape() == (total_samples,)

    mydata.close()
