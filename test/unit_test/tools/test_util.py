from spikeylab.tools.util import increment_title, convert2native

import numpy as np

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