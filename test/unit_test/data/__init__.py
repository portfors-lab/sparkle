import os

tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), u"tmp")

def setup_package():
    if not os.path.exists(tempfolder):
        os.mkdir(tempfolder)

def teardown_package():
    os.rmdir(tempfolder)