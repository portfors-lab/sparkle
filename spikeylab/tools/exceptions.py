class DataIndexError(IndexError):
    pass

class FileDoesNotExistError(IOError):
    def __init__(self, fpath):
        self.fpath = fpath

    def __str__(self):
        return "Attempt to access invalid file path: {}".format(self.fpath)