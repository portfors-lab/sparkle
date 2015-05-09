import time

import numpy as np

from sparkle.QtWrapper.QtGui import QApplication
from sparkle.gui.plotting.pyqtgraph_widgets import ChartWidget


def test_chart_speed():

    fs_range = range(10000, 100000, 10000) + range(100000, 500000, 25000)
    update_range = range(1, 10, 2) + range(10, 50, 10)# using this to determine point to plot at a time

    results = []

    for fs in fs_range:
        results.append([])
        for uprate in update_range:
            result = run_speed_test(fs, uprate)
            results[-1].append(result)
            print 'fs', fs, 'update rate', uprate, ':', result

        
def run_speed_test(fs, rate):
    fig = ChartWidget()
    fig.setWindowTitle('chart speed test')
    winsz = 1.0 #seconds
    fig.set_windowsize(winsz)
    fig.set_sr(fs)
    fig.show()

    npts = int(fs/rate) 

    last_time = time.time()
    for i in range(10):
        y = np.random.random(npts)
        fig.append_data(y,y)
        QApplication.processEvents()
        now = time.time()
        dt = now - last_time
        last_time = now
        if dt > 1/float(rate):
            # missed deadline, fail
            fig.close()
            return dt - (1/float(rate))

    fig.close()
    return True


if __name__ == '__main__':
    app = QApplication([])
    test_chart_speed()
    app.exit(0)
