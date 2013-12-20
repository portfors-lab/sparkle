import os
import importlib
import sys
import glob

from PyQt4 import QtGui, QtCore

class DynamicStack(QtGui.QStackedWidget):
    def __init__(self, parent=None):
        QtGui.QStackedWidget.__init__(self, parent)

        package_path = os.path.dirname(__file__)
        package_name = os.path.basename(package_path)
        print package_path, package_name

        # module_files = os.listdir(os.path.join(package_path,'widgets'))
        module_files = glob.glob('widgets'+os.sep+'[a-zA-Z]*.py')
        module_names = [os.path.splitext(x)[0] for x in module_files]

        module_paths = [x.replace(os.sep, '.') for x in module_names]
        modules = [__import__(x, fromlist=['ParameterWidget']) for x in module_paths]

        widgets = [getattr(x, 'ParameterWidget') for x in modules]
        for widget in widgets:
            self.addWidget(widget())

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)

    dstack = DynamicStack()
    dstack.show()
    sys.exit(app.exec_())
