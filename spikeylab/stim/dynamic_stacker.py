import os
import importlib
import sys
import glob
import inspect

from PyQt4 import QtGui, QtCore

from spikeylab.stim.abstract_parameters import AbstractParameterWidget


class DynamicStackedWidget(QtGui.QStackedWidget):
    def __init__(self, parent=None):
        QtGui.QStackedWidget.__init__(self, parent)

        package_path = os.path.dirname(__file__)
        # package_name = os.path.basename(package_path)
        # print package_path, package_name

        mod = '.'.join(self.__module__.split('.')[:-1])
        if len(mod) > 0:
            mod =  mod + '.'

        widget_folder = os.path.join(package_path, 'widgets')

        module_files = glob.glob(widget_folder+os.sep+'[a-zA-Z]*.py')
        # print 'modules files', module_files
        module_names = [os.path.splitext(os.path.basename(x))[0] for x in module_files]

        # module_paths = [x.replace(os.sep, '.') for x in module_names]
        module_paths = [mod+'widgets.'+x for x in module_names]
        modules = [__import__(x, fromlist=['ParameterWidget']) for x in module_paths]

        widgets = []
        names = []
        for module in modules:
            try:
                w = getattr(module, 'ParameterWidget')
                if w.include_in_stack:
                    widgets.append(w)
                    names.append(w.name)
            except AttributeError:
                pass
        self.names = names

        for widget in widgets:
            self.addWidget(widget())

    def update_units(self, tscale, fscale):
        # bad!
        AbstractParameterWidget().setFScale(fscale)
        AbstractParameterWidget().setTScale(tscale)

    def widget_for_name(self, name):
        index = self.names.index(name)
        return self.widget(index)

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)

    dstack = DynamicStackedWidget()
    dstack.show()
    sys.exit(app.exec_())
