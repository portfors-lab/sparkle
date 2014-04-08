from PyQt4 import QtGui, QtCore

class ComponentDetailWidget(QtGui.QWidget):
    """class that presents the stimulus doc in a clear and useful way"""
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self)

        self.lyt = QtGui.QVBoxLayout()
        self.setLayout(self.lyt)

        # keeps track of which attributes to display
        self.display_table = {}
        self.default_attributes = ['intensity', 'risefall']
        font = QtGui.QFont()
        font.setPointSize(12)
        self.setFont(font)

    def set_display_table(self, table):
        self.display_table = table

    def set_default_attributes(self, defaults):
        self.default_attributes = defaults

    def set_doc(self, docs):
        font = QtGui.QFont()
        font.setPointSize(14)
        for doc in docs:
            stim_type = doc['stim_type']
            if not stim_type in self.display_table:
                continue
            if not stim_type in self.display_table[stim_type]:
                continue
            glay = QtGui.QGridLayout()
            # always at least include stimulus type
            title = QtGui.QLabel(stim_type)
            title.setFont(font)
            glay.addWidget(title,0,0)
            # get any other attributes to display, or defaults if not specified
            display_attributes = self.display_table.get(stim_type, self.default_attributes)
            for i, attr in enumerate(display_attributes):
                if attr == stim_type:
                    continue # already got it
                val = doc[attr]
                # add to UI
                glay.addWidget(QtGui.QLabel(attr),i+1,0)
                glay.addWidget(QtGui.QLabel(str(val)),i+1,1)
            self.lyt.addLayout(glay)

    def clear_doc(self):
        clearLayout(self.lyt)

def clearLayout(layout):
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                clearLayout(item.layout())

class ComponentDetailSelector(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self)

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

    def set_components(self, components):
        layout = self.layout()
        for comp in components:
            attr_widget = ComponentAttributerChecker(comp)
            layout.addWidget(attr_widget)

    def set_checked_details(self, checked):
        layout = self.layout()
        for i in range(layout.count()):
            w = layout.itemAt(i).widget()
            if w.stim_type in checked:
                w.set_checked(checked[w.stim_type])

    def get_checked_details(self):
        attrs = {}
        layout = self.layout()
        for i in range(layout.count()):
            w = layout.itemAt(i).widget()
            attrs[w.stim_type] = w.get_checked()
        return attrs

class ComponentAttributerChecker(QtGui.QWidget):
    def __init__(self, comp_attributes, parent=None):
        QtGui.QWidget.__init__(self)

        layout = QtGui.QGridLayout()

        font = QtGui.QFont()
        font.setBold(True)
        stim_type = comp_attributes.pop('stim_type')
        title = QtGui.QCheckBox(stim_type)
        title.setFont(font)
        layout.addWidget(title,0,0)

        for i, key in enumerate(comp_attributes):
            layout.addWidget(QtGui.QCheckBox(key),i+1,0)

        self.setLayout(layout)
        self.stim_type = stim_type

    def set_checked(self, tocheck):
        layout = self.layout()
        for i in range(layout.count()):
            w = layout.itemAt(i).widget()
            if w.text() in tocheck:
                w.setChecked(True)

    def get_checked(self):
        attrs = []
        layout = self.layout()
        for i in range(layout.count()):
            w = layout.itemAt(i).widget()
            if w.isChecked():
                attrs.append(w.text())
        return attrs