from sparkle.QtWrapper import QtGui


class DynamicStackedWidget(QtGui.QStackedWidget):
    """Adds a couple methods for getting child widgets to 
    a :qtdoc:QStackedWidget"""
    def widgetForName(self, name):
        """Gets a widget with *name*

        :param name: the widgets in this container should all have
         a name() method. This is the string to match to that result
        :type name: str
        """
        for iwidget in range(len(self)):
            if self.widget(iwidget).name() == name:
                return self.widget(iwidget)

    def widgets(self):
        """Gets all (first) child wigets"""
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
