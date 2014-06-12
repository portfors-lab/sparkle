import numpy as np

DAQmx_Val_Rising = None
DAQmx_Val_Cfg_Default = None
DAQmx_Val_Volts = None
DAQmx_Val_ContSamps = None
DAQmx_Val_Acquired_Into_Buffer = None
DAQmx_Val_GroupByChannel = None
DAQmx_Val_FiniteSamps = None
DAQmx_Val_GroupByScanNumber = None

class Task(object):

	def CreateAIVoltageChan(self, chan, name, p0, minv, maxv, units, p1):
		pass

	def CreateAOVoltageChan(self, chan, name, minv, maxv, units, p1):
		pass

	def CfgSampClkTiming(self, clk, fs, edge, acq_mode, bufsize):
		pass

	def AutoRegisterDoneEvent(self, p0):
		pass

	def StartTask(self):
		pass

	def AutoRegisterEveryNSamplesEvent(self, p0, npts, p1, name):
		pass

	def ReadAnalogF64(self, npts, maxv, groupby, inbuffer, total_samples, datatype, p0):
		# populate contents of inbuffer with some fake data
		t = np.arange(npts)
		f = 5
		data = 2*np.sin(2*np.pi*f*t/len(t))
		inbuffer[:] = data		

	def StopTask(self):
		pass

	def ClearTask(self):
		pass

	def CfgDigEdgeStartTrig(self, trigsrc, edge):
		pass

	def WriteAnalogF64(self, npts, p0, maxv, grouby, output, datatype, p1):
		pass

	def WaitUntilTaskDone(self, timeout):
		pass	

def DAQmxGetDevAIPhysicalChans(dev, buf, buflen):
	fakechans = 'ai0,ai1,ai2,ai3'
	buf[0:len(fakechans)] = fakechans

def DAQmxGetDevAOPhysicalChans(dev, buf, buflen):
	fakechans = 'ao0,ao1,ao2,ao3'
	buf[0:len(fakechans)] = fakechans