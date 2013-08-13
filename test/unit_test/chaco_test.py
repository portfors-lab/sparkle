from audiolab.plotting.chacoplots import LiveWindow

import sys
import time, random
import numpy as np

from PyQt4.QtGui import QApplication

def test_chaco_plot():
    app = QApplication(sys.argv)
    fig = LiveWindow(2)
    fig.resize(600, 400)
    fig.show()

    x = np.arange(200)

    for i in range(10):
        y = np.sin(random.randint(0,10) * x)
        fig.draw_line(np.mod(i,2),0,x,y)
        QApplication.processEvents()
        time.sleep(0.5)

    fig.close()