
class ProtocolTabelModel():
    def __init__(self, parent=None):
        self._tests = []
        self.caldb = None
        self.calv = None
        self.calibrationVector = None
        self.calibrationFrequencies = None
        self.calibrationFrange = None

    def setReferenceVoltage(self, caldb, calv):
        self.caldb = caldb
        self.calv = calv
        for test in self._tests:
            test.setReferenceVoltage(caldb, calv)

    def setCalibration(self, db_boost_array, frequencies, frange):
        self.calibrationVector = db_boost_array
        self.calibrationFrequencies = frequencies
        self.calibrationFrange = frange
        for test in self._tests:
            test.setCalibration(db_boost_array, frequencies, frange)
    
    def rowCount(self):
        return len(self._tests)

    def test(self, row):
        return self._tests[row]

    def allTests(self):
        return self._tests

    def remove(self, position):
        """Removes a test from the order list, but not keeps a reference"""
        return self._tests.pop(position)

    def insert(self, stim, position):
        """Creates inserts a new test into list"""
        if position == -1:
            position = self.rowCount()
        stim.setReferenceVoltage(self.caldb, self.calv)
        stim.setCalibration(self.calibrationVector, self.calibrationFrequencies, self.calibrationFrange)
        self._tests.insert(position, stim)
    
    def clear(self):
        self._tests = []

    def verify(self, windowSize=None):
        """Verify that this protocol model is valid. Return 0 if sucessful,
        a failure message otherwise"""
        if self.rowCount() == 0:
            return "Protocol must have at least one test"
        if self.caldb is None or self.calv is None:
            return "Protocol reference voltage not set"
        for test in self._tests:
            msg = test.verify(windowSize)
            if msg:
                return msg
        return 0
