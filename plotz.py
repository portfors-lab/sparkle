from PyQt4 import QtCore, QtGui
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from abstract_figures import BasePlot

import time

class ResultsPlot(BasePlot):
    def __init__(self,data,parent=None):
        ncols = np.floor(np.sqrt(data.shape[1]))
        nrows = np.ceil(data.shape[1]/subplotcols)
        BasePlot.__init__(self,(nrows,ncols),arent)
        self.setWindowTitle('Results')
        self.data=data
        self.create_main_frame()
        self.create_menu()
        
    def create_main_frame(self):
        
        #assume columns are traces
        print("data size: "+str(self.data.shape))
        print(self.data.shape[0])
        print(self.data.shape[1])
        
        print('rows: '+str(subplotrows)+' cols: '+str(subplotcols))

        #make a new window to display acquired data
        for itrace, ax in enumerate(self.axs):
            # add the axes in subplots
            ax.plot(self.data[:,itrace], picker=5)

        #self.fig.canvas.mpl_connect('button_press_event', self.axes_click)
        self.fig.canvas.mpl_connect('pick_event', self.line_click)
        self.fig.canvas.mpl_connect('button_release_event', self.line_drop)

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
            
class SimplePlot(BasePlot):
    def __init__(self,*args,parent=None):
        BasePlot.__init__(self,(1,1),parent)

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

        for idata in range(len(data)):
            self.ax[0].plot(xvals[idata],data[idata])

class SubPlots(BasePlot):
    def __init__(self,*args,callback=None,parent=None):
        nsubplots = len(args)
        BasePlot.__init__(self,(nsubplots,1),parent)
 
        for iplot, ax in enumerate(self.axs):
            # divide argument tuple into x ,y data
            xdata = args[iplot][0]
            ydata = args[iplot][1]

            # the data could either be a single list representing data, 
            # or a list of sets of data

            # test to see if argument is nested list 
            # -- meaning multiple lines in plot
            if len(xdata) > 0 and isinstance(xdata[0], list):
                #add multiple lines to plot
                for iline in range(len(xdata)):
                    ax.plot(xdata[iline], ydata[iline])
            else:
                ax.plot(xdata, ydata)

        for ax in self.axs:
            ax.set_xlim(0,5)
            ax.set_ylim(-10,10)

        self.nsubplots = nsubplots

    def update_data(self, xdata, ydata, axnum=1):
        self.axs[axnum].lines[0].set_data(xdata,ydata)
        self.canvas.draw()

    def draw_line(self, axnum, linenum, xdata, ydata):
        self.axs[axnum].lines[linenum].set_data(xdata,ydata)
        self.canvas.draw()
        

class AnimatedWindow(BasePlot):
    def __init__(self,*args,callback=None,parent=None):
        nsubplots = len(args)
        BasePlot.__init__(self,(nsubplots,1),parent)

        for ax in self.axs:
            ax.set_xlim(0,5)
            ax.set_ylim(-10,10)

        self.canvas.draw()

        # save these backgrounds for animation
        self.ax_backgrounds = [None]*nsubplots
        for isubplot in range(nsubplots):
            self.ax_backgrounds[isubplot] = self.canvas.copy_from_bbox(self.axs[isubplot].bbox)

        # now do first plot with provided data, 
        # this will also set how many line each plot will contain

        for ax in self.canvas.figure.axes:
            # divide argument tuple into x ,y data
            iplot = self.canvas.figure.axes.index(ax)
            xdata = args[iplot][0]
            ydata = args[iplot][1]

            # the data could either be a single list representing data, or a list of sets of data

            # test to see if argument is nested list 
            # -- meaning multiple lines in plot
            if len(xdata) > 0 and isinstance(xdata[0], list):
                #add multiple lines to plot
                for iline in range(len(xdata)):
                    ax.plot(xdata[iline], ydata[iline], animated=True)
            else:
                ax.plot(xdata, ydata, animated=True)

        self.callback = callback

        self.resize_mutex = QtCore.QMutex()
        
        self.cnt = 0

    def draw_line(self, axnum, linenum, xdata, ydata):
        self.canvas.restore_region(self.ax_backgrounds[axnum])
        self.axs[axnum].lines[linenum].set_data(xdata,ydata)

        # draw everything in this axis, to not loose other lines
        for line in self.axs[axnum].lines:
            self.axs[axnum].draw_artist(line)
        self.canvas.blit(self.axs[axnum].bbox)

        if self.cnt == 0:
            # TODO: this shouldn't be necessary, but if it is excluded the
            # canvas outside the axes is not initially painted.
            self.canvas.draw()
            self.cnt += 1

    def start_update(self, update_rate):
        # timer takes interval in ms. assuming rate in Hz, convert
        interval = int(max(1000/update_rate, 1))
        self.timer = self.startTimer(interval)

    def timerEvent(self, evt):
        self.callback()

    def redraw(self):
        if self.resize_mutex.tryLock():
            print("redraw")
            saved_data = []
            for ax in self.axs:
                nlines = len(ax.lines)
                for line in ax.lines:
                    saved_data.append(line.get_data())
                axlims = ax.axis()
                ax.clear()
                for i in range(nlines):
                    ax.plot([],[])
                ax.set_ylim(axlims[2], axlims[3])
                ax.set_xlim(axlims[0], axlims[1])
            
            self.canvas.draw()

            for iax in range(len(self.axs)):
                self.ax_backgrounds[iax] = self.canvas.copy_from_bbox(self.axs[iax].bbox)

            for xvals, yvals in saved_data:
                #xvals, yvals = saved_data[iax]
                for ax in self.axs:
                    for line in ax.lines:
                        line.set_data(xvals,yvals)
                        ax.draw_artist(line)
                    self.canvas.blit(ax.bbox)
            
            # this seems to be necessary to get background to show properly
            self.canvas.draw()
            self.resize_mutex.unlock()

    def keyPressEvent(self,event):
        print("key press event from AnimatedWindow")
        if event.text() == 'r':
            print("arrrrrrr")
            self.redraw()
        else:
            super().keyPressEvent(event)
    
class ScrollingPlot(BasePlot):
    def __init__(self,*args,callback=None,parent=None):
        nsubplots = len(args)
        BasePlot.__init__(self,(nsubplots,1),parent)
        # TODO : write this class
 #if ndata/aisr > lims[1]:
                #print("change x lim, {} to {}".format((ndata-n)/aisr,((ndata-n)/aisr)+XLEN))
                #self.sp.figure.axes[1].set_xlim((ndata-n)/aisr,((ndata-n)/aisr)+XLEN)
                # must use regular draw to update axes tick labels
                #self.sp.draw()
                # update saved background so scale stays accurate
                #self.sp.axs_background = self.sp.copy_from_bbox(self.sp.figure.axes[1].bbox)
