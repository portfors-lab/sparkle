from __future__ import division
import time

import numpy as np
from pymouse import PyMouse
from pykeyboard import PyKeyboard

def mousedrag(source, dest, speed=1000):
    m = PyMouse()
    m.press(*source)

    time.sleep(0.1)

    npoints = int(np.sqrt((dest[0]-source[0])**2 + (dest[1]-source[1])**2 ) / (speed/1000))
    for i in range(npoints):
        x = int(source[0] + ((dest[0]-source[0])/npoints)*i)
        y = int(source[1] + ((dest[1]-source[1])/npoints)*i)
        m.move(x,y)
        time.sleep(0.001)

    m.release(*dest)

def click(point):
    m = PyMouse()
    m.move(*point)
    m.press(*point)
    m.release(*point)

def doubleclick(point):
    m = PyMouse()
    m.move(*point)
    time.sleep(0.1)
    m.press(*point)
    m.release(*point)
    m.press(*point)
    m.release(*point)

def move(point):
    """wrapper just so we don't have to import pymouse separately"""
    m = PyMouse()
    m.move(*point)

def keypress(key):
    k = PyKeyboard()
    if key == 'enter':
        key = k.return_key
    k.tap_key(key)

def type(string):
    k = PyKeyboard()
    k.type_string(string)