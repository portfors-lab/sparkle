import os

def sampledir():
    return os.path.abspath(os.path.dirname(__file__))

def sampleimage():
    return os.path.join(sampledir(), 'sample_image.jpg')

def samplewav():
    return os.path.join(sampledir(), 'sample_syl.wav')

def calibration_filename():
    return os.path.join(sampledir(), 'calibration.hdf5')

def datafile():
    return os.path.join(sampledir(), 'dummydata.hdf5')

def test_template():
    return os.path.join(sampledir(), 'multitone.json')
