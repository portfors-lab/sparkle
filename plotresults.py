from PyQt4 import QtCore, QtGui
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar

from custom_toolbar import CustomToolbar

class ResultsPlot(QtGui.QMainWindow):
    def __init__(self,data,parent=None):
        #parent=None
        QtGui.QMainWindow.__init__(self,parent)
        self.setWindowTitle('Results')
        self.data=data
        self.create_main_frame()
        self.create_menu()
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
            ax = self.fig.add_subplot(subplotrows,subplotcols,itrace)
            ax.plot(self.data[:,itrace], picker=5)

        #self.fig.canvas.mpl_connect('button_press_event', self.axes_click)
        self.fig.canvas.mpl_connect('pick_event', self.line_click)
        self.fig.canvas.mpl_connect('button_release_event', self.line_drop)

        self.mpl_toolbar = CustomToolbar(self.canvas, self.main_frame)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)

        self.main_frame.resize(500,500)
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)
        self.from_axes = None

    def create_menu(self):
        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)

        resetAction = QtGui.QAction('Reset plots', self)
        resetAction.triggered.connect(self.reset_plots)

        #self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(resetAction)
        fileMenu.addAction(exitAction)

    def reset_plots(self):
        print('Reset \'em')
        for itrace in range(self.data.shape[1]):
            #clear each axes and plot data anew
            ax = self.fig.axes[itrace]
            ax.cla()
            ax.plot(self.data[:,itrace], picker=5)
        self.fig.canvas.draw()

    def axes_click(self,event):
        if event.inaxes == None:
            return
        ax = event.inaxes
        contains, other = ax.lines[0].contains(event)
        if contains:
            print('you clicked the line')
            print(contains)

    def line_click(self,event):
        self.from_axes = event.mouseevent.inaxes
        print('line click, {}'.format(len(self.from_axes.lines)))

    def line_drop(self,event):
        if self.from_axes != None and event.inaxes != None and self.from_axes != event.inaxes:
            print('drag n drop')
            dropax = event.inaxes
            print('lines to move {}'.format(len(self.from_axes.lines)))
            nmovelines = len(self.from_axes.lines)
            for iline in range(nmovelines):
                #self.from_axes.lines.remove(iline)
                iline = self.from_axes.lines[0]
                del self.from_axes.lines[0]
                #dropax.add_line(iline)
                xdata, ydata = iline.get_data()
                #must transpose the data, otherwise is plots each points as it's own line
                dropax.plot(xdata.transpose(),ydata.transpose(), picker=5)
            self.canvas.draw()
            print('lines in drop axes: {}'.format(len(dropax.lines)))
            print('-'*30)
            self.from_axes = None
        else:
            self.from_axes = None
            

