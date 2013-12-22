import os
import importlib
import sys
import glob
import inspect

from PyQt4 import QtGui, QtCore

from spikeylab.stim.abstract_parameters import AbstractParameterWidget


class DynamicStackedWidget(QtGui.QStackedWidget):

    def update_units(self, tscale, fscale):
        # bad!
        AbstractParameterWidget().setFScale(fscale)
        AbstractParameterWidget().setTScale(tscale)

    def widget_for_name(self, name):
        for iwidget in range(len(self)):
            if self.widget(iwidget).name() == name:
                return self.widget(iwidget)

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)

    dstack = DynamicStackedWidget()
    dstack.show()
    sys.exit(app.exec_())
