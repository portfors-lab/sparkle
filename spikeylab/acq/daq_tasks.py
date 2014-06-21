#from PyDAQmx import Task
#from PyDAQmx.DAQmxConstants import *
#from PyDAQmx.DAQmxTypes import *
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
    def __init__(self, chans, samplerate, bufsize, clksrc=u""):
        Task.__init__(self)
        if isinstance(chans, basestring):
            chan_str = chans
            self.nchans = 1
        else:
            chan_str = ','.join(chans)
            self.nchans = len(chans)
        self.CreateAIVoltageChan(chan_str,u"",DAQmx_Val_Cfg_Default,
            -10.0,10.0,DAQmx_Val_Volts,None)
        self.CfgSampClkTiming(clksrc,samplerate, DAQmx_Val_Rising, 
                              DAQmx_Val_ContSamps,bufsize)
        #self.AutoRegisterEveryNSamplesEvent(DAQmx_Val_Acquired_Into_Buffer,100,0)
        self.AutoRegisterDoneEvent(0)
    def start(self):
        self.StartTask()
    def register_callback(self, fun, npts):
        self.callback_fun = fun
        self.n = npts
        self.AutoRegisterEveryNSamplesEvent(DAQmx_Val_Acquired_Into_Buffer,
                                            npts,0,name=u"run_callback")
    def run_callback(self):
        self.callback_fun(self)
    def read(self):
        r = c_int32()
        inbuffer = np.zeros(self.n*self.nchans)
        self.ReadAnalogF64(self.n,10.0,DAQmx_Val_GroupByChannel,
                            inbuffer, self.n*self.nchans, byref(r), None)
        data = inbuffer.reshape(self.nchans, self.n)
        return data
    def DoneCallback(self,status):
        print u"Status"+unicode(status)
        return 0
    def stop(self):
        try:
            self.StopTask()
            self.ClearTask()
        except DAQError:
            pass

class AOTask(Task):
    def __init__(self, chan, samplerate, npoints, clksrc="", trigsrc=""):
        Task.__init__(self)
        self.npoints = npoints
        self.CreateAOVoltageChan(chan,"",-10.0,10.0, 
            DAQmx_Val_Volts,None)
        self.CfgSampClkTiming(clksrc,samplerate, DAQmx_Val_Rising, 
                              DAQmx_Val_ContSamps,npoints)
        #starts the AO and AI at the same time
        if len(trigsrc) > 0:
            self.CfgDigEdgeStartTrig(trigsrc,DAQmx_Val_Rising)
        self.AutoRegisterDoneEvent(0)
    def start(self):
        self.StartTask()
    def write(self,output):
        w = c_int32()
        # print "output max", max(abs(output))
        self.WriteAnalogF64(self.npoints,0,10.0,DAQmx_Val_GroupByChannel,
                            output,w,None);
    def stop(self):
        self.StopTask()
        self.ClearTask()
    def DoneCallback(self,status):
        print u"Status"+unicode(status)
        return 0

class AITaskFinite(Task):
    def __init__(self, chan, samplerate, npts, clksrc=""):
        Task.__init__(self)
        self.CreateAIVoltageChan(chan,"",DAQmx_Val_Cfg_Default,
                                 -10.0,10.0,DAQmx_Val_Volts,None)
        self.CfgSampClkTiming(clksrc,samplerate, DAQmx_Val_Rising, 
                              DAQmx_Val_FiniteSamps,npts)
        #self.AutoRegisterDoneEvent(0)
        self.npts = npts
    def start(self):
        self.StartTask()
    def read(self):
        r = c_int32()
        inbuffer = np.zeros(self.npts)
        self.ReadAnalogF64(self.npts,10.0,DAQmx_Val_GroupByScanNumber,inbuffer,
                      self.npts,byref(r),None)
        self.WaitUntilTaskDone(10.0)
        return inbuffer
    def stop(self):
        # attempts to stop task after already clear throw error
        try:
            self.StopTask()
            self.ClearTask()
        except DAQError:
            pass

class AOTaskFinite(Task):
    def __init__(self, chan, samplerate, npoints, clksrc=u"", trigsrc=u""):
        Task.__init__(self)
        self.npoints = npoints

        self.CreateAOVoltageChan(chan,u"",-10.0,10.0, DAQmx_Val_Volts, None)
        self.CfgSampClkTiming(clksrc,samplerate, DAQmx_Val_Rising, 
                              DAQmx_Val_FiniteSamps, npoints)
        if len(trigsrc) > 0:
            self.CfgDigEdgeStartTrig(trigsrc,DAQmx_Val_Rising)
    def start(self):
        self.StartTask()
    def write(self,output):
        output, atten_level = scale_output(output)
        w = c_int32()
        self.WriteAnalogF64(self.npoints, 0, 10.0, DAQmx_Val_GroupByChannel,
                            output, w, None);
    def wait(self):
        self.WaitUntilTaskDone(10.0)
    def stop(self):
        # attempts to stop task after already clear throw error
        try:
            self.StopTask()
            self.ClearTask()
        except DAQError:
            pass

def scale_output(output):
    # scale the desired output to be above the device minimum,
    # and also return necessary attenuation factor
    return output, 0

def get_ao_chans(dev):
    buf = create_string_buffer(256)
    buflen = c_uint32(sizeof(buf))
    DAQmxGetDevAOPhysicalChans(dev, buf, buflen)
    pybuf = buf.value
    chans = pybuf.decode(u'utf-8').split(u",")
    return chans  

def get_ai_chans(dev):
    buf = create_string_buffer(512)
    buflen = c_uint32(sizeof(buf))
    DAQmxGetDevAIPhysicalChans(dev, buf, buflen)
    pybuf = buf.value
    chans = pybuf.decode(u'utf-8').split(u",")
    return chans
