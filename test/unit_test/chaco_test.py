from audiolab.plotting.chacoplots import LiveWindow, ImageWindow, ImageWidget, ImagePlotter

import sys, os
import time, random
import numpy as np
import Image

from PyQt4.QtGui import QApplication

import audiolab.tools.audiotools as adt

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

def test_chaco_image():
    app = QApplication(sys.argv)
    # fig = ImageWidget()
    fig = ImagePlotter(None, 1)
    # fname = os.path.join(os.path.abspath(os.path.dirname(__file__)), "ducklings.jpg")
    # print fname
    # img = Image.open(fname)
    # print img.size
    # img = np.array(img.getdata(), np.uint8).reshape(img.size[1], img.size[0], 3)
    # # img = np.array(img)
    # print img.shape
    # print type(img)
    sylpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), "sample_syl.wav")
    spec, f, bins, fs = adt.spectrogram(sylpath)

    fig.update_data(spec)
    fig.widget.resize(600, 400)
    # fig.resize(600,400)
    fig.widget.show()

    QApplication.processEvents()
    time.sleep(3)