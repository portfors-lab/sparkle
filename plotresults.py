from PyQt4 import QtCore, QtGui
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

class ResultsPlot(QtGui.QMainWindow):
    def __init__(self,data,parent=None):
        #parent=None
        QtGui.QMainWindow.__init__(self,parent)
        self.setWindowTitle('Results')
        self.data=data
        self.create_main_frame()
        #self.show()
        #self.exec_()
    def create_main_frame(self):
        self.main_frame = QtGui.QWidget()
        #assume columns are traces
        print("data size: "+str(self.data.shape))
        print(self.data.shape[0])
        print(self.data.shape[1])
        subplotcols = np.floor(np.sqrt(self.data.shape[1]))
        subplotrows = np.ceil(self.data.shape[1]/subplotcols)
        print('rows: '+str(subplotrows)+' cols: '+str(subplotcols))

        #make a new window to display acquired data
        self.fig = Figure((5.0,4.0), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)

        self.axes = [None]*self.data.shape[1]
        #make a new window to display acquired data
        for itrace in range(self.data.shape[1]):
            #add the axes in subplots
            #self.axes[iplot] = self.fig.add_subplot(subplotrows,subplotcols,
                                                    #iplot)
            #self.axes[iplot].plot(self.data[:,iplot])

        #self.main_frame.addWidget(self.canvas)
            ax = self.fig.add_subplot(subplotrows,subplotcols,itrace)
            ax.plot(self.data[:,itrace])

        grid = QtGui.QGridLayout()
        grid.addWidget(self.canvas,0,0)

        self.main_frame.resize(500,500)
        self.main_frame.setLayout(grid)
        self.setCentralWidget(self.main_frame)
