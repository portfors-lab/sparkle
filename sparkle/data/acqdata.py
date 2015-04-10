import os

from sparkle.tools.exceptions import DataIndexError, DisallowedFilemodeError, \
    OverwriteFileError, ReadOnlyError
from sparkle.tools.util import convert2native, max_str_num

"""
This is an abstract class intended to serve mostly as an interface. It should be subclassed
to provide actual access to datafiles. Implementation will depend on the internal structure
of the data file.
"""

class AcquisitionData(object):
    """
    Provides convenient access to data file; 
    each data file should represent an experimental session.

    Data files may conatain any number of one of the three types of datasets: 

    1. Finite datasets, where the amount of data to be stored is known in advance
    2. Open-ended aquisition, where the size of the acqusition window is known, but the number of traces to acquire is not
    3. Continuous acquisition, this is a 'chart' function where data is acquired continuously without break until the user stops the operation
    
    Upon new file creation the following attributes are saved to the file: *date*, *user*, *computer name*
    
    Finite datasets create sets with automatic naming of the scheme test_#, where the number starts with 1 and increments for the whole file, regardless of the group it is under.

    :param filename: the name of the data file to open.
    :type filename: str
    :param user: name of user opening the file
    :type user: str
    :type filemode: str
    :param filemode: The mode in which to open this file. Allowed values are:

        * 'w-' : Write to new file, fails if file already exists
        * 'a' : Append to existing file
        * 'r' : Read only, no writing allowed
        Overwriting an exisiting file is not allowed, and will result in an error
    """
    def __init__(self, filename, user='unknown', filemode='w-'):
        if filemode not in ['w-', 'a', 'r']:
            raise DisallowedFilemodeError(filename, filemode)
        if filemode == 'w-' and os.path.isfile(filename):
            raise OverwriteFileError(filename)

        self.filename = filename
        self.filemode = filemode

        self.open_set_size = 32
        self.chunk_size = 2**24 # better to have a multiple of fs?
        self.needs_repack = False

        self.datasets = {}
        self.meta = {}


    def close(self):
        """Closes the datafile, only one reference to a file may be 
        open at one time.

        If there is no data in the file, it will delete itself"""
        raise NotImplementedError

    def init_group(self, key, mode='finite'):
        """Create a group hierarchy level

        :param key: The name of the group, may be nested e.g. 'topgroup/subgroub'
        :type key: str
        :param mode: The type of acquisition this group is for. Options are: 'finite', 'calibration', 'open', 'continuous'
        :type mode: str
        """
        raise NotImplementedError

    def init_data(self, key, dims=None, mode='finite', nested_name=None):
        """
        Initializes a new dataset

        :param key: The dataset or group name. If finite, this will create a group (if none exists), and will sequentially name datasets under this group test_#
        :type key: str
        :type dims: tuple
        :param dims: 
            Dimensions of dataset:
            
            * if mode == 'finite', this is the total size
            * if mode == 'open', this is the dimension of a single trace
            * if mode == 'continuous', this is ignored
            * if mode == 'calibration', this is the total size
        :param mode: The kind of acquisition taking place
        :type mode: str
        :param nested_name: If mode is calibration, then this will be the dataset name created under the group key. Ignored for other modes.
        :type nested_name: str
        """
        raise NotImplementedError

    def append(self, key, data, nested_name=None):
        """
        Inserts data sequentially to structure in repeated calls. 
        Depending on how the dataset was initialized:

        * If mode == 'finite': If *nested_name* is ``None``, data is appended to the current automatically incremented *test_#* dataset under the given group. Otherwise data is appended to the group *key*, dataset *nested_name*.
        * If mode == 'calibration': Must provide a *nested_name* for a dataset to append data to under group *key*
        * If mode == 'open': Appends chunk to dataset *key*
        * If mode == 'continuous': Appends to dataset *key* forever

        For 'Finite' and 'calibration' modes, an attempt to append past the 
        initialized dataset size will result in an error

        :param key: name of the dataset/group to append to
        :type key: str
        :param data: data to add to file
        :type data: numpy.ndarray
        :param nested_name: If mode is 'calibration' or 'finite', then this will be the dataset name created under the group key. Ignored for other modes.
        :type nested_name: str
        """
        raise NotImplementedError

    def insert(self, key, index, data):
        """
        Inserts data to index location. For 'finite' mode only. Does not 
        affect appending location marker. Will Overwrite existing data.

        :param key: Group name to insert to
        :type key: str
        :param index: location that the data should be inserted
        :type index: tuple
        :param data: data to add to file
        :type data: numpy.ndarray
        """
        raise NotImplementedError

    def get_data(self, key, index=None):
        """
        Returns data for key at specified index

        :param key: name of the dataset to retrieve, may be nested
        :type key: str
        :param index: slice of of the data to retrieve, ``None`` gets whole data set. Numpy style indexing.
        :type index: tuple
        """
        raise NotImplementedError

    def get_info(self, key, inherited=False):
        """Retrieves all saved attributes for the group or dataset. 

        :param key: The name of group or dataset to get info for
        :type key: str
        :param inherited: If data uses a heirachial structure, includes inherited attributes.
        :type inherited: bool
        :returns: dict -- named attibutes and values
        """
        raise NotImplementedError


    def get_calibration(self, key, reffreq):
        """Gets a saved calibration, in attenuation from a refernece frequency point

        :param key: THe name of the calibraiton to retrieve
        :type key: str
        :param reffreq: The frequency for which to set as zero, all other frequencies will then be in attenuation difference from this frequency
        :type reffreq: int
        :returns: (numpy.ndarray, numpy.ndarray) -- frequencies of the attenuation vector, attenuation values
        """
        raise NotImplementedError

    def calibration_list(self):
        """Lists the calibrations present in this file

        :returns: list<str> -- the keys for the calibration groups
        """
        raise NotImplementedError

    def delete_group(self, key):
        """Removes the group from the file, deleting all data under it

        :param key: Name of group to remove
        :type key: str
        """
        raise NotImplementedError

    def set_metadata(self, key, attrdict, signal=False):
        """Sets attributes for a dataset or group

        :param key: name of group or dataset
        :type key: str
        :param attrdict: A collection of name:value pairs to save as metadata
        :type attrdict: dict
        """
        raise NotImplementedError

    def append_trace_info(self, key, stim_data):
        """Sets the stimulus documentation for the given dataset/groupname. If key is for a finite group, sets for current test

        :param key: Group or dataset name
        :type key: str
        :param stim_data: JSON formatted data to append to a list
        :type stim_data: str
        """
        raise NotImplementedError

    def keys(self):
        """The high-level keys for this file. This may be the names of groups, and/or datasets.

        :returns: list<str> -- list of the keys
        """
        raise NotImplementedError

    def all_datasets(self):
        """Returns a list containing all datasets anywhere within file. Warning: this will get all
        the data in the file
        """
        raise NotImplementedError

    def dataset_names(self):
        """Returns a list of the name of every dataset in this file. Each name is a valid
        key for get_info and get_data
        """
        raise NotImplementedError

    def get_trace_stim(self, key):
        """Gets a list of the stimulus metadata for the given dataset *key*.

        :param key: The name of group or dataset to get stimulus info for
        :type key: str
        :returns: list<dict> -- each dict in the list holds the stimulus info
         for each trace in the test. Therefore, the list should have a length equal 
         to the number of traces in the given test.
        """
        raise NotImplementedError


def increment(index, dims, data_shape):
    """Increments a given index according to the shape of the data added

    :param index: Current index to be incremented
    :type index: list
    :param dims: Shape of the data that the index is being incremented by
    :type dims: tuple
    :param data_shape: Shape of the data structure being incremented, this is check that incrementing is correct
    :returns: list - the incremented index
    """

    # check dimensions of data match structure
    inc_to_match = data_shape[1:]
    for dim_a, dim_b in zip(inc_to_match, dims[-1*(len(inc_to_match)):]):
        if dim_a != dim_b:
            raise DataIndexError()

    # now we can safely discard all but the highest dimension
    inc_index = len(index) - len(data_shape)
    inc_amount = data_shape[0]
    # make the index and increment amount dimensions match
    index[inc_index] += inc_amount

    # finally check that we did not run over allowed dimension
    if index[inc_index] > dims[inc_index]:
        raise DataIndexError()

    while inc_index > 0 and index[inc_index] == dims[inc_index]:
        index[inc_index-1] +=1
        index[inc_index:] = [0]*len(index[inc_index:])
        inc_index -=1
    return index
