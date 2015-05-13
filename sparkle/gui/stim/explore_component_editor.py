from sparkle.QtWrapper import QtCore, QtGui
from sparkle.gui.stim.abstract_editor import AbstractEditorWidget
from sparkle.gui.stim.dynamic_stacker import DynamicStackedWidget
from sparkle.gui.stim.smart_spinbox import SmartSpinBox


class ExploreComponentEditor(AbstractEditorWidget):
    """Editor for individual track in the explore stimulus model"""
    closePlease = QtCore.Signal(object)
    def __init__(self, parent=None):
        super(ExploreComponentEditor, self).__init__(parent)

        headerLayout  = QtGui.QHBoxLayout()
        self.exploreStimTypeCmbbx = QtGui.QComboBox()
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True) 
        self.exploreStimTypeCmbbx.setFont(font)
        self.closeBtn = QtGui.QPushButton('x')
        self.closeBtn.setFixedSize(25,25)
        self.closeBtn.setFlat(True)
        self.closeBtn.clicked.connect(self.closeRequest) 
        headerLayout.addWidget(self.exploreStimTypeCmbbx)
        headerLayout.addWidget(self.closeBtn)

        self.componentStack = DynamicStackedWidget()
        self.exploreStimTypeCmbbx.currentIndexChanged.connect(self.componentStack.setCurrentIndex)

        self.delaySpnbx = SmartSpinBox()
        self.delaySpnbx.setKeyboardTracking(False)
        self.delaySpnbx.setScale(self._scales[0])
        self.delaySpnbx.valueChanged.connect(self.valueChanged.emit)
        self.tunit_fields.append(self.delaySpnbx)

        delayLayout = QtGui.QHBoxLayout()
        delayLayout.addWidget(QtGui.QLabel("Delay"))
        delayLayout.addWidget(self.delaySpnbx)

        separator = QtGui.QFrame()
        separator.setFrameStyle(QtGui.QFrame.HLine)

        layout = QtGui.QVBoxLayout()
        layout.addLayout(headerLayout)
        layout.addWidget(self.componentStack)
        layout.addWidget(separator)
        layout.addLayout(delayLayout)

        self.setLayout(layout)

        self.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Sunken)
        self.setLineWidth(2)

        for m in ['widgets', 'widgetForName']:
            setattr(self, m, getattr(self.componentStack, m))

    def addWidget(self, widget, name):
        """Add a component editor widget"""
        self.exploreStimTypeCmbbx.addItem(name)
        self.componentStack.addWidget(widget)
        widget.valueChanged.connect(self.valueChanged.emit)

    def currentWidget(self):
        stimIndex = self.exploreStimTypeCmbbx.currentIndex()
        componentWidget = self.componentStack.widget(stimIndex)
        return componentWidget

    def currentIndex(self):
        return self.exploreStimTypeCmbbx.currentIndex()

    def delay(self):
        return self.delaySpnbx.value()

    def saveTemplate(self):
        """Get a json structure of the current inputs, 
        to be able to load later"""
        savedict = {}
        for comp_editor in self.widgets():
            stim = comp_editor.component()
            comp_editor.saveToObject()
            savedict[stim.name] = stim.stateDict()
        savedict['delay'] = self.delaySpnbx.value()
        return savedict

    def loadTemplate(self, template):
        for comp_editor in self.widgets():
            stim = comp_editor.component()
            if stim.name in template:
                stim.loadState(template[stim.name])
            # re-assign component to editor, so GUI fields are updated
            comp_editor.setComponent(stim)
        delay = template.get('delay', 0)
        self.delaySpnbx.setValue(delay)

    def closeRequest(self):
        self.closePlease.emit(self)
