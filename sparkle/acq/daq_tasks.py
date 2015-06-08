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
    :param bufsize: length (in samples) of the data buffer to allocate for each channel
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
        """Begins acquistition"""
        self.StartTask()

    def register_callback(self, fun, npts):
        """ Provide a function to be executed periodically on 
        data collection, every time after the specified number 
        of points are collected.
        
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
        """Halts the acquisition"""
        try:
            self.StopTask()
            self.ClearTask()
        except DAQError:
            pass

class AOTask(Task):
    """Class for managing continuous analog output with NI devices
    
    :param chans: Analog output channels to generate data on
    :type chans: list<str>
    :param samplerate: Sampling frequency (Hz) at which data points are generated
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
        """Writes the data to be output to the device buffer, output will be looped when the data runs out

        :param output: data to output
        :type output: numpy.ndarray
        """
        w = c_int32()
        # print "output max", max(abs(output))
        self.WriteAnalogF64(self.bufsize, 0, 10.0, DAQmx_Val_GroupByChannel,
                            output, w, None);
    def stop(self):
        """Halts the Generation"""
        self.StopTask()
        self.ClearTask()

class AITaskFinite(Task):
    """Class for managing finite duration analog input with NI devices
        
    :param chans: Analog Input channels to gather data from
    :type chans: list<str>
    :param samplerate: Sampling frequency (Hz) at which data points are collected
    :type samplerate: int
    :param npts: number of data point to gather per channel
    :type npts: int
    :param clksrc: source terminal for the sample clock, default is internal clock
    :type clksrc: str
    :param trigsrc: source of a digital trigger to start the generation, default : no trigger, begin immediately on call of start method
    :type trigsrc: str
    """
    def __init__(self, chan, samplerate, npts, clksrc="", trigsrc=None):
        Task.__init__(self)
        if isinstance(chan, list):
            self.nchans = len(chan)
            chan = ','.join(chan)
        else:
            self.nchans = 1
        self.CreateAIVoltageChan(chan,"",DAQmx_Val_Cfg_Default,
                                 -10.0, 10.0, DAQmx_Val_Volts, None)
        self.CfgSampClkTiming(clksrc, samplerate, DAQmx_Val_Rising, 
                              DAQmx_Val_FiniteSamps, npts)
        #self.AutoRegisterDoneEvent(0)
        self.npts = npts

        if trigsrc:
            self.CfgDigEdgeStartTrig(trigsrc, DAQmx_Val_Rising)

    def start(self):
        """Begins acquistition -- immediately if not using a trigger"""
        self.StartTask()

    def read(self):
        """Reads the data off of the device input buffer. Blocks for acquisition to finish with a timeout of 10 seconds
        
        :returns: numpy.ndarray -- the acquired data
        """
        r = c_int32()
        bufsize = self.npts*self.nchans
        inbuffer = np.zeros(bufsize)
        self.ReadAnalogF64(self.npts, 10.0, DAQmx_Val_GroupByChannel, inbuffer,
                           bufsize, byref(r), None)
        self.WaitUntilTaskDone(10.0)


        return inbuffer.reshape(self.nchans, self.npts)

    def stop(self):
        """Halts the acquisition"""
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
    :param samplerate: Sampling frequency (Hz) at which data points are generated
    :type samplerate: int
    :param npts: number of data points to output
    :type npts: int
    :param clksrc: source terminal for the sample clock, default is internal clock
    :type clksrc: str
    :param trigsrc: source of a digital trigger to start the generation
    :type trigsrc: str
    """
    def __init__(self, chan, samplerate, npoints, clksrc=u"", trigsrc=None):
        Task.__init__(self)
        self.npoints = npoints

        self.CreateAOVoltageChan(chan,u"",-10.0,10.0, DAQmx_Val_Volts, None)
        self.CfgSampClkTiming(clksrc,samplerate, DAQmx_Val_Rising, 
                              DAQmx_Val_FiniteSamps, npoints)
        if trigsrc:
            self.CfgDigEdgeStartTrig(trigsrc, DAQmx_Val_Rising)

    def start(self):
        """Begins generation -- immediately, if not using a trigger"""
        self.StartTask()

    def write(self,output):
        """Writes the data to be output to the device buffer
        
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
        """Halts the Generation"""
        # attempts to stop task after already clear throw error
        try:
            self.StopTask()
            self.ClearTask()
        except DAQError:
            pass

class DigitalOutTask(Task):
    """Task to Generate Digital output on a port, generates a square pulse

    :param chan: Digital port to ouput to
    :type chan: str
    :param rate: frequency of the pulses to generate
    :type rate: int
    :param npoints: number of pulses to generate
    :type nponts: int
    :param clksrc: source terminal for the sample clock, default is internal clock -- generated using counter channel
    :type clksrc: str
    """
    def __init__(self, chan, rate, npoints=100, clksrc=''):
        Task.__init__(self)
        # necessary to get the rising edge at the correct frequency
        rate = rate*2

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

        data = np.array([0,1], dtype=np.uint8)
        self.WriteDigitalLines(len(data), False, DAQmx_Val_WaitInfinitely, DAQmx_Val_GroupByChannel, data, w, None)

    def start(self):
        """Begins generation"""
        self.StartTask()
        if self.clock:
            self.clock.StartTask()

    def stop(self):
        """Halts generation"""
        self.StopTask()
        self.ClearTask()
        if self.clock:
            self.clock.StopTask()
            self.clock.ClearTask()

    def generated(self):
        """Reports the number of digital output pulses generated"""
        buf = c_uint64()
        self.GetWriteTotalSampPerChanGenerated(buf)
        return buf.value

class CounterOutTask(Task):
    """Task to create a pulse train internall on the device, 
    for the purpose of syncing operations

    :param chan: counter channel to use
    :type chan: str
    :param rate: frequency (Hz) to generate the pulse train at
    :type rate: int
    :param npoints: number of points to generate for the pulse train
    :type npoints: int
    """
    def __init__(self, chan, rate, npoints=100):
        Task.__init__(self)
        # chan e.g. 'Dev1/ctr0'
        self.CreateCOPulseChanFreq(chan, '', DAQmx_Val_Hz, DAQmx_Val_Low, 0., rate , 0.5)
        self.CfgImplicitTiming(DAQmx_Val_ContSamps, npoints)

    def start(self):
        """Begins the pulse train generation"""
        self.StartTask()

    def stop(self):
        """Halts the pulse train generation"""
        self.StopTask()
        self.ClearTask()

def get_ao_chans(dev):
    """Discover and return a list of the names of all analog output channels for the given device

    :param dev: the device name
    :type dev: str
    """
    buf = create_string_buffer(256)
    buflen = c_uint32(sizeof(buf))
    DAQmxGetDevAOPhysicalChans(dev.encode(), buf, buflen)
    pybuf = buf.value
    chans = pybuf.decode(u'utf-8').split(u",")
    return chans  

def get_ai_chans(dev):
    """Discover and return a list of the names of all analog input channels for the given device
    
    :param dev: the device name
    :type dev: str
    """
    buf = create_string_buffer(512)
    buflen = c_uint32(sizeof(buf))
    DAQmxGetDevAIPhysicalChans(dev.encode(), buf, buflen)
    pybuf = buf.value
    chans = pybuf.decode(u'utf-8').split(u", ")
    return chans

def get_devices():
    """Discover and return a list of the names of all NI devices on this system"""
    buf = create_string_buffer(512)
    buflen = c_uint32(sizeof(buf))
    DAQmxGetSysDevNames(buf, buflen)
    pybuf = buf.value
    devices = pybuf.decode(u'utf-8').split(u",")
    return devices
