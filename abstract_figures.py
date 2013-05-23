import functools

import numpy as np
from PyQt4 import QtCore, QtGui
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

from custom_toolbar import CustomToolbar

class BasePlot(QtGui.QMainWindow):
    def __init__(self,dims,parent=None):
        QtGui.QMainWindow.__init__(self,parent)

        if len(dims) != 2:
            raise Exception("Incorrect number of subplot dimensions given. Expected 2, recieved {}".format(len(dims)))

        self.main_frame = QtGui.QWidget()

        nrows = dims[0]
        ncols = dims[1]
        nsubplots = nrows*ncols

        fig = Figure()
        self.canvas = FigureCanvas(fig)
        self.canvas.setParent(self.main_frame)

        self.axs = []
        for iax in range(nsubplots):
            self.axs.append( fig.add_subplot(nrows,ncols,iax+1) )

        self.mpl_toolbar = CustomToolbar(self.canvas, self.main_frame)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)

        self.main_frame.resize(500,500)
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)

        self.canvas.mpl_connect('button_release_event', 
                                self.canvas_context)

        self.progeny = []
        self.active = True

    def canvas_context(self, event):
        if event.button == 3:
            if event.inaxes:
                yaxis_action = QtGui.QAction('autoscale y', self)
                yaxis_action.triggered.connect(functools.partial(self.autoscale_y,event))
                xaxis_action = QtGui.QAction('autoscale x', self)
                xaxis_action.triggered.connect(functools.partial(self.autoscale_x,event))
                spawn_action = QtGui.QAction('spawn', self)
                spawn_action.triggered.connect(functools.partial(self.spawn_child,event))
                popMenu = QtGui.QMenu(self)
                popMenu.addAction(yaxis_action)
                popMenu.addAction(xaxis_action)
                popMenu.addAction(spawn_action)
                figheight = self.canvas.height()
                point = QtCore.QPoint(event.x, figheight - event.y)
                popMenu.exec(self.canvas.mapToGlobal(point))

    def autoscale_y(self, event):
        for ax in self.axs:
            if ax.contains(event)[0]:
                self.ylim_auto(self,[ax])

    def ylim_auto(self,axs):
        for ax in axs:
            x0, x1 = ax.get_xlim()
            #set to zero so that we may use to get the max of multiple lines in an axes
            y0, y1 = float("inf"), float("-inf")
            #find y max and min for current x range
            for iline in ax.lines:
                xdata, ydata = iline.get_data()
                if len(xdata) > 0:
                    # placeholder lines have empty data
                
                    # find the indicies of the xlims and use to take 
                    # the min and max of same y range
                    xind0 = (np.abs(xdata-x0)).argmin()
                    xind1 = (np.abs(xdata-x1)).argmin()
                        
                    y0 = min(np.amin(ydata[xind0:xind1]),y0)
                    y1 = max(np.amax(ydata[xind0:xind1]),y1)
                       
            ax.set_ylim(y0,y1)
            self.canvas.draw()


    def autoscale_x(self,event):
        for ax in self.axs:
            if ax.contains(event)[0]:
                self.xlim_auto([ax])

    def xlim_auto(self, axs):
        for ax in axs:
            x0 = float("inf")
            x1 = float("-inf")
            for iline in ax.lines:
                xdata = iline.get_xdata()
                if len(xdata) > 0:
                    #placeholder lines have empty data
                    x0 = min(xdata[0], x0)
                    x1 = max(xdata[-1], x1)
            ax.set_xlim(x0,x1)
            self.canvas.draw()

    def spawn_child(self, event):
        for ax in self.axs:
            if ax.contains(event)[0]:
                #copy data to new figure (not live)
                xdatas = []
                ydatas = []
                for iline in ax.lines:
                    xdata, ydata = iline.get_data()
                    xdatas.append(xdata)
                    ydatas.append(ydata)
                new_fig = SimplePlot(xdatas, ydatas)
                new_fig.show()
                #we must keep a reference to the plots, otherwise they go away
                self.progeny.append(new_fig)

    def keyPressEvent(self,event):
        print("key press event from BasePlot")
        if event.text() == 'r':
            print("gaaaaarr")

    def closeEvent(self,event):
        # added this so that I can test whether user has closed figure 
        # - is there are better way?
        self.active = False
        QtGui.QMainWindow.closeEvent(self,event)
