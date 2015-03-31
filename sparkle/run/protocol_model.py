import copy


class ProtocolTabelModel():
    def __init__(self, parent=None):
        self._tests = []
        self.caldb = None
        self.calv = None
        self.calibrationVector = None
        self.calibrationFrequencies = None
        self.calibrationFrange = None

    def setReferenceVoltage(self, caldb, calv):
        """See :meth:`StimulusModel<sparkle.stim.stimulus_model.StimulusModel.setReferenceVoltage>`"""
        self.caldb = caldb
        self.calv = calv
        for test in self._tests:
            test.setReferenceVoltage(caldb, calv)

    def setCalibration(self, db_boost_array, frequencies, frange):
        """Sets calibration for all tests

        See :meth:`StimulusModel<sparkle.stim.stimulus_model.StimulusModel.setCalibration>`"""
        self.calibrationVector = db_boost_array
        self.calibrationFrequencies = frequencies
        self.calibrationFrange = frange
        for test in self._tests:
            test.setCalibration(db_boost_array, frequencies, frange)
    
    def rowCount(self):
        """The number of tests in this protocol

        :returns: int -- test count
        """
        return len(self._tests)

    def test(self, row):
        """Gets a test by index

        :param row: index number of test
        :type row: int
        :returns: :class:`StimulusModel<sparkle.stim.stimulus_model.StimulusModel>`
        """
        return self._tests[row]

    def allTests(self):
        """Gets all tests

        :returns: list<:class:`StimulusModel<sparkle.stim.stimulus_model.StimulusModel>`>
        """
        return copy.deepcopy(self._tests)

    def remove(self, position):
        """Removes the test at position from the protocol

        :param position: index of stimulus to remove
        :type position: int
        """
        return self._tests.pop(position)

    def insert(self, stim, position):
        """Inserts a new stimulus into the list at the given position

        :param stim: stimulus to insert into protocol
        :type stim: :class:`StimulusModel<sparkle.stim.stimulus_model.StimulusModel>`
        :param position: index (row) of location to insert to
        :type position: int
        """
        if position == -1:
            position = self.rowCount()
        stim.setReferenceVoltage(self.caldb, self.calv)
        stim.setCalibration(self.calibrationVector, self.calibrationFrequencies, self.calibrationFrange)
        self._tests.insert(position, stim)
    
    def clear(self):
        """Clears all tests from protocol"""
        self._tests = []

    def verify(self, windowSize=None):
        """Verify that this protocol model is valid. Return 0 if sucessful,
        a failure message otherwise

        :param windowSize: acquistion window size (seconds), to check against duration, check is not performed is None provided
        :type windowSize: float
        :returns: 0 (int) for success, fail message (str) otherwise
        """
        if self.rowCount() == 0:
            return "Protocol must have at least one test"
        if self.caldb is None or self.calv is None:
            return "Protocol reference voltage not set"
        for test in self._tests:
            msg = test.verify(windowSize)
            if msg:
                return msg
        return 0
