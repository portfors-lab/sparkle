from PyQt4 import QtCore, QtGui
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar


CONFIGURE_SUBPLOTS_BTN_POS = 6

class CustomToolbar(NavigationToolbar):
    def __init__(self, canvas, parent=None):
        NavigationToolbar.__init__(self,canvas,parent)
        self.canvas = canvas
        #remove unwanted buttons
        children = self.children()
        builtin_buttons = []
        for child in children:
            #print(child.__class__.__name__)
            if type(child) == QtGui.QToolButton:
                builtin_buttons.append(child)
        #buttons in order, 7 == save 
        builtin_buttons[7].setParent(None)

        # try to edit callback
        builtin_buttons[5].toggled.connect(self.new_zoom)

        #add new toolbar items
        self.grid_cb = QtGui.QCheckBox("Show &Grid")
        self.grid_cb.setChecked(False)
        
        self.grid_cb.stateChanged.connect(self.toggle_grid)
        self.addWidget(self.grid_cb)

    def toggle_grid(self):
        for ax in self.canvas.figure.axes:
            ax.grid(self.grid_cb.isChecked())
        self.canvas.draw()

    def new_zoom(self, checked):
        #print("update canvas draw")
        if checked:
            # add a draw command after every button up event
            self.cid = self.canvas.mpl_connect('button_release_event', self.draw_update)
        else:
            # clear draw command update
            self.canvas.mpl_disconnect(self.cid)

    def draw_update(self,event):
        print('updating after button release')
        self.canvas.draw()
