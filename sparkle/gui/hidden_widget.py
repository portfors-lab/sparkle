from sparkle.QtWrapper import QtGui
from sparkle.resources.icons import arrowdown, arrowup


class WidgetHider(QtGui.QWidget):   
    """Takes a widget and places it into a collapsable container widget

    :param content: widget to form the hidable contents of this container
    :type content: :qtdoc:`QWidget`
    """
    def __init__(self, content, parent=None):
        super(WidgetHider, self).__init__(parent)

        self.title = QtGui.QLabel(content.windowTitle())
        self.hideIcon = arrowdown()
        self.showIcon = arrowup()
        self.hideBtn = QtGui.QPushButton('',self)
        self.hideBtn.setIcon(self.showIcon)
        self.hideBtn.setFlat(True)
        self.hideBtn.clicked.connect(self.hide)
        titlebarLayout = QtGui.QHBoxLayout()
        titlebarLayout.setSpacing(0)
        titlebarLayout.setContentsMargins(0,0,0,0)
        titlebarLayout.addWidget(self.title)
        titlebarLayout.addWidget(self.hideBtn)
        titlebarLayout.addStretch(1)

        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)

        layout.addLayout(titlebarLayout)
        layout.addWidget(content)

        self.content = content
        content.hide()
        self.setFixedHeight(30)

        self.setLayout(layout)

    def hide(self, event):
        """Toggles the visiblity of the content widget"""
        if self.content.isHidden():
            self.content.show()
            self.hideBtn.setIcon(self.hideIcon)
            self.setMaximumHeight(16777215)
        else:
            self.content.hide()
            self.hideBtn.setIcon(self.showIcon)
            self.setFixedHeight(30)
