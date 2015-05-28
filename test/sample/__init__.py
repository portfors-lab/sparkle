import os
import shutil

def sampledir():
    return os.path.abspath(os.path.dirname(__file__))

def wavdir():
    return os.path.join(sampledir(), 'wavs')

def sampleimage():
    return os.path.join(sampledir(), 'sample_image.jpg')

def samplewav():
    return os.path.join(wavdir(), 'asample_syl.wav')

def samplewav1():
    return os.path.join(wavdir(), 'another_syl.wav')

def samplewav333():
    return os.path.join(wavdir(), 'asample_syl333.wav')

def samplecall1():
    return os.path.join(wavdir(), 'sample_syl.call1')

def calibration_filename():
    return os.path.join(sampledir(), 'calibration.hdf5')

def datafile():
    return os.path.join(sampledir(), 'tinyexperiment.hdf5')

def batlabfile():
    return os.path.join(sampledir(), 'batlab')

def tutorialdata():
    return os.path.join(sampledir(), 'tutorial_data.hdf5')

def test_template():
    return os.path.join(sampledir(), 'multitone.json')

def badinputs():
    return os.path.join(sampledir(), 'controlinputs.json')

def hzsinputs():
    return os.path.join(sampledir(), 'hzsinputs.json')

def batlabvocal():
    return os.path.join(sampledir(), 'batlabvocal.json')

def reallylong():
    return os.path.join(sampledir(), 'ohgodwhenwillitend.json')

def reset_input_file():
    src = os.path.join(sampledir(), 'inputsstash.json')
    dest = os.path.join(sampledir(), 'controlinputs.json')
    shutil.copyfile(src, dest)
    src = os.path.join(sampledir(), 'hzsinputs_stash.json')
    dest = os.path.join(sampledir(), 'hzsinputs.json')
    shutil.copyfile(src, dest)