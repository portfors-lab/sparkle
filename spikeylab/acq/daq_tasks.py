try:
    from PyDAQmx import *
except:
    from daqmx_stub import *
    from ctypes import *

    import logging
    logger = logging.getLogger('main')
    logger.warning('ERROR IMPORTING DEVICE DRIVERS, RUNNING IN DEVELOPMENT MODE')

import numpy as np

class AITask(Task):
    """Class for managing continuous input with NI devices
    
    :param chans: Analog Input channels to gather data from
    :type chans: list<str>
    :param samplerate: Sampling frequency (Hz) at which data points are collected
    :type samplerate: int
    :param bufsize: length (in samples) of the data buffer for each channel
    :type bufsize: int
    :param clksrc: source terminal for the sample clock, default is internal clock
    :type clksrc: str
    """
    def __init__(self, chans, samplerate, bufsize, clksrc=""):
        Task.__init__(self)
        if isinstance(chans, basestring):
            chan_str = chans
            self.nchans = 1
        else:
            chan_str = ','.join(chans)
            self.nchans = len(chans)
        self.CreateAIVoltageChan(chan_str, u"", DAQmx_Val_Cfg_Default,
                                -10.0, 10.0, DAQmx_Val_Volts, None)
        self.CfgSampClkTiming(clksrc,samplerate, DAQmx_Val_Rising, 
                              DAQmx_Val_ContSamps, bufsize)
        #self.AutoRegisterEveryNSamplesEvent(DAQmx_Val_Acquired_Into_Buffer,100,0)
        self.AutoRegisterDoneEvent(0)

    def start(self):
        """Begin acquistition"""
        self.StartTask()

    def register_callback(self, fun, npts):
        """ Provide a function that to be executed periodically on data collection
        
        :param fun: the function that gets called, it must have a single positional argument that will be the data buffer read
        :type fun: function
        :param npts: The number of data points collected before the function is called.
        :type npts: int
        """
        self.callback_fun = fun
        self.n = npts
        self.AutoRegisterEveryNSamplesEvent(DAQmx_Val_Acquired_Into_Buffer,
                                            npts, 0, name=u"_run_callback")
    def _run_callback(self):
        inbuffer = self._read().squeeze()
        self.callback_fun(inbuffer)

    def _read(self):
        r = c_int32()
        inbuffer = np.zeros(self.n*self.nchans)
        self.ReadAnalogF64(self.n,10.0,DAQmx_Val_GroupByChannel,
                            inbuffer, self.n*self.nchans, byref(r), None)
        data = inbuffer.reshape(self.nchans, self.n)
        return data

    def stop(self):
        """Halt the acquisition"""
        try:
            self.StopTask()
            self.ClearTask()
        except DAQError:
            pass

class AOTask(Task):
    """Class for managing continuous analog output with NI devices
    
    :param chans: Analog output channels to generate data on
    :type chans: list<str>
    :param samplerate: Sampling frequency (Hz) at which data points generated
    :type samplerate: int
    :param bufsize: length (in samples) of the data buffer for each channel
    :type bufsize: int
    :param clksrc: source terminal for the sample clock, default is internal clock
    :type clksrc: str
    :param trigsrc: source of a digital trigger to start the generation
    :type trigsrc: str
    """
    def __init__(self, chan, samplerate, bufsize, clksrc="", trigsrc=""):
        Task.__init__(self)
        self.bufsize = bufsize
        self.CreateAOVoltageChan(chan,"",-10.0,10.0, 
            DAQmx_Val_Volts,None)
        self.CfgSampClkTiming(clksrc,samplerate, DAQmx_Val_Rising, 
                              DAQmx_Val_ContSamps, bufsize)
        #starts the AO and AI at the same time
        if len(trigsrc) > 0:
            self.CfgDigEdgeStartTrig(trigsrc, DAQmx_Val_Rising)
        self.AutoRegisterDoneEvent(0)

    def start(self):
        """Begins generation -- immediately if not using a trigger"""
        self.StartTask()

    def write(self, output):
        """ Write the data to be output to the device buffer

        :param output: data to output
        :type output: numpy.ndarray
        """
        w = c_int32()
        # print "output max", max(abs(output))
        self.WriteAnalogF64(self.bufsize, 0, 10.0, DAQmx_Val_GroupByChannel,
                            output, w, None);
    def stop(self):
        """Halt the Generation"""
        self.StopTask()
        self.ClearTask()

