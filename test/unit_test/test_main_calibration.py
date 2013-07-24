from audiolab.calibration.calibration import ToneCurve
import os
# create calibration class
# run through calibration
# check data structures

tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "tmp")

def test_main_cal():
    """
    Test whole run-through of calibration curve
    """

    # set up tone curve
    duration = 0.1 #seconds
    samplerate = 1000000 # device maximum for 6259
    risefall = 0.005
    nreps = 3 
    freqs = [x for x in range(5000,10001,1000)]
    intensities = [x for x in range(0,121,20)]

    fname = os.path.join(tempfolder,'runthrough_temp.hdf5')
    tc = ToneCurve(duration, samplerate, risefall, nreps, freqs, intensities, filename=fname, calf=15000)
    tc.arm(b'PCI-6259/ao0',b'PCI-6259/ai0')

    # run it straight through to finish
    while tc.haswork():
        tc.next()
    # one extra time to get last write
    tc.next()

    # so now tc's data structure should be populated with acquired data
    assert tc.caldata.get('peaks', (6000, 80)) != 0
    assert tc.caldata.get('vmax', (6000, 40)) != 0
