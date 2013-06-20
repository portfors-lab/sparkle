import numpy as np

class DataTraces():
    def __init__(self, arr, index, reps=True):
        
        # if this data structure will be holding repetitions,
        # assume second to last dimension are reps, i.e. does
        # not need labelled index
        self.data = {}
        self.index = index

    def add_dataset(self, label, init_array, index=None, reps=False,):
        # add data to the next place in the array
        self.data[label] = init_array
        self.rep[label] = reps

    def append(self, label, trace):
        self.data[label].append(trace)

    def insert(self, trace, loc):
        # insert data into data array at index, replacing
        # any current data at that index
        if len(loc) != len(self.index.shape):
            raise Exception("Incorrect number of indicies for DataTraces.insert()")

            self.data[loc] = trace

    def get(self, loc):
        # return, but do not remove, data at index
