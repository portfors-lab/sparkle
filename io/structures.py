import numpy as np
import h5py
import datetime

class BigStore():
    def __init__(self, filename, chunksize=2**16):

        self.chunk_size = chunksize
        self.hdf5 = h5py.File(filename, 'w')
        self.counter = 0
        self.chunk_location = 0

        self.hdf5.create_dataset('set'+str(self.counter), (self.chunk_size,))

    def append(self,d):
        """
        Insert data list to end of data file
        """

        if self.chunk_location + len(d) <= self.chunk_size:
            self.hdf5['set'+str(self.counter)][self.chunk_location:self.chunk_location+len(d)] = d[:]
            self.chunk_location += len(d)
        else:
            nleft = self.chunk_size - self.chunk_location
            #print('nleft: ', nleft)
            if nleft > 0:
                self.hdf5['set'+str(self.counter)][self.chunk_location:] = d[:nleft]
            dtemp = d[nleft:]
            self.chunk_location = 0
            
            print('new data set')
            nslices = int(np.ceil(len(dtemp)/self.chunk_size))
            for islice in range(0,nslices):
                self.counter +=1
                self.hdf5.create_dataset('set'+str(self.counter), (self.chunk_size,))
                end = min(len(dtemp), self.chunk_size)
                self.hdf5['set'+str(self.counter)][:end] = dtemp[:end]
                dtemp = dtemp[end:]
            self.chunk_location = end

    def consolidate(self):
        """
        Concatenate all the datasets into a single stream
        """
        total_samples = (self.chunk_size * self.counter) + self.chunk_location
        master_set = self.hdf5.create_dataset('alldata', (total_samples,))

        for iset in range(self.counter-1):
            master_set[iset*self.chunk_size:(iset+1)*self.chunk_size] = self.hdf5['set'+str(iset)][:]

        # also add in the last set, which may not be a complete chunk
        master_set[self.counter*self.chunk_size:(self.counter*self.chunk_size)+self.chunk_location] = self.hdf5['set'+str(self.counter)][:self.chunk_location]

        # now go ahead and delete fractional sets.
        for iset in range(self.counter+1):
            del self.hdf5['set'+str(iset)]

    def shape(self):
        """
        Tuple of data size
        """
        if 'alldata' in self.hdf5:
            return self.hdf5['alldata'].shape
        else:
            return ((self.chunk_size * self.counter) + self.chunk_location,)

    def close(self):
        self.hdf5.close()

