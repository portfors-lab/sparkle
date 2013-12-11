from spikeylab.tools.util import increment_title

def test_increment_title():
    title = 'ex_4_12-4-13_5'
    new_title = increment_title(title)
    print 'new_title', new_title
    assert new_title == 'ex_4_12-4-13_6'