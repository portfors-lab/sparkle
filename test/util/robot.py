from __future__ import division
import time

from numpy import sqrt
from pymouse import PyMouse
from pykeyboard import PyKeyboard

def drag(source, dest, speed=1000):
    """
    Simulates a smooth mouse drag

    :param source: location (x,y) to start the drag, in screen coordinates
    :type source: (int, int)
    :param dest: location (x,y) to end the drag, in screen coordinates
    :type dest: (int, int)
    :param speed: rate at which to execute the drag, in pixels/second
    :type speed: int
    """
    m = PyMouse()
    m.press(*source)

    time.sleep(0.1)

    npoints = int(sqrt((dest[0]-source[0])**2 + (dest[1]-source[1])**2 ) / (speed/1000))
    for i in range(npoints):
        x = int(source[0] + ((dest[0]-source[0])/npoints)*i)
        y = int(source[1] + ((dest[1]-source[1])/npoints)*i)
        m.move(x,y)
        time.sleep(0.001)

    m.release(*dest)

def click(point):
    """
    Simulates a mouse click

    :param point: location (x,y) of the screen to click
    :type point: (int, int)
    """
    m = PyMouse()
    m.move(*point)
    m.press(*point)
    m.release(*point)

def doubleclick(point):
    """
    Simulates a mouse double click

    :param point: location (x,y) of the screen to click
    :type point: (int, int)
    """
    m = PyMouse()
    m.press(*point)
    m.release(*point)
    m.press(*point)
    m.release(*point)

def move(point):
    """
    Moves the mouse cursor to the provided location

    :param point: location (x,y) of the screen to place the cursor
    :type point: (int, int)
    """
    # wrapper just so we don't have to import pymouse separately
    m = PyMouse()
    m.move(*point)

def keypress(key):
    """
    Simulates a key press

    :param key: the key [a-zA-Z0-9] to enter. Use 'enter' for the return key
    :type key: str
    """
    k = PyKeyboard()
    if key == 'enter':
        key = k.return_key
    k.tap_key(key)

def type(string):
    """
    Stimulates typing a string of characters
    
    :param string: A string of characters to enter
    :type string: str
    """
    k = PyKeyboard()
    k.type_string(string)

def wheel(ticks):
    """
    Simulates a mouse wheel movement

    :param ticks: number of increments to scroll the whell
    :type ticks: int
    """
    m = PyMouse()
    m.scroll(ticks)