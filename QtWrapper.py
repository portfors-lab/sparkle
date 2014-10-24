"""Adapted from https://gist.github.com/remram44/5985681

This compatibility layer allows to use either PySide or PyQt4 as the Qt
binding. """


import os
import sys

binding = 'PyQt4'

def set_sip_api():
    import sip
    api2_classes = [
            'QData', 'QDateTime', 'QString', 'QTextStream',
            'QTime', 'QUrl', 'QVariant',
            ]
    for cl in api2_classes:
        sip.setapi(cl, 2)

if binding == "PySide":
    from PySide import QtCore, QtGui, QtNetwork, QtSvg, QtTest
    sys.stderr.write("Using default binding %s\n" % binding)

elif binding == "PyQt4":
    # set_sip_api()
    from PyQt4 import QtCore, QtGui, QtNetwork, QtSvg, QtTest
    sys.stderr.write("Using default binding %s\n" % binding)

else:
    raise ImportError("Python binding not specified")

sys.modules[__name__ + '.QtCore'] = QtCore
sys.modules[__name__ + '.QtGui'] = QtGui
sys.modules[__name__ + '.QtNetwork'] = QtNetwork
sys.modules[__name__ + '.QtSvg'] = QtSvg
sys.modules[__name__ + '.QtTest'] = QtTest

if binding == "PySide":
    QtCore.QT_VERSION_STR = QtCore.__version__
    QtCore.QT_VERSION = tuple(int(c) for c in QtCore.__version__.split('.'))
    try:
        from PySide import QtOpenGL
        sys.modules[__name__ + '.QtOpenGL'] = QtOpenGL
    except ImportError:
        pass
    try:
        from PySide import QtWebKit
        sys.modules[__name__ + '.QtWebKit'] = QtWebKit
    except ImportError:
        pass

    # This will be passed on to new versions of matplotlib
    os.environ['QT_API'] = 'pyside'
    
    from datetime import datetime as datetime_, timedelta

    @staticmethod
    def qWait(t):
        end = datetime_.now() + timedelta(milliseconds=t)
        while datetime_.now() < end:
            QtGui.QApplication.processEvents()
    QtTest.QTest.qWait = qWait

    def QtLoadUI(uifile, base):
        from PySide import QtUiTools
        loader = QtUiTools.QUiLoader()
        uif = QtCore.QFile(uifile)
        uif.open(QtCore.QFile.ReadOnly)
        result = loader.load(uif, base)
        uif.close()
        return result

elif binding == 'PyQt4':    
    try:
        from PyQt4 import QtOpenGL
        sys.modules[__name__ + '.QtOpenGL'] = QtOpenGL
    except ImportError:
        pass
    try:
        from PyQt4 import QtWebKit
        sys.modules[__name__ + '.QtWebKit'] = QtWebKit
    except ImportError:
        pass

    QtCore.Signal = QtCore.pyqtSignal
    QtCore.Slot = QtCore.pyqtSlot
    QtCore.Property = QtCore.pyqtProperty
    os.environ['QT_API'] = 'pyqt'
    def QtLoadUI(uifile, base):
        from PyQt4 import uic
        return uic.loadUi(uifile, base)

def get_qt_binding_name():
    return binding


__all__ = ['QtCore', 'QtGui', 'QtLoadUI', 'get_qt_binding_name']
