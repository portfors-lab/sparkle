from PyDAQmx import Task
from PyDAQmx.DAQmxConstants import *
from PyDAQmx.DAQmxTypes import *
import numpy as np
import matplotlib.pyplot as plt

class AITask(Task):
    def __init__(self, chan, samplerate, bufsize, clksrc=b""):
        Task.__init__(self)
        self.CreateAIVoltageChan(chan,b"",DAQmx_Val_Cfg_Default,
            -10.0,10.0,DAQmx_Val_Volts,None)
        self.CfgSampClkTiming(clksrc,samplerate, DAQmx_Val_Rising, 
                              DAQmx_Val_ContSamps,bufsize)
        #self.AutoRegisterEveryNSamplesEvent(DAQmx_Val_Acquired_Into_Buffer,100,0)
        self.AutoRegisterDoneEvent(0)
    def start(self):
        self.StartTask()
    def register_callback(self, fun, npts):
        self.callback_fun = fun
        self.AutoRegisterEveryNSamplesEvent(DAQmx_Val_Acquired_Into_Buffer,
                                            npts,0,name="run_callback")
    def run_callback(self):
        self.callback_fun(self)
    def DoneCallback(self,status):
        print("Status"+str(status))
        return 0
    def stop(self):
        self.StopTask()
        self.ClearTask()
        
class AOTask(Task):
    def __init__(self, chan, samplerate, npoints, clksrc=b"", trigsrc=b""):
        Task.__init__(self)
        self.npoints = npoints
        self.CreateAOVoltageChan(chan,b"",-10.0,10.0, 
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
        self.WriteAnalogF64(self.npoints,0,10.0,DAQmx_Val_GroupByChannel,
                            output,
            w,None);
    def stop(self):
        self.StopTask()
        self.ClearTask()
    def DoneCallback(self,status):
        print("Status"+str(status))
        return 0

class AITaskFinite(Task):
    def __init__(self, chan, samplerate, npts, clksrc=b""):
        Task.__init__(self)
        self.CreateAIVoltageChan(chan,b"",DAQmx_Val_Cfg_Default,
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
        self.StopTask()
        self.ClearTask()

class AOTaskFinite(Task):
    def __init__(self, chan, samplerate, npoints, clksrc=b"", trigsrc=b""):
        Task.__init__(self)
        self.npoints = npoints
        #self.data = np.zeros(npoints)
        self.CreateAOVoltageChan(chan,b"",-10.0,10.0, DAQmx_Val_Volts,None)
        self.CfgSampClkTiming(clksrc,samplerate, DAQmx_Val_Rising, 
                              DAQmx_Val_FiniteSamps,npoints)
        if len(trigsrc) > 0:
            self.CfgDigEdgeStartTrig(trigsrc,DAQmx_Val_Rising)
        #starts the AO and AI at the same time
        #self.CfgDigEdgeStartTrig(b"ai/StartTrigger",DAQmx_Val_Rising)
    def start(self):
        self.StartTask()
    def write(self,output):
        w = c_int32()
        self.WriteAnalogF64(self.npoints,0,10.0,DAQmx_Val_GroupByChannel,output,
            w,None);
    def stop(self):
        self.StopTask()
        self.ClearTask()