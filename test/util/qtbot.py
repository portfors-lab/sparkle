import threading
import time

from PyQt4 import QtCore, QtGui, QtTest

from test.util import robot

def center(widget, view_index=None):
    """
    Gets the global position of the center of the widget. If index is
    provided, widget is a view and get the center at the index position

    :param widget: widget to get the center location of
    :type widget: PyQt4.QtGui.QWidget
    :param view_index: index of the item in the widget to get the center location of
    :type view_index: PyQt4.QtCore.QModelIndex
    :returns: (int, int) -- the (x,y) location in screen coordinates
    """
    if view_index is not None:
        # widget is a subclass of QAbstractView
        rect = widget.visualRect(view_index)
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


def click(widget, view_index=None):
    """
    Simulates a click at the center of the widget

    :param view_index: If not None, assumes the given widget is a view, clicks the center of the indexed item in the view
    """
    pos = center(widget, view_index)
    robot.click(pos)

def doubleclick(widget, view_index=None):
    """
    Simulates a double click at the center of the widget

    :param view_index: If not None, assumes the given widget is a view, clicks the center of the indexed item in the view
    """
    pos = center(widget, view_index)
    robot.doubleclick(pos)

def move(widget, view_index=None):
    """
    Simulates a click at the center of the widget

    :param view_index: If not None, assumes the given widget is a view, clicks the center of the indexed item in the view
    """
    pos = center(widget, view_index)
    robot.move(pos)

def wheel(ticks):
    """
    Simulates a mouse wheel movement

    :param ticks: number of increments to scroll the whell
    :type ticks: int
    """
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
    """
    Simulates a key press

    :param key: the key [a-zA-Z0-9] to enter. Use 'enter' for the return key
    :type key: str
    """
    robot.keypress(key)

def type(msg):
    """
    Stimulates typing a string of characters
    
    :param string: A string of characters to enter
    :type string: str
    """
    robot.type(str(msg))

def drag(src, dest, src_index=None, dest_index=None):
    """
    Simulates a smooth mouse drag from one widget to another

    :param src: source widget
    :type src: PyQt4.QtGui.QWidget
    :param dest: widget to drag to
    :type dest: PyQt4.QtGui.QWidget
    :param src_index: If not None, assumes src widget is a view, drags from this item at index location 
    :type src_index: PyQt4.QtCore.QModelIndex
    :param dest_index: If not None, assumes dest widget is a view, drags to this item at index location
    :type dest_index: PyQt4.QtCore.QModelIndex
    """
    src_pos = center(src, src_index)
    dest_pos = center(dest, dest_index)
    thread = threading.Thread(target=robot.drag, args=(src_pos, dest_pos))
    thread.start()
    while thread.is_alive():
        QtTest.QTest.qWait(500)

def wait_for_dialog(cls=QtGui.QDialog):
    """
    Listens for a modal dialog, and closes it
    """
    thread = threading.Thread(target=close_modal)
    thread.start()
    while thread.is_alive():
        QtTest.QTest.qWait(500)

def close_modal():
    """
    Endlessly waits for a modal widget, clicks ok button when found
    """
    modalWidget = None
    while modalWidget is None:
        modalWidget = QtGui.QApplication.activeModalWidget()
        time.sleep(1)
    # knowledge of CellCommentDialog Structure
    click(modalWidget.ui.okBtn)

def close_dialog():
    """
    Endlessly waits for a QDialog widget, presses enter when found
    """
    dialogs = []
    while len(dialogs) == 0:
        topWidgets = QtGui.QApplication.topLevelWidgets()
        dialogs = [w for w in topWidgets if isinstance(w, QtGui.QDialog)]
        time.sleep(1)
    robot.keypress('enter')

def listen_for_file_dialog(fpath):
    """
    Listens for a modal widget, and accepts when found

    :param fpath: string to type in the default focus location of widget
    :type fpath: str
    """
    thread = threading.Thread(target=accept_modal, args=(fpath,))
    thread.start()

def accept_modal(fpath=None):
    """
    Endlessly waits for a modal widget, types given filepath and presses enter when found
    
    :param fpath: string to type in the default focus location of widget
    :type fpath: str
    """
    modalWidget = None
    while modalWidget is None:
        modalWidget = QtGui.QApplication.activeModalWidget()
        time.sleep(1)
    if fpath is not None:
        robot.type(fpath)
    robot.keypress('enter')

def reorder_view(view, start_idx, end_idx):
    """
    Simulates a smooth mouse drag from one widget to another

    :param view: Widget where the dragging will take place
    :type view: PyQt4.QtGui.QAbstractItemView
    :param start_idx: index of item in view to start drag from
    :type start_idx: PyQt4.QtCore.QModelIndex
    :param end_idx: index of item in view to drag to
    :type end_idx: PyQt4.QtCore.QModelIndex
    """
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
    # block return until drag is finished
    while thread.is_alive():
        QtTest.QTest.qWait(500)