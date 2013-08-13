from traits.etsconfig.etsconfig import ETSConfig
ETSConfig.toolkit = "qt4"
from enthought.enable.api import Window
from enthought.chaco.api import VPlotContainer, ArrayPlotData, Plot

import sys, random
import numpy as np
from PyQt4 import QtGui, QtCore

class LiveWindow(QtGui.QMainWindow):
    def __init__(self, nsubplots):
        QtGui.QMainWindow.__init__(self)
        self.mainWidget = QtGui.QWidget(self) # dummy widget to contain layout manager
        self.plotview = Plotter(self, nsubplots)

        layout = QtGui.QVBoxLayout(self.mainWidget)
        layout.setObjectName("superlayout")
        layout.addWidget(self.plotview.widget)
        #self.setLayout(layout)

        self.resize(600,400)

        self.setCentralWidget(self.mainWidget)

    def draw_line(self, axnum, linenum, x, y):
        self.plotview.update_data(axnum, linenum, x, y)



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
            plots.append(Plot(idata, padding=50, border_visible=True))
            plots[-1].plot(("x", "y"), name="data plot", color="green")
            plots[-1].padding_top = 10
            plots[-1].padding_bottom = 10

        plots[0].padding_bottom = 30
        plots[-1].padding_top = 30
        container = VPlotContainer(*plots)
        container.spacing = 0

        return Window(parent, -1, component=container)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    plot = LiveWindow(2)
    plot.resize(600, 400)
    plot.show()

    x = np.arange(200)
    y = random.randint(0,10) * np.sin(x)
    plot.draw_line(0,0,x,y)

    sys.exit(app.exec_())