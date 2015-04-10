import test.sample as sample
from sparkle.data.batlabdata import BatlabData
from sparkle.data.hdf5data import HDF5Data
from sparkle.data.open import open_acqdata
import time

"""test using only AcquisitionData Interface"""

def test_read_data():

    filenames = [sample.batlabfile()+'.raw', sample.datafile()];

    for fname in filenames:
        dataobj = open_acqdata(fname, filemode='r')

        yield check_attributes, dataobj
        yield check_get_datasets, dataobj
        yield check_dataset_attributes, dataobj
        yield check_dataset_attributes_all, dataobj
        yield check_keys, dataobj
        yield check_get_data, dataobj

        dataobj.close()

def check_attributes(dataobj):
    attrs = dataobj.get_info('')
    assert 'date' in attrs
    assert 'who' in attrs
    assert 'computername' in attrs

def check_get_datasets(dataobj):
    datasets = dataobj.all_datasets()
    assert len(datasets) > 0
    # all datasets should have a name attribute
    for dset in datasets:
        assert dset.name is not None
        assert hasattr(dset, 'shape')

def check_dataset_attributes(dataobj):
    dataset_names = dataobj.dataset_names()
    assert len(dataset_names) > 0
    # we should be able to get info on any dataset by its name
    for name in dataset_names:
        info = dataobj.get_info(name)
        assert 'stim' in info
        # assert 'start' in info
        # print name, info.keys()

def check_dataset_attributes_all(dataobj):
    dataset_names = dataobj.dataset_names()
    assert len(dataset_names) > 0
    # we should be able to get info on any dataset by its name
    for name in dataset_names:
        info = dataobj.get_info(name, inherited=True)
        print info.keys()
        assert 'stim' in info
        assert 'samplerate_ad' in info
        # assert 'comment' in info
        # assert 'testtype' in info
        # assert 'user_tag' in info
        assert 'start' in info

def check_keys(dataobj):
    k = dataobj.keys()
    assert len(k) > 1

def check_get_data(dataobj):
    dataset_names = dataobj.dataset_names()
    assert len(dataset_names) > 0
    for dset in dataset_names:
        data = dataobj.get_data(dset)
        assert hasattr(data, 'shape')
