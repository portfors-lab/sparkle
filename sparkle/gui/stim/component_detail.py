
from sparkle.QtWrapper import QtGui
from sparkle.tools.util import clearLayout


class ComponentsDetailWidget(QtGui.QWidget):
    """class that presents the stimulus doc in a clear and useful way"""
    def __init__(self, parent=None):
        super(ComponentsDetailWidget, self).__init__(parent)

        self.lyt = QtGui.QVBoxLayout()
        self.setLayout(self.lyt)

        # keeps track of which attributes to display
        self.displayTable = {}
        self.defaultAttributes = ['intensity', 'risefall']
        font = QtGui.QFont()
        font.setPointSize(12)
        self.setFont(font)

    def setDisplayTable(self, table):
        """Sets the table that determines what attributes to display

        :param table: keys of stimulus names, and values of a list of attribute names to display
        :type table: dict
        """
        self.displayTable = table

    def setDefaultAttributes(self, defaults):
        """Sets the default attributes to display, if a stimulus type is not in 
        the display table

        :param defaults: names of attributes to show
        :type defaults: list<str>
        """
        self.defaultAttributes = defaults

    def setDoc(self, docs):
        """Sets the documentation to display

        :param docs: a list of the stimuli doc, which are dicts
        :type docs: list<dict>
        """
        # sort stim by start time
        docs = sorted(docs, key=lambda k: k['start_s'])

        for doc in docs:
            stim_type = doc['stim_type']
            if not stim_type in self.displayTable:
                continue
            if not stim_type in self.displayTable[stim_type]:
                continue
            display_attributes = self.displayTable.get(stim_type, self.defaultAttributes)
            
            self.lyt.addWidget(ComponentDetailFrame(doc, display_attributes))

    def clearDoc(self):
        """Clears the widget"""
        clearLayout(self.lyt)

class ComponentDetailFrame(QtGui.QFrame):
    """Displays the given *displayAttributes* in a stimulus component's documentation *comp_doc*"""
    def __init__(self, comp_doc, displayAttributes):
        super(ComponentDetailFrame, self).__init__()

        self.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)
        font = QtGui.QFont()
        font.setPointSize(14)

        glay = QtGui.QGridLayout()
        stim_type = comp_doc['stim_type']

        # always at least include stimulus type
        title = QtGui.QLabel(stim_type)
        title.setFont(font)
        glay.addWidget(title,0,0)
        # get any other attributes to display, or defaults if not specified
        for i, attr in enumerate(displayAttributes):
            if attr == stim_type:
                continue # already got it
            val = comp_doc[attr]
            # add to UI
            glay.addWidget(QtGui.QLabel(attr),i+1,0)
            glay.addWidget(QtGui.QLabel(str(val)),i+1,1)
            
        self.setLayout(glay)

class ComponentsDetailSelector(QtGui.QWidget):
    """Container for ComponentAttributerCheckers"""
    def __init__(self, parent=None):
        super(ComponentsDetailSelector, self).__init__(parent)

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

    def setComponents(self, components):
        """Clears and sets the components contained in this widget

        :param components: list of documentation for subclasses of AbStractStimulusComponents
        :type Components: list<dict>
        """
        layout = self.layout()
        for comp in components:
            attrWidget = ComponentAttributerChecker(comp)
            layout.addWidget(attrWidget)

    def setCheckedDetails(self, checked):
        """Sets which components are checked

        :param checked: dictionary of stimtype:list<attribute names> for which components and their attributes should be checked
        :type checked: dict
        """
        layout = self.layout()
        for i in range(layout.count()):
            w = layout.itemAt(i).widget()
            if w.stimType in checked:
                w.setChecked(checked[w.stimType])

    def getCheckedDetails(self):
        """Gets the currently checked components and checked attributes

        :returns: dict -- of members with stimtype:list<attribute names>
        """
        attrs = {}
        layout = self.layout()
        for i in range(layout.count()):
            w = layout.itemAt(i).widget()
            attrs[w.stimType] = w.getChecked()
        return attrs

class ComponentAttributerChecker(QtGui.QFrame):
    """Allows a user to select attributes from a components's doc"""
    def __init__(self, compAttributes):
        super(ComponentAttributerChecker, self).__init__()

        self.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
        layout = QtGui.QGridLayout()

        font = QtGui.QFont()
        font.setBold(True)
        stimType = compAttributes.pop('stim_type')
        title = QtGui.QCheckBox(stimType)
        title.setFont(font)
        layout.addWidget(title,0,0)

        for i, key in enumerate(compAttributes):
            layout.addWidget(QtGui.QCheckBox(key),i+1,0)

        self.setLayout(layout)
        self.stimType = stimType


    def setChecked(self, tocheck):
        """Sets the attributes *tocheck* as checked

        :param tocheck: attributes names to check
        :type tocheck: list<str>
        """
        layout = self.layout()
        for i in range(layout.count()):
            w = layout.itemAt(i).widget()
            if w.text() in tocheck:
                w.setChecked(True)

    def getChecked(self):
        """Gets the checked attributes

        :returns: list<str> -- checked attribute names
        """
        attrs = []
        layout = self.layout()
        for i in range(layout.count()):
            w = layout.itemAt(i).widget()
            if w.isChecked():
                attrs.append(str(w.text()))
        return attrs
