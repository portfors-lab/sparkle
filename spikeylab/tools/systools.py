import sys, os

APPNAME = 'audiolab'

def get_appdir():
    if sys.platform == 'win32':
        appdir = os.path.join(os.environ['APPDATA'], APPNAME)
    else:
        appdir = os.path.expanduser(path.join("~", "." + APPNAME))

    return appdir