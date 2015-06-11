from sparkle.QtWrapper import QtGui, QtTest

from sparkle.gui.stim.tuning_curve import TuningCurveEditor
from sparkle.gui.stim.factory import TCFactory
from sparkle.gui.stim.qstimulus import QStimulusModel

def test_save_user_inputs():
    originalDefaults = TCFactory.defaultInputs.copy()
    stim = TCFactory.create()
    stim.setReferenceVoltage(100, 1.0)
    stim.setMaxVoltage(1.5, 10.0)
    qstim = QStimulusModel(stim)
    editor = qstim.showEditor()

    editor.show()
    editor.ui.durSpnbx.setValue(0.03)
    editor.ui.risefallSpnbx.setValue(0.022)
    editor.ui.nrepsSpnbx.setValue(3)
    editor.ui.freqStartSpnbx.setValue(9999)
    editor.ui.freqStopSpnbx.setValue(7777)
    editor.ui.freqStepSpnbx.setValue(333)
    editor.ui.dbStepSpnbx.setValue(11)
    editor.ui.dbStartSpnbx.setValue(22)
    editor.ui.dbStopSpnbx.setValue(99)
    # assert int(editor.ui.dbNstepsLbl.text()) == 8
    QtTest.QTest.qWait(500)

    editor.close()
    QtTest.QTest.qWait(500)

    stim = TCFactory.create()
    stim.setReferenceVoltage(100, 1.0)
    qstim = QStimulusModel(stim)
    editor2 = qstim.showEditor()

    editor2.show()
    QtTest.QTest.qWait(1500)
    assert editor2.ui.durSpnbx.value() == 0.03
    assert editor2.ui.risefallSpnbx.value() == 0.022
    assert editor2.ui.nrepsSpnbx.value() == 3
    assert editor2.ui.freqStartSpnbx.value() == 9999
    assert editor2.ui.freqStopSpnbx.value() == 7777
    assert editor2.ui.freqStepSpnbx.value() == 333
    assert editor2.ui.dbStartSpnbx.value() == 22
    assert editor2.ui.dbStopSpnbx.value() == 99
    assert editor2.ui.dbStepSpnbx.value() == 11
    # assert int(editor2.ui.dbNstepsLbl.text()) == 8
    editor2.close()

    TCFactory.defaultInputs = originalDefaults

