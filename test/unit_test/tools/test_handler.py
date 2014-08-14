import sys
import logging
import re

from PyQt4 import QtCore, QtGui

from spikeylab.tools.uihandler import TextEditHandler

class TestUIHandler():
    def setUp(self):
        self.app = QtGui.QApplication([])

    def tearDown(self):
        QtGui.QApplication.closeAllWindows()
        QtGui.QApplication.processEvents()
        del self.app

    def test_info_message(self):        
        w = QtGui.QLineEdit()
        handler = TextEditHandler()
        handler.signal.message.connect(w.setText)

        record = logging.LogRecord('main', 10, __file__, 13, "Now I've got glass floors", [], None)
        handler.emit(record)

        assert w.text() == "Now I've got glass floors"

    def test_warning_message(self):
        w = QtGui.QPlainTextEdit()
        handler = TextEditHandler()
        handler.signal.message.connect(w.appendHtml)

        record = logging.LogRecord('main', 30, __file__, 13, "This is a warning", [], None)
        handler.emit(record)

        assert w.toPlainText() == 'This is a warning'

    def test_error_message(self):
        w = QtGui.QPlainTextEdit()
        handler = TextEditHandler()
        handler.signal.message.connect(w.appendHtml)

        try:
            5/0
        except:
            info = sys.exc_info()

        record = logging.LogRecord('main', 40, __file__, 13, "This is an error", [], info)
        handler.emit(record)

        match = re.match('.*This is an error.*', w.toPlainText())
        assert match is not None