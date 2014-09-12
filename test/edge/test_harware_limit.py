from spikeylab.acq.players import FinitePlayer
from spikeylab.stim.types.stimuli_classes import PureTone, Vocalization, Silence

from test.scripts.util import record

if __name__ == "__main__":
    genrate = 5e5
    acqrate = 5e5
    winsz = [0.1, 0.2, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 10, 15, 20, 30, 40, 50, 60] #seconds

    refv = 1.0 # Volts
    refdb = 85 # dB SPL

    player = FinitePlayer()
    player.set_aochan(u"PCI-6259/ao2")
    player.set_aichan(u"PCI-6259/ai16")

    tone = PureTone()
    player.set_aisr(acqrate)

    for dur in winsz:
        try:
            print 'Recording window size: {}'.format(dur)
            tone.setDuration(dur)
            player.set_aidur(dur)
            response = record(player, tone.signal(genrate, 0, refdb, refv), 
                              genrate, nreps=1)
            assert len(response) == dur*genrate
        except:
            print 'Something went wrong at {} second window'.format(dur)
            raise

    print 'Nah, all cool'