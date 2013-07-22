import numpy as np
import os
from audiolab.calibration.datatypes import CalibrationObject
import glob


# I had originally tried to do this in a class, but the setup function
# wasn't properly working when a generator was also used. So I have
# used a bunch of globals instead
FREQS = [x for x in range(5,51,5)]
INTENSITIES = [x for x in range(0,101,10)]
SAMPLERATE = 100000
DURATION = 200
RISEFALL = 5
NREPS = 3
DBV = (100,0.1)
NPTS = (SAMPLERATE*(DURATION/1000))
D = np.ones(NPTS)

tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "tmp")

def test_calobj_load():
    """
    Test that you load back the same calibration data object that you save
    """
    co =  CalibrationObject(FREQS, INTENSITIES, SAMPLERATE, DURATION, 
                            RISEFALL, NREPS,v=DBV[1])
    
    co.init_data('testdata', 4, dim4=NPTS)
    
    co.put('testdata', (FREQS[1], INTENSITIES[3], 1), D)
    print('testdata type ', type(co.data['testdata']))        

    filetypes = ['.json', '.mat', '.npy', '.pkl', '.hdf5']
    #filetypes = ['.hdf5']
    for ext in filetypes:
        fname = os.path.join(tempfolder,'savetemp' + ext)
        co.save_to_file(fname)

    # load it back in
    for ext in filetypes:
        fname = os.path.join(tempfolder,'savetemp' + ext)
        caldata = CalibrationObject.load_from_file(fname)
        yield verify_dictfields, caldata, ext
        yield verify_get, caldata, ext

    # delete generated file
    for filename in glob.glob(os.path.join(tempfolder,'savetemp.*')):
        os.remove(filename)

def verify_dictfields(data, ext):

    assert data.stim['sr'] == SAMPLERATE
    assert data.stim['calV'] == DBV[1]
    assert data.stim['frequencies'] == FREQS
    assert data.stim['intensities'] == INTENSITIES
    assert data.stim['duration'] == DURATION
    assert data.stim['risefalltime'] == RISEFALL
    assert data.stim['repetitions'] == NREPS

def verify_get(data, ext):
        
    dback = data.get('testdata', (FREQS[1], INTENSITIES[3], 1))
    assert np.array_equal(dback,D)


        



