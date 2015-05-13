import copy

from sparkle.QtWrapper import QtCore, QtGui


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

    def update(self):
        # lazy way, just clear and reload
        self.setData(self.data)

    def expandTest(self, row, column):
        stimuli = self.data.get_trace_stim(self.datasets[row].name)
        self.trace_table = QtGui.QTableWidget()
        self.trace_table.setRowCount(len(stimuli))
        if len(stimuli) == 1:
            first = 0
        elif len(stimuli[0]['components']) == 1 and stimuli[0]['components'][0]['stim_type'] == 'silence':
            first = 1
        else:
            first = 0
        
        headers = []
        # components will all be the same for each trace
        stim = copy.deepcopy(stimuli[first]['components'])
        for comp in stim:
            comp.pop('stim_type')
            comp.pop('start_s')
            headers.append('type')
            headers.append('start')
            for param in comp.keys():
                headers.append(param)

        self.trace_table.setColumnCount(len(headers))
        self.trace_table.setHorizontalHeaderLabels(headers)
        for itrace, trace in enumerate(stimuli):
            col = 0
            for component in trace['components']:
                self.trace_table.setItem(itrace, col, QtGui.QTableWidgetItem(component.pop('stim_type')))
                col +=1
                # manually curated entries?
                self.trace_table.setItem(itrace, col, QtGui.QTableWidgetItem(str(component.pop('start_s'))))
                col +=1

                for attr, val in component.items():
                    self.trace_table.setItem(itrace, col, QtGui.QTableWidgetItem(str(val)))
                    col +=1

        self.trace_table.show()


if __name__ == '__main__':
    import sys
    from sparkle.data.open import open_acqdata
    from test import sample

    app = QtGui.QApplication(sys.argv)
    # data = open_acqdata(sample.batlabfile(), filemode='r')
    data = open_acqdata(sample.datafile(), filemode='r')
    table = StimTable()
    table.setData(data)
    table.show()
    app.exec_()
