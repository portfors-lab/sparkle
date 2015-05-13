import logging
import os
import re
import sys

import yaml

from sparkle.QtWrapper import QtCore, QtGui
from sparkle import tools
from sparkle.tools.log import init_logging
from sparkle.tools.uihandler import TextEditHandler, assign_uihandler_slot


class TestUIHandler():

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

        
class MockLogWindow(object):
    def __init__(self):
        self.messages = [];

    def log_slot(self, msg):
        self.messages.append(msg)

def test_logging_config_uihandler():
    init_logging()
    win = MockLogWindow()

    logger = logging.getLogger('main')
    
    assign_uihandler_slot(logger, win.log_slot)

    logger.exception('an exception') 
    logger.warning('a warning')
    logger.info('some info')
    logger.debug('extra stuff')
    config_file = os.path.join(os.path.dirname(tools.__file__), 'logging.conf')
    with open(config_file, 'r') as yf:
        config = yaml.load(yf)
    print config

    level = config['handlers']['ui']['level']
    # assume we alway log error and warnings
    assert 'exception' in win.messages[0]
    assert 'color="Red"' in win.messages[0]
    assert 'warning' in win.messages[1]
    assert 'color="Orange"' in win.messages[1]

    if level in ['INFO', 'DEBUG']:
        assert 'info' in win.messages[2]
    if level == 'DEBUG':
        assert 'stuff' in win.messages[3]
