from PyQt4 import QtCore, QtGui

def center(item, parent=None):
    """Overloaded function, takes a widget or a QRect and returns
    the center as a QPoint"""
    if isinstance(item, QtGui.QWidget):
        midpoint = QtCore.QPoint(item.width()/2, item.height()/2)
        global_point = item.mapToGlobal(midpoint)
    elif isinstance(item, QtCore.QRect):
        midpoint = QtCore.QPoint(item.x() + item.width()/2, item.y() + item.height()/2)
        if parent is not None:
            global_point = parent.mapToGlobal(midpoint)
        else:
            global_point =  midpoint
    return global_point.x(), global_point.y()

def hotspot(radio):
    """Return a clickable coordinate for radio button"""
    pt = radio.mapToGlobal(QtCore.QPoint(10,10))
    return pt.x(), pt.y()