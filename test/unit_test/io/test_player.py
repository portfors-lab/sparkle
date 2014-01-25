import numpy as np

from spikeylab.io.players import FinitePlayer

def test_finite_acquisition_equal_dims():
    player = FinitePlayer()
    fs = 500000
    dur = 0.01
    x = np.arange(fs*dur)
    tone = data_func(x, 5)
    player.set_stim(tone, fs)
    player.set_aidur(0.01)
    player.set_aisr(fs)
    player.start(u"PCI-6259/ao0",u"PCI-6259/ai0")

    response0 = player.read()
    player.reset()
    response1 = player.read()
    player.stop()

    # pyplot.plot(tone)
    # pyplot.plot(response0)
    # pyplot.show()

    amp = np.max(tone)
    tolerance = max(amp*0.1, 0.005) #noise floor
    assert np.allclose(tone, response0,rtol=0,atol=tolerance)

def test_finite_acquisition_unequal_dims():
    player = FinitePlayer()
    fs = 500000
    dur = 0.02
    x = np.arange((fs*dur)/2)
    tone = data_func(x, 5)
    player.set_stim(tone, fs)
    player.set_aidur(0.02)
    player.set_aisr(fs/4)
    player.start(u"PCI-6259/ao0",u"PCI-6259/ai0")

    response0 = player.read()
    player.reset()
    response1 = player.read()
    player.stop()

    # Just make sure doesn't throw error then?



def data_func(x, f):
    return 2*np.sin(2*np.pi*f*x/len(x))