import logging

class TextEditHandler(logging.Handler):
    def __init__(self, widget=None):
        logging.Handler.__init__(self)
        self.widget = widget

    def emit(self, m):
        if self.widget is not None:
            self.widget.appendPlainText(m.msg)

    def set_widget(self, widget):
        self.widget = widget