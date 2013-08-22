# from traits.etsconfig.etsconfig import ETSConfig
from enthought.etsconfig.etsconfig import ETSConfig
ETSConfig.toolkit = "qt4"
from enthought.enable.api import Window
from enthought.chaco.api import VPlotContainer, ArrayPlotData, Plot
from chaco.tools.api import PanTool, ZoomTool, DragZoom

import sys, random
import numpy as np
from PyQt4 import QtGui, QtCore

class LiveWindow(QtGui.QMainWindow):
    def __init__(self, nsubplots):
        QtGui.QMainWindow.__init__(self)
        self.mainWidget = QtGui.QWidget(self) # dummy widget to contain layout manager
        self.plotview = Plotter(self, nsubplots)

        layout = QtGui.QVBoxLayout(self.mainWidget)
        layout.setObjectName("masterlayout")
        layout.addWidget(self.plotview.widget)

        self.resize(600,400)

        self.setCentralWidget(self.mainWidget)

    def draw_line(self, axnum, linenum, x, y):
        self.plotview.update_data(axnum, linenum, x, y)

class ScrollingWindow(QtGui.QMainWindow):
    def __init__(self, nsubplots, deltax, windowsize=1):
        QtGui.QMainWindow.__init__(self)
        self.mainWidget = QtGui.QWidget(self) # dummy widget to contain layout manager
        self.plotview = ScrollingPlotter(self, nsubplots, deltax, windowsize)

        layout = QtGui.QVBoxLayout(self.mainWidget)
        layout.setObjectName("masterlayout")
        layout.addWidget(self.plotview.widget)

        self.resize(600,400)

        self.setCentralWidget(self.mainWidget)

    def append(self, y, axnum=0):
        self.plotview.update_data(axnum, y)


class Plotter():
    def __init__(self, parent, nsubplots):
        self.plotdata = []
        for isubplot in range(nsubplots):
            self.plotdata.append(ArrayPlotData(x=np.array([]),  y=np.array([])))
        self.window = self.create_plot(parent)
        self.widget = self.window.control
        

    def update_data(self, axnum, linenum, x, y):
        self.plotdata[axnum].set_data("x", x)
        self.plotdata[axnum].set_data("y", y)
        self.window.component.components[axnum].request_redraw()

    def create_plot(self, parent):
        plots = []
        for idata in self.plotdata:
            plot = Plot(idata, padding=50, border_visible=True)
            plot.plot(("x", "y"), name="data plot", color="green")
            plot.padding_top = 10
            plot.padding_bottom = 10
            plot.tools.append(PanTool(plot))
            plot.tools.append(ZoomTool(plot))
            plots.append(plot)

        plots[0].padding_bottom = 30
        plots[-1].padding_top = 30
        container = VPlotContainer(*plots)
        container.spacing = 0

        return Window(parent, -1, component=container)

class ScrollingPlotter(Plotter):
    def __init__(self, parent, nsubplots, deltax, windowsize=1):
        Plotter.__init__(self, parent, nsubplots)
        self.plots = self.window.component.components
        # time steps between data points
        self.deltax = deltax
        print "delta x", deltax
        # time window of display (seconds)
        self.windowsize = windowsize
        for plot in self.plots:
            plot.range2d.x_range.low = 0
            plot.range2d.x_range.high = windowsize


        self.plotdata[0].set_data('x', [-1])
        self.plotdata[0].set_data('y', [0])

    def update_data(self, y, axnum=0):
        # append the y data and append appropriate number of 
        # x points
        points_to_add = len(y)
        xdata = self.plotdata[axnum].get_data('x')
        x_to_append = np.arange(xdata[-1]+self.deltax, 
                            xdata[-1]+self.deltax+(self.deltax*points_to_add),
                            self.deltax)
        xdata = np.append(xdata, x_to_append)
        self.plotdata[axnum].set_data("x", xdata)
        ydata = self.plotdata[axnum].get_data('y')
        ydata = np.append(ydata,y)
        self.plotdata[axnum].set_data("y", ydata)
        
        # now scroll axis limits
        if self.plots[axnum].range2d.x_range.high <= xdata[-1]:
            self.plots[axnum].range2d.x_range.high += self.deltax*points_to_add
            self.plots[axnum].range2d.x_range.low += self.deltax*points_to_add


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    plot = LiveWindow(2)
    plot.resize(600, 400)
    plot.show()

    x = np.arange(200)
    y = random.randint(0,10) * np.sin(x)
    plot.draw_line(0,0,x,y)

    sys.exit(app.exec_())