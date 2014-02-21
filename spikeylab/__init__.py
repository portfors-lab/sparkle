import sip
sip.setapi('QVariant', 2)
sip.setapi('QString', 2)
sip.setdestroyonexit(0)

print 'intializing spikey'
from spikeylab.main.log import init_logging
init_logging()

