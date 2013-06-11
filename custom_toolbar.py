from PyQt4 import QtCore, QtGui
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from datacursor import DataCursor

class CustomToolbar(NavigationToolbar):
    def __init__(self, canvas, parent=None, flickable=False):
        NavigationToolbar.__init__(self,canvas,parent)
        self.canvas = canvas
        self.parent = parent

        #remove unwanted buttons
        layout = self.layout()
        builtin_buttons = []
        for ichild in range(layout.count()):
            child = layout.itemAt(ichild)
            #print(child.widget().__class__.__name__)
            builtin_buttons.append(child.widget())
        
        # to remove default button from toolbar...
        # buttons in order, 8 == save 
        #builtin_buttons[8].setParent(None)

        # in order to insert buttons it seems I must take
        # the last widget off and put it back on when finished
        # except I don't know how to put it back on...
        xylabel =  builtin_buttons[10]
        xylabel.setParent(None)

        # edit callback
        builtin_buttons[5].toggled.connect(self.zoom_mod)

        #add new toolbar items
        #self.grid_cb = QtGui.QCheckBox("Show &Grid")
        #self.grid_cb.setChecked(False)
        
        #self.grid_cb.stateChanged.connect(self.toggle_grid)
        #self.addWidget(self.grid_cb)

        # datacursor toggle button
        self.datacursor_tb = QtGui.QToolButton(self)
        self.datacursor_tb.setIcon(QtGui.QIcon("dc_icon.png"))
        self.datacursor_tb.setCheckable(True)
        self.datacursor_tb.clicked[bool].connect(self.use_cursors)

        self.addWidget(self.datacursor_tb)

        self.addWidget(xylabel)

        if flickable:
            # add forward and back buttons to flick between plots
            flick_next_btn = QtGui.QPushButton(">")
            flick_next_btn.clicked.connect(self.flick_next)

            flick_prev_btn = QtGui.QPushButton("<")
            flick_prev_btn.clicked.connect(self.flick_prev)

            self.addWidget(flick_prev_btn)
            self.addWidget(flick_next_btn)

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
            lines = []
            for ax in self.canvas.figure.axes:
                #self.canvas.mpl_connect('pick_event', DataCursor(ax))
                for line in ax.lines:
                    #line.set_picker(5)
                    # not sure that adding abunch of empty annotations to
                    # all lines is the best way, but works for now
                    lines.append(line)
            self.dc = DataCursor(lines, template='x: %d\ny: %0.5f')
        else:
            while len(self.dc.pick_events) > 0:
                pe = self.dc.pick_events.pop()
                self.canvas.mpl_disconnect(pe)

    def flick_next(self):
        # if it is a flick plot we assume that next_plot method exists
        self.parent.next_plot()

    def flick_prev(self):
        self.parent.previous_plot()

    def keyPressEvent(self,event):
        print("key press event from toolbar")
        super().keyPressEvent(event)
