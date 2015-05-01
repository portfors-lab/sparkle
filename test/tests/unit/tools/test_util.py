import os
import shutil

import numpy as np

from sparkle.tools.util import convert2native, create_unique_path, \
    increment_title, next_str_num

tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), u"tmp")

def setup():
    if not os.path.exists(tempfolder):
        os.mkdir(tempfolder)

def teardown():
    # os.rmdir(tempfolder)
    shutil.rmtree(tempfolder, ignore_errors=True)

def test_increment_title():
    title = 'ex_4_12-4-13_5'
    new_title = increment_title(title)
    print 'new_title', new_title
    assert new_title == 'ex_4_12-4-13_6'

def test_convert():
    np_array = np.ones((3,))
    converted_array = convert2native(np_array)
    assert converted_array == [1, 1, 1]

    mixed_list = [[1,2,3], np.zeros((3,3)), 4, np.int_(5), {'a':7, 'b':np.int_(8)}, (np.int_(8), 'dog')]
    mixed_expected = [[1,2,3], [[0,0,0],[0,0,0],[0,0,0]], 4, 5, {'a':7, 'b':8}, (8,'dog')]
    mixed_converted = convert2native(mixed_list)
    print 'mixed converted', mixed_converted
    for i in range(len(mixed_expected)):
        assert mixed_converted[i] == mixed_expected[i]

def test_next_str_num_existing():
    pattern = 'Mouse497_'
    items = ['Cat365', 'Mouse497_2', 'Mouse497_3']
    next_str = next_str_num(pattern, items)

    assert next_str == 'Mouse497_4'

def test_next_str_num_first():
    pattern = 'Mouse497_'
    items = ['Cat365', 'Dog_7']
    next_str = next_str_num(pattern, items)

    assert next_str == 'Mouse497_1'

def test_next_str_num_empty():
    pattern = 'Mouse497_'
    items = []
    next_str = next_str_num(pattern, items)

    assert next_str == 'Mouse497_1'

def test_next_str_num_numbers():
    pattern = 'Mouse497'
    items = ['Mouse4972', 'Mouse4973']
    next_str = next_str_num(pattern, items)

    assert next_str == 'Mouse4974'

def test_create_unique_path_no_existing():
    path = create_unique_path(os.path.join(tempfolder,'test_file'))
    assert path == os.path.join(tempfolder,'test_file0.hdf5')

def test_create_unique_path_with_existing():
    open(os.path.join(tempfolder,'test_file0.hdf5'), 'a').close()
    path = create_unique_path(os.path.join(tempfolder, 'test_file'))
    assert path == os.path.join(tempfolder,'test_file1.hdf5')
