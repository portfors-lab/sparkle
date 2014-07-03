import threading
import time

from PyQt4 import QtCore, QtGui, QtTest

from test.util import robot

def center(widget, index=None):
    """Get the global position of the center of the widget. If index is
    provided, widget is a view and get the center at the index position"""
    if index is not None:
        # widget is a subclass of QAbstractView
        rect = widget.visualRect(index)
        viewport = widget.viewport()
        midpoint = QtCore.QPoint(rect.x() + rect.width()/2, rect.y() + rect.height()/2)
        global_point = viewport.mapToGlobal(midpoint)
    else:
        if isinstance(widget, QtGui.QRadioButton):
            # we want the center of the hit region
            global_point = widget.mapToGlobal(QtCore.QPoint(10,10))
        else:
            midpoint = QtCore.QPoint(widget.width()/2, widget.height()/2)
            global_point = widget.mapToGlobal(midpoint)

    return global_point.x(), global_point.y()


def click(widget, index=None):
    pos = center(widget, index)
    robot.click(pos)

def doubleclick(widget, index=None):
    pos = center(widget, index)
    robot.doubleclick(pos)

def move(widget, index=None):
    pos = center(widget, index)
    robot.move(pos)

def wheel(ticks):
    # wrapper
    if ticks < 0:
        increment = -1
    else:
        increment = 1
    # neccessary to space out mouse wheel increments    
    for i in range(abs(ticks)):
        robot.wheel(increment)
        QtTest.QTest.qWait(100)

def keypress(key):
    robot.keypress(key)

def type(msg):
    robot.type(str(msg))

def drag(src, dest, src_index=None, dest_index=None):
    src_pos = center(src, src_index)
    dest_pos = center(dest, dest_index)
    thread = threading.Thread(target=robot.drag, args=(src_pos, dest_pos))
    thread.start()
    while thread.is_alive():
        QtTest.QTest.qWait(500)

def wait_for_dialog(cls=QtGui.QDialog):
    thread = threading.Thread(target=close_modal)
    thread.start()
    while thread.is_alive():
        QtTest.QTest.qWait(500)

def close_modal():
    modalWidget = None
    while modalWidget is None:
        modalWidget = QtGui.QApplication.activeModalWidget()
        time.sleep(1)
    # knowledge of CellCommentDialog Structure
    click(modalWidget.ui.okBtn)

def listen_for_file_dialog(fpath):
    thread = threading.Thread(target=accept_modal, args=(fpath,))
    thread.start()

def accept_modal(fpath=None):
    modalWidget = None
    while modalWidget is None:
        modalWidget = QtGui.QApplication.activeModalWidget()
        time.sleep(1)
    if fpath is not None:
        robot.type(fpath)
    robot.keypress('enter')

def reorder_view(view, start_idx, end_idx):
    start_pos = center(view, view.model().index(*start_idx))
    if end_idx[1] > 0:
        prev_idx = (end_idx[0], end_idx[1]-1)
        end_pos = center(view, view.model().index(*prev_idx))
        comp0len = view.visualRect(view.model().index(*prev_idx)).width()
        end_pos = (end_pos[0]+(comp0len/2)+15, end_pos[1])
    else:
        end_pos = 15, view.rowReach()*(0.5*end_idx[0])

    thread = threading.Thread(target=robot.drag, args=(start_pos, end_pos))
    thread.start()
    while thread.is_alive():
        QtTest.QTest.qWait(500)