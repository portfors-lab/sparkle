import logging
import traceback

from PyQt4 import QtCore

class LogSignal(QtCore.QObject):
    message = QtCore.pyqtSignal(str)

class TextEditHandler(logging.Handler):
    """Relay log message via a signal to connected widgets. Using a signal
    vs. setting the text here allows for logging messages from threads."""
    def __init__(self, widget=None):
        logging.Handler.__init__(self)
        self.signal = LogSignal()

    def emit(self, m):
        if m.levelno >= 40:
            if m.exc_info is not None:
                # print 'infos', traceback.format_exception(*m.exc_info)
                formatted_exc = ''.join(traceback.format_exception(*m.exc_info))
                formatted_msg =  m.msg +'<br>'.join(formatted_exc.split('\n'))
            else:
                formatted_msg =  m.msg
            colored_message = '<font color="Red">' + formatted_msg + '</font>'
        elif m.levelno >= 30:
            colored_message = '<font color="Orange">' + m.msg + '</font>'
        else:
            colored_message = m.msg

        self.signal.message.emit(colored_message)

    def set_widget(self, widget):
        self.widget = widget