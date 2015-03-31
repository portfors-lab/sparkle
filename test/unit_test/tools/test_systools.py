import os

import sparkle.tools.systools as systools


def test_project_dir_valid():
    path = systools.get_project_directory()
    assert os.path.isdir(path)

def test_src_dir_valid():
    path = systools.get_src_directory()
    assert os.path.isdir(path)

def test_appdir_valid():
    path = systools.get_appdir()
    assert os.path.isdir(os.path.dirname(path))
