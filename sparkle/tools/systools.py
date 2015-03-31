import ctypes
import os
import platform
import random
import string
import sys

APPNAME = 'audiolab'

def get_appdir():
    if sys.platform == 'win32':
        appdir = os.path.join(os.environ['APPDATA'], APPNAME)
    else:
        appdir = os.path.expanduser(os.path.join("~", "." + APPNAME))

    return appdir

def get_project_directory():
    return os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def get_src_directory():
    return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

def get_free_mb(folder):
    """ Return folder/drive free space (in bytes)
    """
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value/1024/1024
    else:
        st = os.statvfs(folder)
        return st.f_bavail * st.f_frsize/1024/1024

def get_drives():
    if platform.system() == 'Windows':
        return ['C:\\', 'D:\\']
    else:
        return ['/home']

def rand_id():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for x in range(4))
