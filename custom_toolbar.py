from PyQt4 import QtCore, QtGui
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib import cbook
from matplotlib import offsetbox
from matplotlib import text
import numpy as np

CONFIGURE_SUBPLOTS_BTN_POS = 6

class CustomToolbar(NavigationToolbar):
    def __init__(self, canvas, parent=None):
        NavigationToolbar.__init__(self,canvas,parent)
        self.canvas = canvas
        #remove unwanted buttons
        layout = self.layout()
        #children = self.children()
        builtin_buttons = []
        for ichild in range(layout.count()):
            child = layout.itemAt(ichild)
            print(child.widget().__class__.__name__)
            #if type(child) == QtGui.QToolButton:
            builtin_buttons.append(child.widget())
        print(len(builtin_buttons))

        # to remove default button from toolbar...
        #buttons in order, 7 == save 
        #builtin_buttons[7].setParent(None)

        # in order to insert buttons it seems I must take
        # the last widget off and put it back on when finished
        xylabel =  builtin_buttons[10]
        xylabel.setParent(None)

        # try to edit callback
        builtin_buttons[5].toggled.connect(self.zoom_mod)

        #add new toolbar items
        #self.grid_cb = QtGui.QCheckBox("Show &Grid")
        #self.grid_cb.setChecked(False)
        
        #self.grid_cb.stateChanged.connect(self.toggle_grid)
        #self.addWidget(self.grid_cb)

        # datacursor toggle button
        #self.datacursor_tb = QtGui.QPushButton("dc")
        
        self.datacursor_tb = QtGui.QToolButton(self)
        self.datacursor_tb.setIcon(QtGui.QIcon("dc_icon.png"))
        self.datacursor_tb.setCheckable(True)
        self.datacursor_tb.clicked[bool].connect(self.use_cursors)

        self.addWidget(self.datacursor_tb)

        print(xylabel)
        self.addWidget(xylabel)

    def toggle_grid(self):
        for ax in self.canvas.figure.axes:
            ax.grid(self.grid_cb.isChecked())
        self.canvas.draw()

    def zoom_mod(self, checked):
        if checked:
            # add a draw command after every button up event
            self.cid = self.canvas.mpl_connect('button_release_event', self.draw_update)
        else:
            # clear draw command update
            self.canvas.mpl_disconnect(self.cid)

    def draw_update(self,event):
        # repaint canvas after button release -- this is to
        # make sure the toolbar works properly with animated windows
        self.canvas.draw()

    def use_cursors(self, active):
        if active:
            for ax in self.canvas.figure.axes:
                #self.canvas.mpl_connect('pick_event', DataCursor(ax))
                for line in ax.lines:
                    #line.set_picker(5)
                    pass
            self.dc = DataCursor([self.canvas.figure.axes[2].lines[0]], template='x: %d\ny: %0.5f')
        else:
            while len(self.dc.pick_events) > 0:
                pe = self.dc.pick_events.pop()
                self.canvas.mpl_disconnect(pe)

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
        offsetbox.DraggableAnnotation(annotation)
        return annotation

    def __call__(self, event):
        """Intended to be called through "mpl_connect"."""
        # Rather than trying to interpolate, just display the clicked coords
        # This will only be called if it's within "tolerance", anyway.
        if type(event.artist) == text.Annotation:
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

def find_closest_index(xdata, ydata, y_loc, x_loc):
    # given an array and a y value, return x index of closest
    # array element
    x_ind = np.searchsorted(xdata, [x_loc])[0]
