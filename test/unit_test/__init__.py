print 'setting up all tests...'
import sip
sip.setapi('QVariant', 2)
sip.setapi('QString', 2)
sip.setdestroyonexit(0)