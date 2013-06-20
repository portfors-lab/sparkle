import collections
import sys
import time

from PyQt4 import QtCore, QtGui
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from audiolab.plotting.abstract_figures import BasePlot

class BasicPlot(BasePlot):
    def __init__(self,*args,parent=None):
        BasePlot.__init__(self, (1,1), parent)
        # assumes input in the form of (xdata,ydata) tuples

        nlines = len(args)
        for arg in args:
            xdata, ydata = arg
            self.axs[0].plot(xdata,ydata)

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
        
        print('rows: ' + str(subplotrows) + ' cols: ' + str(subplotcols))

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

class SubPlots(BasePlot):
    def __init__(self,*args,callback=None,parent=None):
        nsubplots = len(args)
        BasePlot.__init__(self,(nsubplots,1),parent)
 
        # args are (xdata,ydata) tuples
        for iplot, ax in enumerate(self.axs):
            # divide argument tuple into x ,y data
            xdata = args[iplot][0]
            ydata = args[iplot][1]

            # the data could either be a single list representing data, 
            # or a list of sets of data

            # test to see if argument is nested list 
            # -- meaning multiple lines in plot
            if len(xdata) > 0 and isinstance(xdata[0], collections.Iterable): #isinstance(xdata[0], list):
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

class FlickPlot(BasePlot):
    def __init__(self,*args,callback=None,parent=None, titles=None):
        BasePlot.__init__(self,(1,1),parent,flickable=True)

        # accepts as args either a list of axes tuples... or a nd numpy array
        # and an xdata vector and iterate through the array
        self.titles = titles

        if isinstance(args[0], np.ndarray):
            self.is_ndarray = True
            # convert into tuple list first?
            # not most efficient, but makes flick mehods simpler
            self.xvector = args[1]
            data_array = args[0]
            dims = data_array.shape
            self.dims = dims
            self.current_plot = [0,]*(len(dims)-1)
            self.data_array = data_array
            self.plot_data((self.xvector,data_array[tuple(self.current_plot)]))
            print('title and data shape ', titles.shape,  data_array.shape)

        else:
            self.is_ndarray = False
            nsubplots = len(args)
            self.datalist = args

            # save dims for purposes of title - does not update atm!!!
            self.dims = (nsubplots, len(self.datalist[0][0]))

            # plot the first set of data
            self.current_plot = 0
            self.plot_data(self.datalist[0])
            

    def increment_current(self):
        # increment from rightmost index to leftmost
        ndims = len(self.dims)-1
        for idim in range(ndims):
            if self.current_plot[-idim - 1] < (self.dims[-idim - 2] - 1):
                self.current_plot[-idim-1] += 1
                #break when we find the lowest available increment
                break
            # reset this index to zero and move on to higher
            self.current_plot[-idim -1] = 0

    def decrement_current(self):
        ndims = len(self.dims)-1
        for idim in range(ndims):
            if self.current_plot[-idim - 1] > 0:
                self.current_plot[-idim-1] -= 1
                break
            self.current_plot[-idim -1] = self.dims[-idim -2] - 1

    def next_plot(self):
        if self.is_ndarray:
            self.increment_current()
            self.plot_data((self.xvector,self.data_array[tuple(self.current_plot)]))
        else:
            if self.current_plot < len(self.datalist)-1:
                self.current_plot +=1
                self.plot_data(self.datalist[self.current_plot])
        
        self.canvas.draw()

    def previous_plot(self):
        if self.is_ndarray:
            self.decrement_current()
            self.plot_data((self.xvector,self.data_array[tuple(self.current_plot)]))
        else:
            if self.current_plot > 0:
                self.current_plot -=1
                self.plot_data(self.datalist[self.current_plot])

        self.canvas.draw()

    def plot_data(self, data):
        #print(len(data))
        xdata = data[0]
        ydata = data[1]

        ax = self.axs[0]
        ax.cla()
        # test to see if argument is nested list 
        # -- meaning multiple lines in plot
        if len(xdata) > 0 and  isinstance(xdata[0], collections.Iterable): #isinstance(xdata[0], list):
            #add multiple lines to plot
            for iline in range(len(xdata)):
                #print(xdata.shape, ydata.shape)
                ax.plot(xdata[iline], ydata[iline])
        else:
            ax.plot(xdata, ydata)
        self.update_title()

    def update_title(self):
        if self.is_ndarray:
            current_plot = tuple(self.current_plot)
        else:
            current_plot = self.current_plot

        if self.titles is not None:
            titles = self.titles
            if len(titles.shape) == len(self.dims)-1:
                self.axs[0].set_title(titles[(current_plot)])
            elif len(titles.shape) == len(self.dims)-2:
                self.axs[0].set_title(titles[current_plot[:-1]] + ' rep ' + str(current_plot[-1]))
            else:
                self.axs[0].set_title(str(current_plot))
        else:
            self.axs[0].set_title('Data set ' + str(current_plot))


