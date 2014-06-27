class DataIndexError(IndexError):
    pass

class FileDoesNotExistError(IOError):
    def __init__(self, fpath):
        self.fpath = fpath

    def __str__(self):
        return "Attempt to access invalid file path: {}".format(self.fpath)

class DisallowedFilemodeError(IOError):
    def __init__(self, fpath, mode):
        self.fpath = fpath
        self.mode = mode

    def __str__(self):
        return "Attempt to access file {}, with invalid filemode {}".format(self.fpath, self.mode)

class ReadOnlyError(IOError):
    def __init__(self, fpath):
        self.fpath = fpath

    def __str__(self):
        return "Attempt to write to read only file {}".format(self.fpath)

class OverwriteFileError(IOError):
    def __init__(self, fpath):
        self.fpath = fpath

    def __str__(self):
        return "Attempt to write over existing file {}".format(self.fpath)
