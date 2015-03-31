"""Sanity test to check different RAM limits for 32 or
64-bit python with numpy arrays with a size of a reasonable stimulus"""
import numpy as np

if __name__ == "__main__":

    for i in range(100, 50000, 100):
        print i
        thearrays = []
        for j in range (i):
            thearrays.append(np.ones(0.2*5e5))
    print 'DONE'