class AITaskFinite(Task):
    """Class for managing continuous analog input with NI devices
        
    :param chans: Analog Input channels to gather data from
    :type chans: list<str>
    :param samplerate: Sampling frequency (Hz) at which data points are collected
    :type samplerate: int
    :param npts: number of data point to gather per channel
    :type npts: int
    :param clksrc: source terminal for the sample clock, default is internal clock
    :type clksrc: str
    """
    def __init__(self, chan, samplerate, npts, clksrc="", trigsrc=u""):
        Task.__init__(self)
        self.CreateAIVoltageChan(chan,"",DAQmx_Val_Cfg_Default,
                                 -10.0, 10.0, DAQmx_Val_Volts, None)
        self.CfgSampClkTiming(clksrc, samplerate, DAQmx_Val_Rising, 
                              DAQmx_Val_FiniteSamps, npts)
        #self.AutoRegisterDoneEvent(0)
        self.npts = npts

        if len(trigsrc) > 0:
            self.CfgDigEdgeStartTrig(trigsrc, DAQmx_Val_Rising)

    def start(self):
        """Begin acquistition"""
        self.StartTask()

    def read(self):
        """ Read the data off of the device input buffer. Blocks with a timeout of 10 seconds
        
        :returns: numpy.ndarray -- the acquired data
        """
        r = c_int32()
        inbuffer = np.zeros(self.npts)
        self.ReadAnalogF64(self.npts, 10.0, DAQmx_Val_GroupByScanNumber, inbuffer,
                           self.npts,byref(r), None)
        self.WaitUntilTaskDone(10.0)
        return inbuffer

    def stop(self):
        """Halt the acquisition"""
        # attempts to stop task after already clear throw error
        try:
            self.StopTask()
            self.ClearTask()
        except DAQError:
            pass

class AOTaskFinite(Task):
    """Class for managing finite analog output with NI devices
    
    :param chans: Analog output channels to generate data on
    :type chans: list<str>
    :param samplerate: Sampling frequency (Hz) at which data points generated
    :type samplerate: int
    :param npts: number of data points to output
    :type npts: int
    :param clksrc: source terminal for the sample clock, default is internal clock
    :type clksrc: str
    :param trigsrc: source of a digital trigger to start the generation
    :type trigsrc: str
    """
    def __init__(self, chan, samplerate, npoints, clksrc=u"", trigsrc=u""):
        Task.__init__(self)
        self.npoints = npoints

        self.CreateAOVoltageChan(chan,u"",-10.0,10.0, DAQmx_Val_Volts, None)
        self.CfgSampClkTiming(clksrc,samplerate, DAQmx_Val_Rising, 
                              DAQmx_Val_FiniteSamps, npoints)
        if len(trigsrc) > 0:
            self.CfgDigEdgeStartTrig(trigsrc, DAQmx_Val_Rising)

    def start(self):
        """Begins generation -- immediately, if not using a trigger"""
        self.StartTask()

    def write(self,output):
        """ Write the data to be output to the device buffer
        
        :param output: data to output
        :type output: numpy.ndarray
        """
        w = c_int32()
        self.WriteAnalogF64(self.npoints, 0, 10.0, DAQmx_Val_GroupByChannel,
                            output, w, None);

    def wait(self):
        """returns after the generation finishes"""
        self.WaitUntilTaskDone(10.0)

    def stop(self):
        """Halt the Generation"""
        # attempts to stop task after already clear throw error
        try:
            self.StopTask()
            self.ClearTask()
        except DAQError:
            pass

class DigitalOutTask(Task):
    def __init__(self, chan, rate, npoints=1000, clksrc=''):
        Task.__init__(self)

        self.CreateDOChan(chan, "", DAQmx_Val_ChanForAllLines)

        if clksrc == '':
            devname = chan.split('/')[0]
            self.clock = CounterOutTask(devname+'/ctr0', rate, npoints)
            clksrc = '/'+devname+'/Ctr0InternalOutput'
        else:
            self.clock = None

        self.CfgSampClkTiming(clksrc, rate, DAQmx_Val_Rising, DAQmx_Val_ContSamps, 
                              npoints)
        w = c_int32()
        data = np.zeros(npoints, dtype=np.uint32)
        self.WriteDigitalU32(len(value), 0, DAQmx_Val_WaitInfinitely, 
                             DAQmx_Val_GroupByChannel, data, w, None)

    def start(self):
        self.StartTask()
        if self.clock:
            self.clock.StartTask()

    def stop(self):
        self.StopTask()
        self.ClearTask()
        if self.clock:
            self.clock.StopTask()
            self.clock.ClearTask()

    def generated(self):
        buf = c_uint64()
        self.GetWriteTotalSampPerChanGenerated(buf)
        return buf.value

class CounterOutTask(Task):
    def __init__(self, chan, rate, npoints=1000):
        Task.__init__(self)
        # chan e.g. 'Dev1/ctr0'
        self.CreateCOPulseChanFreq(chan, '', DAQmx_Val_Hz, DAQmx_Val_Low, 0., rate , 0.5)
        self.CfgImplicitTiming(DAQmx_Val_ContSamps, npoints)

    def start(self):
        self.StartTask()

    def stop(self):
        self.StopTask()
        self.ClearTask()

def get_ao_chans(dev):
    """Discover and return a list of the names of all analog output channels for the given device"""
    buf = create_string_buffer(256)
    buflen = c_uint32(sizeof(buf))
    DAQmxGetDevAOPhysicalChans(dev, buf, buflen)
    pybuf = buf.value
    chans = pybuf.decode(u'utf-8').split(u",")
    return chans  

def get_ai_chans(dev):
    """Discover and return a list of the names of all analog input channels for the given device"""
    buf = create_string_buffer(512)
    buflen = c_uint32(sizeof(buf))
    DAQmxGetDevAIPhysicalChans(dev, buf, buflen)
    pybuf = buf.value
    chans = pybuf.decode(u'utf-8').split(u",")
    return chans
