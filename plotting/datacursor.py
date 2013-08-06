from matplotlib.offsetbox import DraggableAnnotation
from matplotlib.text import Annotation
from matplotlib import cbook
import numpy as np

class DataCursor(object):
    """A simple data cursor widget that displays the x,y location of a
    matplotlib artist when it is selected."""
    def __init__(self, artists, tolerance=2, offsets=(-20, 20), 
                 template='x: %0.2f\ny: %0.2f', display_all=False):
        """Create the data cursor and connect it to the relevant figure.
        "artists" is the matplotlib artist or sequence of artists that will be 
            selected. 
        "tolerance" is the radius (in points) that the mouse click must be
            within to select the artist.
        "offsets" is a tuple of (x,y) offsets in points from the selected
            point to the displayed annotation box
        "template" is the format string to be used. Note: For compatibility
            with older versions of python, this uses the old-style (%) 
            formatting specification.
        "display_all" controls whether more than one annotation box will
            be shown if there are multiple axes.  Only one will be shown
            per-axis, regardless. 
        """
        self.template = template
        self.offsets = offsets
        self.display_all = display_all
        if not cbook.iterable(artists):
            artists = [artists]
        self.artists = artists
        self.axes = tuple(set(art.axes for art in self.artists))
        self.figures = tuple(set(ax.figure for ax in self.axes))

        self.annotations = {}
        for ax in self.axes:
            self.annotations[ax] = self.annotate(ax)

        self.pick_events = []
        for artist in self.artists:
            artist.set_picker(tolerance)
        for fig in self.figures:
            pe = fig.canvas.mpl_connect('pick_event', self)
            self.pick_events.append(pe)

    def annotate(self, ax):
        """Draws and hides the annotation box for the given axis "ax"."""
        annotation = ax.annotate(self.template, xy=(0, 0), ha='right',
                xytext=self.offsets, textcoords='offset points', va='bottom',
                #bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0')
                )
        annotation.set_visible(False)
        DraggableAnnotation(annotation)
        return annotation

    def __call__(self, event):
        """Intended to be called through "mpl_connect"."""
        
        #print(event.mouseevent)
        
        # if we picked an annotation, ignore
        if type(event.artist) == Annotation:
            return

        xdata, ydata = event.artist.get_data()
        if len(event.ind) > 1 :
            # select by closest x value of picked points
            mx, my = event.mouseevent.xdata, event.mouseevent.ydata
            x_ind = np.searchsorted(xdata[event.ind], [mx])[0]
            evt_ind = event.ind[x_ind-1]
        else:
            evt_ind = event.ind
        x, y = xdata[evt_ind], ydata[evt_ind]
        #x, y = event.mouseevent.xdata, event.mouseevent.ydata
        annotation = self.annotations[event.artist.axes]
        if x is not None:
            if not self.display_all:
                # Hide any other annotation boxes...
                for ann in self.annotations.values():
                    ann.set_visible(False)
            # Update the annotation in the current axis..
            annotation.xy = x, y
            annotation.set_text(self.template % (x, y))
            annotation.set_visible(True)
            event.canvas.draw()

if __name__ == '__main__':

    import sys
    from PyQt4 import QtCore, QtGui
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

    t0 = np.arange(0.0, 10.0, 0.1)
    t1 = np.arange(0.0, 5.0, 0.02)

    y0 = np.sin(2*np.pi*t0)
    y1 = np.sin(2*np.pi*t1)

    app = QtGui.QApplication(sys.argv)

    window = QtGui.QMainWindow()
    main_frame = QtGui.QWidget()
    fig = Figure()
    canvas = FigureCanvas(fig)
    canvas.setParent(main_frame)
    ax = fig.add_subplot(1,1,1)

    vbox = QtGui.QVBoxLayout()
    vbox.addWidget(canvas)
    main_frame.resize(500,500)
    main_frame.setLayout(vbox)
    window.setCentralWidget(main_frame)
    lines = ax.plot(t0,y0,t1,y1)
    dc = DataCursor(lines)

    window.show()
    input("press any key when finished")
