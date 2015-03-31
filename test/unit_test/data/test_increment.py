from nose.tools import raises

from sparkle.data.acqdata import increment
from sparkle.tools.exceptions import DataIndexError


def test_increment_index_by_1():
    dimensions = (2,3,4)
    data_shape = (1,)
    current_index = [0,0,1]

    current_index = increment(current_index, dimensions, data_shape)
    assert current_index == [0,0,2]

def test_increment_index_single_low_dimension():
    dimensions = (2,3,4)
    data_shape = (4,)
    current_index = [0,1,0]

    increment(current_index, dimensions, data_shape)
    assert current_index == [0,2,0]

def test_increment_index_double_low_dimension():
    dimensions = (2,3,4)
    data_shape = (1,4,)
    current_index = [0,0,0]

    current_index = increment(current_index, dimensions, data_shape)
    assert current_index == [0,1,0]

def test_increment_index_mid_dimension():
    dimensions = (2,3,4)
    data_shape = (2,4,)
    current_index = [0,0,0]

    current_index = increment(current_index, dimensions, data_shape)
    assert current_index == [0,2,0]

def test_increment_index_high_dimension():
    dimensions = (2,3,4)
    data_shape = (1,3,4,)
    current_index = [0,0,0]

    current_index = increment(current_index, dimensions, data_shape)
    assert current_index == [1,0,0]

def test_increment_double_boundary():
    dimensions = (2,2,3,4)
    data_shape = (4,)
    current_index = [0,1,2,0]

    current_index = increment(current_index, dimensions, data_shape)
    assert current_index == [1,0,0,0]

def test_increment_single_middle_dim():
    dimensions = (2,1,4)
    data_shape = (4,)
    current_index = [0,0,0]

    current_index = increment(current_index, dimensions, data_shape)
    assert current_index == [1,0,0]

@raises(DataIndexError)
def test_bad_data_shape():
    dimensions = (2,3,4)
    data_shape = (4,1)
    current_index = [0,0,0]

    current_index = increment(current_index, dimensions, data_shape)
