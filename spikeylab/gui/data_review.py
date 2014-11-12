from spikeylab.gui.hdftree import H5TreeWidget
from spikeylab.data.dataobjects import AcquisitionData
from spikeylab.gui.stim.component_detail import ComponentsDetailWidget

from QtWrapper import QtCore, QtGui

class QDataReviewer(QtGui.QWidget):
    reviewDataSelected = QtCore.Signal(str, int, int)
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        layout = QtGui.QHBoxLayout(self)

        hsplitter = QtGui.QSplitter(QtCore.Qt.Horizontal)

        asplitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.datatree = H5TreeWidget()
        self.datatree.nodeChanged.connect(self.setCurrentData)
        asplitter.addWidget(self.datatree)

        self.attrtxt = QtGui.QPlainTextEdit()
        attrLayout = QtGui.QVBoxLayout()
        attrLayout.setContentsMargins(0,0,0,0)
        attrLayout.addWidget(QtGui.QLabel("Saved Attributes:"))
        attrLayout.addWidget(self.attrtxt)
        attrLayout.addWidget(QtGui.QLabel("Derived Attributes:"))
        self.derivedtxt = QtGui.QPlainTextEdit()
        attrLayout.addWidget(self.derivedtxt)

        holder = QtGui.QWidget()
        holder.setLayout(attrLayout)
        asplitter.addWidget(holder)
        hsplitter.addWidget(asplitter)

        traceSplitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        traceLayout = QtGui.QVBoxLayout()

        self.tracetable = QtGui.QTableWidget()
        headers = ['No. Components', 'Stim Type', 'Sample Rate (Hz)']
        self.tracetable.setColumnCount(len(headers))
        self.tracetable.setHorizontalHeaderLabels(headers)
        self.tracetable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tracetable.cellClicked.connect(self.setTraceData)

        self.prevButton = QtGui.QPushButton('<')
        self.nextButton = QtGui.QPushButton('>')
        self.prevButton.clicked.connect(self.prevRep)
        self.nextButton.clicked.connect(self.nextRep)
        self.prevButton.setEnabled(False)   
        self.nextButton.setEnabled(False)
        
        btnLayout = QtGui.QHBoxLayout()
        btnLayout.addWidget(self.prevButton)
        btnLayout.addWidget(self.nextButton)

        traceLayout.addWidget(self.tracetable)
        traceLayout.addLayout(btnLayout)
        holder_widget = QtGui.QWidget()
        holder_widget.setLayout(traceLayout)

        hsplitter.addWidget(holder_widget)
        layout.addWidget(hsplitter)

        self.current_rep_num = 0

    def setDataObject(self, data):
        self.datatree.clearTree()
        self.tracetable.clearContents()
        self.tracetable.setRowCount(0)
        self.attrtxt.clear()
        self.derivedtxt.clear()

        self.datafile = data
        # display contents as a tree
        self.datatree.addH5Handle(data.hdf5)
        self.datatree.expandItem(self.datatree.topLevelItem(0))

    def update(self):
        self.datatree.update(self.datafile.hdf5)

    def setCurrentData(self, widgetitem):
        path = makepath(widgetitem)
        info = self.datafile.get_info(path)

        # clear out old stuff
        setname = widgetitem.text(0)
        self.tracetable.setRowCount(0)
        self.derivedtxt.clear()
        self.attrtxt.clear()

        self.current_rep_num = 0
        
        for attr in info:
            if attr[0] != 'stim':
                self.attrtxt.appendPlainText(attr[0] + ' : ' + str(attr[1]))
            else:
                # use the datafile object to do json converstion of stim data
                stimuli = self.datafile.get_trace_info(path)

                self.tracetable.setRowCount(len(stimuli))
                for row, stim in enumerate(stimuli):
                    # print stim
                    comp_names = [comp['stim_type'] for comp in stim['components'] if comp['stim_type'].lower() != 'silence']
                    unique = set(comp_names)
                    if len(unique) == 0:
                        comp_type = 'None'
                    elif len(unique) == 1:
                        comp_type = list(unique)[0]
                    else:
                        comp_type = 'Multi'
                    item =  QtGui.QTableWidgetItem(str(len(comp_names)))
                    item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tracetable.setItem(row, 0, item)
                    item =  QtGui.QTableWidgetItem(comp_type)
                    item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tracetable.setItem(row, 1, item)
                    item =  QtGui.QTableWidgetItem(str(stim['samplerate_da']))
                    item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.tracetable.setItem(row, 2, item)
                self.current_test = stimuli
                self.current_path = path

        if path == '':
            return
        data_object = self.datafile.hdf5[path]
        if hasattr(data_object, 'shape'):
            # only data sets have a shape
            data_shape = data_object.shape
            self.derivedtxt.appendPlainText("Dataset dimensions : "+str(data_shape))
            
            if setname.startsWith('test') or setname.startsWith('signal') or setname == 'reference_tone':
                # input samplerate is stored in group attributes
                group_data = self.datafile.get_info('/'.join(path.split('/')[:-1]))
                fsout = dict(group_data)['samplerate_ad']
                self.derivedtxt.appendPlainText("Recording window duration : "+str(float(data_shape[-1])/fsout) + ' s')
            self.current_data_shape = data_shape
            

    def setTraceData(self, row, column, repnum=0):
        
        self.current_rep_num = repnum
        self.current_trace_num = row
        self._update_buttons()
        self.tracetable.selectRow(row)
        self.reviewDataSelected.emit(self.current_path, row, repnum)

    def nextRep(self):
        self.current_rep_num += 1
        if self.current_rep_num == self.current_data_shape[1]:
            self.setTraceData(self.current_trace_num+1,0)
        else:
            self._update_buttons()
            self.reviewDataSelected.emit(self.current_path, self.current_trace_num, self.current_rep_num)

    def prevRep(self):
        self.current_rep_num -= 1
        if self.current_rep_num == -1:
            self.setTraceData(self.current_trace_num-1, 0, self.current_data_shape[1]-1)
        else:
            self._update_buttons()
            self.reviewDataSelected.emit(self.current_path, self.current_trace_num, self.current_rep_num)

    def _update_buttons(self):
        # by keeping buttons correctly enabled we dont need to check current
        # rep is within data limits
        if self.current_rep_num > 0 or self.current_trace_num > 0:
            self.prevButton.setEnabled(True)
        else:
            self.prevButton.setEnabled(False)
        if self.current_data_shape[1] > self.current_rep_num + 1 or self.current_data_shape[0] > self.current_trace_num + 1:
            self.nextButton.setEnabled(True)
        else:
            self.nextButton.setEnabled(False)

def makepath(item):
    if item is None:
        return ''
    elif item.text(0).endsWith('.hdf5'):
        return ''
    else:
        return makepath(item.parent()) + '/' + str(item.text(0))

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    QtGui.qApp = app
    data = AcquisitionData('C:\\Users\\amy.boyle\\audiolab_data\\open_testing.hdf5', filemode='r')
    viewer = QDataReviewer()
    viewer.setDataObject(data)
    viewer.show()
    app.exec_()