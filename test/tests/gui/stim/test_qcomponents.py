from sparkle.QtWrapper import QtCore, QtGui, QtTest
from sparkle.gui.stim.components.qcomponents import wrapComponent
from sparkle.stim.types import get_stimuli_models
from sparkle.stim.types.stimuli_classes import *

PAUSE = 200
ALLOW = 15

# painters must be used inside of a paintEvent
class Canvas(QtGui.QWidget):
    def setComponent(self, component):
        self.component = component

    def paintEvent(self, event):
        super(Canvas, self).paintEvent(event)
        painter = QtGui.QPainter(self)
        rect = QtCore.QRect(100, 100, 200, 200)
        palette = QtGui.QPalette()
        
        self.component.paint(painter, rect, palette)

class TestQComponents():
    def setup(self):
        self.canvas = Canvas()

    def teardown(self):
        self.canvas.close()
        
    def test_qcomponents(self):
        stimuli = [stim_class() for stim_class in get_stimuli_models()]
        for stim in stimuli:
            yield self.check_component, stim

    def check_component(self, stim):

        # what to check for paint, no errors?
        qstim = wrapComponent(stim)
        self.canvas.setComponent(qstim)
        self.canvas.show()

        QtTest.QTest.qWait(PAUSE)

        editor = qstim.showEditor()
        editor.show()
        QtTest.QTest.qWait(ALLOW)

        if 'duration' in editor.inputWidgets:
            editor.inputWidgets['duration'].setValue(0.33)
            editor.saveToObject()
            assert stim.duration() == 0.33
        if 'intensity' in editor.inputWidgets:
            editor.inputWidgets['intensity'].setValue(33)
            editor.saveToObject()
            assert stim.intensity() == 33
        if 'frequency' in editor.inputWidgets:
            editor.inputWidgets['frequency'].setValue(33)
            editor.saveToObject()
            assert stim.frequency() == 33
        if 'risefall' in editor.inputWidgets:
            editor.inputWidgets['risefall'].setValue(0.033)
            editor.saveToObject()
            assert stim.risefall() == 0.033

        editor.close()
