from PyDAQmx import Task
from PyDAQmx.DAQmxConstants import *
from PyDAQmx.DAQmxTypes import *
import numpy as np
import matplotlib.pyplot as plt

class AITask(Task):
    def __init__(self, chan, samplerate, npoints, clksrc=b""):
        Task.__init__(self)
        self.data = np.zeros(npoints)
        self.a = []
        self.ndata = 0
        self.npoints = npoints
        self.CreateAIVoltageChan(chan,b"",DAQmx_Val_Cfg_Default,
            -10.0,10.0,DAQmx_Val_Volts,None)
        self.CfgSampClkTiming(clksrc,samplerate, DAQmx_Val_Rising, 
                              DAQmx_Val_ContSamps,npoints)
        #self.AutoRegisterEveryNSamplesEvent(DAQmx_Val_Acquired_Into_Buffer,100,0)
        self.AutoRegisterDoneEvent(0)
    def start(self):
        self.StartTask()
    def register_callback(self, fun, npts):
        self.callback_fun = fun
        print('npts is : ' + str(npts))
        self.AutoRegisterEveryNSamplesEvent(DAQmx_Val_Acquired_Into_Buffer,npts,0,name="run_callback")
    def run_callback(self):
        self.callback_fun(self)
    """
    def EveryNCallback(self):
        r = c_int32()
        self.ReadAnalogF64(self.npoints,10.0,DAQmx_Val_GroupByScanNumber,self.data,
                           self.npoints,byref(r),None)
        #store data in a numpy array where columns are trace sweeps
        self.a.append(self.data.tolist())
        #print(self.aplot)
        if self.aplot:
            self.aplot.set_data(range(len(self.a)-100,len(self.a)),self.data)
            #print('x')
    """
    def stop(self):
        self.StopTask()
        self.ClearTask()
        self.alldata = np.array(self.a).transpose()
        
class AOTask(Task):
    def __init__(self, chan, samplerate, npoints, clksrc=b""):
        Task.__init__(self)
        self.npoints = npoints
        self.data = np.zeros(npoints)
        #create some data to ouput
        #for i in range(NPOINTS):
            #self.data[i] = 9.95*np.sin(i*2.0*np.pi/NPOINTS)
        self.CreateAOVoltageChan(chan,b"",-10.0,10.0, 
            DAQmx_Val_Volts,None)
        self.CfgSampClkTiming(clksrc,samplerate, DAQmx_Val_Rising, 
                              DAQmx_Val_ContSamps,npoints)
        #self.CfgDigEdgeStartTrig(b"ai/StartTrigger",DAQmx_Val_Rising)
        self.AutoRegisterDoneEvent(0)
    def start(self):
        self.StartTask()
    def write(self,output):
        w = c_int32()
        self.WriteAnalogF64(self.npoints,0,10.0,DAQmx_Val_GroupByChannel,output,
            w,None);
    def stop(self):
        self.StopTask()
        self.ClearTask()
    def DoneCallback(self,status):
        print("Status"+str(status))
        return 0
