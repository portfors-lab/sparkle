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
                formatted_exc = ''.join(traceback.format_exception(*m.exc_info))
                # convert to HTML format
                formatted_msg =  m.msg + formatted_exc.replace('\n', '<br>')
            else:
                formatted_msg =  m.msg
            formatted_msg =  formatted_msg.replace(' ', '&nbsp;')
            colored_message = '<font color="Red">' + formatted_msg + '</font>'
        elif m.levelno >= 30:
            colored_message = '<font color="Orange">' + m.msg + '</font>'
        else:
            colored_message = m.msg

        self.signal.message.emit(colored_message)

    def set_widget(self, widget):
        self.widget = widget