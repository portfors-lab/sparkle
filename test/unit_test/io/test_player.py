import numpy as np

from spikeylab.io.players import FinitePlayer

def test_finite_acquisition_equal_dims():
    player = FinitePlayer()
    tone, x= player.set_tone(5000,100,0.01,0.001,500000)
    player.set_aidur(0.01)
    player.set_aisr(500000)
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
    tone, x= player.set_tone(5000,100,0.01,0.001,500000)
    player.set_aidur(0.02)
    player.set_aisr(50000)
    player.start(u"PCI-6259/ao0",u"PCI-6259/ai0")

    response0 = player.read()
    player.reset()
    response1 = player.read()
    player.stop()

    # Just make sure doesn't throw error then?