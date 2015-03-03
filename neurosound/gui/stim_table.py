from QtWrapper import QtCore, QtGui
from neurosound.data.dataobjects import AcquisitionData

class StimTable(QtGui.QTableWidget):
    def __init__(self, data=None):
        super(StimTable, self).__init__()

        self.cellDoubleClicked.connect(self.expandTest)
        if data is not None:
            self.setData(data)

    def setData(self, data):
        # clear table first
        self.clear()

        datasets = data.all_datasets()
        self.setRowCount(len(datasets))
        self.setColumnCount(6)
        for iset, dset in enumerate(datasets):
            info = dict(data.get_info(dset.name))
            # print info
            self.setItem(iset, 0, QtGui.QTableWidgetItem(dset.name))
            self.setItem(iset, 1, QtGui.QTableWidgetItem(info.get('testtype', '')))
            self.setItem(iset, 2, QtGui.QTableWidgetItem(info.get('user_tag', '')))
            if len(dset.shape) < 2:
                ntraces = 1
                nreps = 1
            elif len(dset.shape) < 3:
                ntraces = 1
                nreps = dset.shape[0]
            else:
                ntraces = dset.shape[0]
                nreps = dset.shape[1]
            nsamples = dset.shape[-1]
            self.setItem(iset, 3, QtGui.QTableWidgetItem(str(ntraces)))
            self.setItem(iset, 4, QtGui.QTableWidgetItem(str(nreps)))
            self.setItem(iset, 5, QtGui.QTableWidgetItem(str(nsamples)))

        headers = ['dataset', 'test type', 'user tag', '# traces', '# reps', '# samples']
        self.setHorizontalHeaderLabels(headers)
        self.datasets = datasets
        self.data = data

    def expandTest(self, row, column):
        stimuli = self.data.get_trace_info(self.datasets[row].name)
        self.trace_table = QtGui.QTableWidget()
        self.trace_table.setRowCount(len(stimuli))
        self.trace_table.setColumnCount(10)
        for itrace, trace in enumerate(stimuli):
            col = 0
            headers = []
            for component in trace['components']:
              self.trace_table.setItem(itrace, col, QtGui.QTableWidgetItem(component.pop('stim_type')))
              col +=1
              headers.append('type')
              # manually curated entries?
              self.trace_table.setItem(itrace, col, QtGui.QTableWidgetItem(str(component.pop('start_s'))))
              col +=1
              headers.append('start')

              for attr, val in component.items():
                self.trace_table.setItem(itrace, col, QtGui.QTableWidgetItem(str(val)))
                col +=1
                headers.append(attr)

        self.trace_table.setHorizontalHeaderLabels(headers)
        self.trace_table.show()


if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    # data = AcquisitionData('/home/leeloo/testdata/20141119.hdf5', filemode='r')
    data = AcquisitionData('/home/leeloo/testdata/August 5 2010/August 5 2010.hdf5', filemode='r')
    table = StimTable()
    table.setData(data)
    table.show()
    app.exec_()
