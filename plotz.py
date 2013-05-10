from PyQt4 import QtCore, QtGui
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import functools

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
            
class SimplePlot(QtGui.QMainWindow):
    def __init__(self,*args,parent=None):
        #parent=None
        QtGui.QMainWindow.__init__(self,parent)

        if len(args) == 1:
            [data] = args[0]
            [xvals] = range(len(data))
        else:
            if len(args) != 2:
                print("data arguments must be in x,y array lists")
                return
            data = args[1]
            xvals = args[0]

        self.setWindowTitle('Display')

        self.main_frame = QtGui.QWidget()

        self.fig = Figure((5.0,4.0), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)

        ax = self.fig.add_subplot(111)
        self.mpl_toolbar = CustomToolbar(self.canvas, self.main_frame)
        for idata in range(len(data)):
            ax.plot(xvals[idata],data[idata])

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)

        self.main_frame.resize(500,500)
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)


class SubPlots(QtGui.QMainWindow):
    def __init__(self,*args,parent=None):
        #parent=None
        QtGui.QMainWindow.__init__(self,parent)
 
        if len(args)%2 != 0:
            print("data arguments must be in x,y array pairs")
            return

        self.main_frame = QtGui.QWidget()

        nsubplots = int(len(args)/2)

        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)

        for isubplot in range(nsubplots):
            ax = self.fig.add_subplot(nsubplots,1,isubplot+1)
            #test to see if argument is nested list -- meaning multiple lines in plot
            if len(args[isubplot*2]) > 0 and isinstance(args[isubplot*2][0], list):
                #add multiple lines to plot
                for iline in range(len(args[isubplot*2])):
                    ax.plot(args[isubplot*2][iline],args[(isubplot*2)+1][iline])
            else:
                ax.plot(args[isubplot*2],args[(isubplot*2)+1])

        self.mpl_toolbar = CustomToolbar(self.canvas, self.main_frame)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)

        self.main_frame.resize(500,500)
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)

        self.nsubplots = nsubplots

        self.active = True
        #self.show()

        """
        axis_action = QtGui.QAction('adjust axis', self)
        axis_action.triggered.connect(self.adjust_axis)
        self.popMenu = QtGui.QMenu( self )
        self.popMenu.addAction( axis_action )

        self.canvas.mpl_connect('button_press_event', 
                                    self.on_figure_press)
        """

        self.fig.canvas.mpl_connect('button_release_event', self.canvas_context)

        self.children = []

    def update_data(self, xdata, ydata, axnum=1):
        self.fig.axes[axnum].lines[0].set_data(xdata,ydata)
        self.fig.canvas.draw()

    def autoscale_y(self, event):
        for ax in self.fig.axes:
            if ax.contains(event)[0]:
                x0, x1 = ax.get_xlim()
                #set to zero so that we may use to get the max of multiple lines in an axes
                y0, y1 = float("inf"), float("-inf")
                #find y max and min for current x range
                for iline in ax.lines:
                    xdata, ydata = iline.get_data()
                    if len(xdata) > 0:
                        #placeholder lines have empty data
                        print("xdata len %r, ydata len %r, x0 %r, x1 %r" % (len(xdata), len(ydata), x0, x1))
                        #find the indicies of the xlims and use to take the min and max of same y range
                        xind0 = (np.abs(xdata-x0)).argmin()
                        xind1 = (np.abs(xdata-x1)).argmin()
                        print("x indices %r, %r" % (xdata[xind0], xdata[xind1]))
                        y0 = min(np.amin(ydata[xind0:xind1]),y0)
                        y1 = max(np.amax(ydata[xind0:xind1]),y1)
                        print("y data lims %r %r" % (y0, y1))
                ax.set_ylim(y0,y1)
                self.fig.canvas.draw()


    def autoscale_x(self,event):
        for ax in self.fig.axes:
            if ax.contains(event)[0]:
                x0 = float("inf")
                x1 = float("-inf")
                for iline in ax.lines:
                    xdata = iline.get_xdata()
                    if len(xdata) > 0:
                        #placeholder lines have empty data
                        x0 = min(xdata[0], x0)
                        x1 = max(xdata[-1], x1)
                ax.set_xlim(x0,x1)
                self.fig.canvas.draw()

    def spawn_child(self, event):
        for ax in self.fig.axes:
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
                self.children.append(new_fig)

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

    #def contextMenuEvent(self, event):

    def closeEvent(self,event):
        #added this so that I can test whether user has closed figure - is there are better way?
        self.active = False
        QtGui.QMainWindow.closeEvent(self,event)
