import sys
import inspect

from PyQt4 import QtGui, QtCore

from pyqtgraph import GradientEditorItem

from spikeylab.stim.abstract_component import AbstractStimulusComponent
from spikeylab.stim.types.stimuli_classes import *
from spikeylab.gui.stim.generic_parameters import GenericParameterWidget
from spikeylab.gui.stim.components import vocal_parameters
from spikeylab.tools.audiotools import spectrogram, audioread, audiorate

COLORTABLE=[]
for i in reversed(range(256)): COLORTABLE.append(QtGui.qRgb(i,i,i))

# create mapping of class names, assuming they are wrapping a class
# of the same name + Q
def wrapComponent(comp):
    """Wraps a StimulusComponent with a class containing methods 
    for painting and editing. Class will in fact, be the same as
    the component provided, but will also be a subclass of 
    QStimulusComponent

    :param comp: Component to wrap
    :type comp: subclass of AbstractStimulusComponent
    :returns: sublass of AbstractStimulusComponent and QStimulusComponent
    """
    # if already wrapped, return object
    if hasattr(comp, 'paint'):
        return comp
    # to avoid manually creating a mapping, get all classes in 
    # this module, assume they are the class name appended with Q
    current_module = sys.modules[__name__]
    module_classes = {name[1:]: obj for name, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass) if obj.__module__ == __name__}
    # print __name__, module_classes
    stimclass = comp.__class__.__name__
    qclass = module_classes.get(stimclass, QStimulusComponent)
    return qclass(comp)


class QStimulusComponent(object):
    """Wraps around a stimulus component by reassigning this class as a
    subclass of itself and a (subclass of) AbstractStimulusComponent. Allows
    us to assign new methods without breaking code that relies on class name
    and existing methods of the wrapped class"""
    def __init__(self, basestim):
        # super(QStimulusComponent, self).__init__()
        self.__class__ = type(basestim.__class__.__name__,
                              (self.__class__, basestim.__class__),
                              {})
        self.__dict__ = basestim.__dict__
        
    def paint(self, painter, rect, palette):
        """Draws a generic visual representation for this component

        Re-implement this to get a custom graphic in builder editor

        :param painter: Use this class to do the drawing
        :type painter: :qtdoc:`QPainter`
        :param rect: boundary of the delegate for this component, painting should be done inside this boundary
        :type rect: :qtdoc:`QRect`
        :param palette: contains color groups to use, if wanted
        :type palette: :qtdoc:`QPalette`
        """
        painter.save()

        image = QtGui.QImage("./default.jpg")
        painter.drawImage(rect, image)

        # set text color
        painter.setPen(QtGui.QPen(QtCore.Qt.black)) 
        painter.drawText(rect, QtCore.Qt.AlignLeft, self.__class__.__name__)

        painter.restore()

    def showEditor(self):
        """Generates a default editor that creates fields based on this
        components auto_details. 

        Re-implement this method to use custom editor, subclassing :class:`AbstractComponentWidget<spikeylab.gui.stim.abstract_component_editor.AbstractComponentWidget>`

        :returns: :class:`GenericParameterWidget<spikeylab.gui.stim.generic_parameters.GenericParameterWidget>`
        """
        editor = GenericParameterWidget(self)
        return editor

class QPureTone(QStimulusComponent):
    def paint(self, painter, rect, palette):
        fscale, flabel = AbstractStimulusComponent.get_fscale()
        if (self.frequency()/fscale) - np.floor(self.frequency()/fscale) > 0.0:
            freq = str(self.frequency()/fscale)
        else:
            freq = str(int(self.frequency()/fscale))
        painter.fillRect(rect, palette.base())
        painter.drawText(rect.x()+5, rect.y()+12, rect.width()-5, rect.height()-12, QtCore.Qt.AlignLeft, "Pure Tone")
        painter.fillRect(rect.x()+5, rect.y()+35, rect.width()-10, 20, QtCore.Qt.black)
        painter.drawText(rect.x()+5, rect.y()+80,  freq+ " "+ flabel)


class QFMSweep(QStimulusComponent):
    def paint(self, painter, rect, palette):
        mid = rect.y() + (rect.height()/2)
        painter.drawLine(rect.x()+5, mid, rect.x()+rect.width()-10, mid)


class QVocalization(QStimulusComponent):
    _cached_pixmaps = {} # for faster drawing
    def paint(self, painter, rect, palette):
        if self.file() is not None:
            if self.file() not in self._cached_pixmaps:
                spec, f, bins, fs = spectrogram(self.file())
                spec = spec.T
                spec = abs(np.fliplr(spec))
                spec_max = np.amax(spec)
                # print np.amax(scaled), np.amin(scaled), scaled.shape, spec_max
                scaled = np.around(spec/(spec_max/255)).astype(int)

                width, height = scaled.shape
                image = QtGui.QImage(width, height, QtGui.QImage.Format_RGB32)
                for x in xrange(width):
                    for y in xrange(height):
                        image.setPixel(x,y, COLORTABLE[scaled[x,y]])

                pixmap = QtGui.QPixmap.fromImage(image)
                self._cached_pixmaps[self.file()] = pixmap
            else:
                pixmap = self._cached_pixmaps[self.file()]
            painter.drawPixmap(rect.x(), rect.y(), rect.width(), rect.height(), pixmap)
        else:
            painter.save()
            # draw a warning symbol
            smallrect = QtCore.QRect(rect.x()+10, rect.y()+10, rect.width()-20, rect.height()-20)
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 8))
            painter.drawEllipse(smallrect)
            rad = smallrect.width()/2
            x = rad - (np.cos(np.pi/4)*rad)
            painter.drawLine(smallrect.x()+x, smallrect.y()+x, smallrect.x()+smallrect.width()-x, smallrect.y()+smallrect.height()-x)

            painter.restore()

    def showEditor(self):
        editor = vocal_parameters.VocalParameterWidget(self)
        return editor

class QWhiteNoise(QStimulusComponent):
    def paint(self, painter, rect, palette):
        mid = rect.y() + (rect.height()/2)
        painter.drawLine(rect.x()+5, mid, rect.x()+rect.width()-10, mid)

class QSilence(QStimulusComponent):
    def paint(self, painter, rect, palette):
        mid = rect.y() + (rect.height()/2)
        painter.drawLine(rect.x()+5, mid, rect.x()+rect.width()-10, mid)