import sys, os

APPNAME = 'audiolab'

def get_appdir():
    if sys.platform == 'win32':
        appdir = os.path.join(os.environ['APPDATA'], APPNAME)
    else:
        appdir = os.path.expanduser(os.path.join("~", "." + APPNAME))

    return appdir

def get_project_directory():
    return os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
