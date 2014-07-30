from PyQt4 import QtGui

class DynamicStackedWidget(QtGui.QStackedWidget):

    def widgetForName(self, name):
        for iwidget in range(len(self)):
            if self.widget(iwidget).name() == name:
                return self.widget(iwidget)

    def widgets(self):
        w = []
        for i in range(self.count()):
            w.append(self.widget(i))
        return w

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)

    dstack = DynamicStackedWidget()
    dstack.show()
    sys.exit(app.exec_())
