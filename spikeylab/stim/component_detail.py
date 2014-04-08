from PyQt4 import QtGui, QtCore

class ComponentDetailWidget(QtGui.QWidget):
    """class that presents the stimulus doc in a clear and useful way"""
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self)

        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)

        # keeps track of which attributes to display
        self.display_table = {}
        self.default_attributes = ['intensity', 'risefall']
        self.ignored_stim_types = ['silence']
        font = QtGui.QFont()
        font.setPointSize(12)
        self.setFont(font)

    def set_default_attributes(self, defaults):
        self.default_attributes = defaults

    def set_ignored(self, ignored):
        self.ignored_stim_types = ignored

    def set_doc(self, docs):
        font = QtGui.QFont()
        font.setPointSize(14)
        for doc in docs:
            stim_type = doc.pop('stim_type')
            if stim_type in self.ignored_stim_types:
                continue
            glay = QtGui.QGridLayout()
            # always at least include stimulus type
            title = QtGui.QLabel(stim_type)
            title.setFont(font)
            glay.addWidget(title,0,0)
            # get any other attributes to display, or defaults if not specified
            display_attributes = self.display_table.get(stim_type, self.default_attributes)
            for i, attr in enumerate(display_attributes):
                val = doc[attr]
                # add to UI
                glay.addWidget(QtGui.QLabel(attr),i+1,0)
                glay.addWidget(QtGui.QLabel(str(val)),i+1,1)
            self.layout.addLayout(glay)

    def clear_doc(self):
        clearLayout(self.layout)

def clearLayout(layout):
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                clearLayout(item.layout())