class AnimatedWindow(BasePlot):
    def __init__(self,*args,callback=None,parent=None):
        nsubplots = len(args)
        BasePlot.__init__(self,(nsubplots,1),parent)

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
            if len(xdata) > 0 and isinstance(xdata[0], collections.Iterable): #isinstance(xdata[0], list):
                #add multiple lines to plot
                for iline in range(len(xdata)):
                    ax.plot(xdata[iline], ydata[iline], animated=True)
            else:
                ax.plot(xdata, ydata, animated=True)

        # custom menu action
        live_subwindow = QtGui.QAction('live spawn', self)
        self.add_context_item((live_subwindow,self.spawn_live))

        self.callback = callback

        self.resize_mutex = QtCore.QMutex()
        
        self.cnt = 0
        self.live_progeny = []

        self.redraw()

    def spawn_live(self):
        print("event received")
        event = self.last_event
        for axnum, ax in enumerate(self.axs):
            if ax.contains(event)[0]:
                print("creating live sub window of axes ", axnum)
                #copy data to new figure (not live)
                lines = []
                for line in ax.lines:
                    ldata = line.get_data()
                    lines.append(ldata)
                new_fig = AnimatedWindow(*lines)

                # now go through and make colors match
                for iline, line in enumerate(ax.lines):
                    c = line.get_color()
                    new_fig.axs[iline].lines[0].set_color(c)
                new_fig.show()
                
                #we must keep a reference to the plots, otherwise they go away
                self.live_progeny.append((new_fig, axnum))

    def draw_line(self, axnum, linenum, xdata, ydata):
        try:
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

            # call this function on all linked subwindows
            for child, axn in self.live_progeny:
                if axn == axnum:
                    if child.active:
                        # live progeny only have 1 axes
                        child.draw_line(linenum, 0, xdata, ydata)
                    else:
                        # window was closed, remove from progeny list
                        #pass
                        self.live_progeny.remove((child, axn))
        except:
            print("WARNING : Problem drawing from Animated Window")

    def start_update(self, update_rate):
        # timer takes interval in ms. assuming rate in Hz, convert
        interval = int(max(1000/update_rate, 1))
        self.timer = self.startTimer(interval)

    def timerEvent(self, evt):
        self.callback()

    def redraw(self):
        if self.resize_mutex.tryLock():
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
                
            for iax, ax in enumerate(self.axs):
                xvals, yvals = saved_data[iax]                
                for line in ax.lines:
                    line.set_data(xvals,yvals)
                    ax.draw_artist(line)
                self.canvas.blit(ax.bbox)
            
            # this seems to be necessary to get background to show properly
            self.canvas.draw()
            
            self.resize_mutex.unlock()

    def resize_event(self):
        print("mpl resize event")

    def keyPressEvent(self,event):
        #print("key press event from AnimatedWindow")
        if event.text() == 'r':
            self.redraw()
        else:
            # pass keypress to parent classes
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



if __name__ == '__main__':
    import pickle

    t0 = np.arange(0.0, 10.0, 0.1)
    t1 = np.arange(0.0, 5.0, 0.02)

    y0 = np.sin(2*np.pi*t0)
    y1 = np.sin(2*np.pi*t1)
    y2 = 2*np.sin(4*2*np.pi*t0)
    y3 = np.cos(4*np.pi*t0)
    y4 = np.sin(6*np.pi*t1)

    d = [(t0,y0), (t1,y1), ((t0,y2),(t0,y3)), (t1,y4)]

    """
    fft_data = np.load("cal0_ffttraces.npy")
    with open("cal0_index.pkl", 'rb') as cfo:
        index = pickle.load(cfo)
    npts = fft_data.shape[-1]*2
    freq = np.arange(npts)/(npts/400000)
    freq = freq[:(npts/2)] #single sided    

    fdb_dict = index[0]
    #label_array = [['' for x in range(fft_data.shape[1])] for y in range(fft_data.shape[0])]
    #label_array = np.array(fft_data.shape[:-2], itemsize=60)
    label_array = np.empty(fft_data.shape[:-2], dtype=np.dtype(('U',60)))
    for fdb, ifdb in fdb_dict.items():
        label_array[ifdb[0],ifdb[1]] = "Frequency: %d, Intensity: %d" % fdb
    """

    app = QtGui.QApplication(sys.argv)
    #myapp = FlickPlot(fft_data,freq,titles=label_array)
    myapp = FlickPlot(*d, titles=np.array(['meow', 'spam', 'wow', 'ducks']))
    myapp.show()
    sys.exit(app.exec_())
