from sparkle.QtWrapper import QtCore, QtGui
from sparkle.gui.datatree import DataTree
from sparkle.gui.stim.component_detail import ComponentsDetailWidget
from sparkle.gui.stim_table import StimTable

INTERVAL = 200 #ms

class QDataReviewer(QtGui.QWidget):
    reviewDataSelected = QtCore.Signal(str, int, int)
    testSelected = QtCore.Signal(str)
    def __init__(self, parent=None):
        super(QDataReviewer, self).__init__(parent)

        layout = QtGui.QHBoxLayout(self)

        hsplitter = QtGui.QSplitter(QtCore.Qt.Horizontal)

        asplitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        contents_view = QtGui.QWidget()
        content_view_layout = QtGui.QVBoxLayout()
        self.btngrp = QtGui.QButtonGroup()
        choice_layout = QtGui.QHBoxLayout()
        tree_radio = QtGui.QRadioButton("File tree")
        table_radio = QtGui.QRadioButton("Test table")
        tree_radio.setChecked(True)
        self.btngrp.addButton(tree_radio)
        self.btngrp.addButton(table_radio)
        self.btngrp.setId(tree_radio, 0)
        self.btngrp.setId(table_radio, 1)
        choice_layout.addWidget(tree_radio)
        choice_layout.addWidget(table_radio)
        content_view_layout.addLayout(choice_layout)
        contents_stack = QtGui.QStackedWidget()
        self.datatree = DataTree()
        self.datatable = StimTable()
        contents_stack.addWidget(self.datatree)
        contents_stack.addWidget(self.datatable)
        self.btngrp.buttonClicked[int].connect(contents_stack.setCurrentIndex)
        content_view_layout.addWidget(contents_stack)
        contents_view.setLayout(content_view_layout)

        self.datatree.nodeChanged.connect(self.setCurrentNode)
        self.datatable.currentCellChanged.connect(self.setCurrentCell)
        asplitter.addWidget(contents_view)

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

        self.tracetable = TraceTable()
        headers = ['No. Components', 'Stim Type', 'Sample Rate (Hz)']
        self.tracetable.setColumnCount(len(headers))
        self.tracetable.setHorizontalHeaderLabels(headers)
        self.tracetable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tracetable.cellClicked.connect(self.setTraceData)
        self.tracetable.currentCellChanged.connect(self.traceChanged)
        self.tracetable.left.connect(self.prevRep)
        self.tracetable.right.connect(self.nextRep)

        self.prevButton = QtGui.QPushButton('<')
        self.nextButton = QtGui.QPushButton('>')
        self.firstButton = QtGui.QPushButton('|<')
        self.lastButton = QtGui.QPushButton('>|')
        self.prevButton.clicked.connect(self.prevRep)
        self.nextButton.clicked.connect(self.nextRep)
        self.firstButton.clicked.connect(self.firstRep)
        self.lastButton.clicked.connect(self.lastRep)
        self.prevButton.setEnabled(False)   
        self.nextButton.setEnabled(False)
        self.firstButton.setEnabled(False)
        self.lastButton.setEnabled(False)
        self.prevButton.setToolTip("previous presentation")
        self.nextButton.setToolTip("next presentation")
        self.firstButton.setToolTip("start of trace")
        self.lastButton.setToolTip("end of trace")
        
        self.playTraceButton = QtGui.QPushButton("play")
        self.playTraceButton.clicked.connect(self.playTrace)
        self.playTestButton = QtGui.QPushButton("play all")
        self.playTestButton.clicked.connect(self.playTest)
        self.playTraceButton.setToolTip("play current trace")
        self.playTestButton.setToolTip("play test")

        self.overlayButton = QtGui.QPushButton("overlay")
        self.overlayButton.clicked.connect(self.overlayTrace)
        self.overlayButton.setToolTip('Overlap all reps in trace')

        btnLayout = QtGui.QGridLayout()
        btnLayout.addWidget(self.prevButton, 0, 0)
        btnLayout.addWidget(self.firstButton, 0, 1)
        btnLayout.addWidget(self.lastButton, 0, 2)
        btnLayout.addWidget(self.nextButton, 0, 3)
        btnLayout.addWidget(self.playTraceButton, 1, 0)
        btnLayout.addWidget(self.playTestButton, 1, 1)
        btnLayout.addWidget(self.overlayButton, 1, 2)

        traceLayout.addWidget(self.tracetable)
        traceLayout.addLayout(btnLayout)
        holder_widget = QtGui.QWidget()
        holder_widget.setLayout(traceLayout)

        hsplitter.addWidget(holder_widget)
        layout.addWidget(hsplitter)

        self.current_rep_num = 0
        self.current_trace_num = None
        self.current_path = None
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.nextRep)
        self.traceStop = False

    def setDataObject(self, data):
        self.datatree.clearTree()
        self.tracetable.clearContents()
        self.tracetable.setRowCount(0)
        self.attrtxt.clear()
        self.derivedtxt.clear()

        self.datafile = data
        # display contents as a tree
        self.datatree.addData(data)
        # and a table
        self.datatable.setData(data)

    def update(self):
        self.datatree.update()
        self.datatable.update()

    def setCurrentCell(self, row, column, prevrow=None, prevcol=None):
        # don't care about the column clicked, get the path for the row
        if row != -1:
            path = str(self.datatable.item(row, 0).text())
            self.setCurrentData(path)

    def setCurrentNode(self, path):
        self.setCurrentData(str(path))
        
    def setCurrentData(self, path):
        setname = path.split('/')[-1]
        info = self.datafile.get_info(path)

        # clear out old stuff
        self.tracetable.setRowCount(0)
        self.derivedtxt.clear()
        self.attrtxt.clear()

        self.current_rep_num = 0
        
        for attr in info:
            if attr != 'stim':
                self.attrtxt.appendPlainText(attr + ' : ' + str(info[attr]))
            else:
                # use the datafile object to do json converstion of stim data
                stimuli = self.datafile.get_trace_stim(path)

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
        dataset = self.datafile.get_data(path)
        if dataset is not None:
            # only data sets have a shape
            data_shape = dataset.shape
            # build a string for unknown data shape length
            dimstr = '('
            for dim in data_shape:
                dimstr += str(dim) + ', '
            # dont want last comma
            dimstr = dimstr[:-2] + ')'
            self.derivedtxt.appendPlainText("Dataset dimensions : " + dimstr)
            
            parent_path = '/'.join(path.split('/')[:-1])
            if len(parent_path) > 0:
                group_info = self.datafile.get_info(parent_path)
                fsout = group_info['samplerate_ad']
            else:
                fsout = info['samplerate_ad']
                group_info = []
            # group_info = self.datafile.get_info('/'.join(path.split('/')[:-1]))
            if setname.startswith('test') or setname.startswith('signal') or setname == 'reference_tone':
                # input samplerate is stored in group attributes
                self.derivedtxt.appendPlainText("Recording window duration : "+str(float(data_shape[-1])/fsout) + ' s')
            if setname.startswith('test'):
                self.testSelected.emit(path)
            self.current_data_shape = data_shape

            # also display "inherited" attributes from group
            self.attrtxt.appendHtml('<br><b>Segment Attributes:</b>')
            for gattr in group_info:
                self.attrtxt.appendPlainText(gattr + ' : ' + str(group_info[gattr]))

    def currentDataPath(self):
        return self.current_path, self.current_trace_num, self.current_rep_num

    def setTraceData(self, row, column, repnum=0):
        self.current_rep_num = repnum
        self.current_trace_num = row
        self._update_buttons()
        self.reviewDataSelected.emit(self.current_path, row, repnum)

    def selectTrace(self, tracenum, repnum=0):
        self.tracetable.selectRow(tracenum)
        self.setTraceData(tracenum, 0, repnum)

    def traceChanged(self, row, col, prevrow, prevcol):
        self.setTraceData(row, col)

    def nextRep(self):
        if self.current_rep_num == self.current_data_shape[1]-1 and self.current_trace_num == self.current_data_shape[0]-1:
            return
        self.current_rep_num += 1
        if self.current_rep_num == self.current_data_shape[1]:
            if self.traceStop:
                # stop here, don't advance to next trace
                self.stopTrace()
                self.current_rep_num -=1
            else:
                self.selectTrace(self.current_trace_num+1)
        else:
            self._update_buttons()
            self.reviewDataSelected.emit(self.current_path, self.current_trace_num, self.current_rep_num)

    def prevRep(self):
        if self.current_rep_num == 0 and self.current_trace_num == 0:
            return
        self.current_rep_num -= 1
        if self.current_rep_num == -1:
            self.selectTrace(self.current_trace_num-1, self.current_data_shape[1]-1)
        else:
            self._update_buttons()
            self.reviewDataSelected.emit(self.current_path, self.current_trace_num, self.current_rep_num)

    def firstRep(self):
        self.current_rep_num = 0
        self._update_buttons()
        self.reviewDataSelected.emit(self.current_path, self.current_trace_num, self.current_rep_num)

    def lastRep(self):
        self.current_rep_num = self.current_data_shape[1]-1
        self._update_buttons()
        self.reviewDataSelected.emit(self.current_path, self.current_trace_num, self.current_rep_num)

    def playTrace(self):
        self.firstRep()
        self.traceStop = True
        self.playTraceButton.setText("stop")
        self.playTraceButton.clicked.disconnect()
        self.playTraceButton.clicked.connect(self.stopTrace)
        self.playTestButton.setEnabled(False)
        self.timer.start(INTERVAL)

    def stopTrace(self):
        self.timer.stop()
        self.playTraceButton.setText("play")
        self.playTestButton.setText("play all")
        self.playTraceButton.clicked.disconnect()
        self.playTraceButton.clicked.connect(self.playTrace)
        self.playTestButton.clicked.disconnect()
        self.playTestButton.clicked.connect(self.playTest)
        self.playTestButton.setEnabled(True)
        self.playTraceButton.setEnabled(True)

    def playTest(self):
        self.setTraceData(0, 0, 0)
        self.traceStop = False
        self.playTestButton.clicked.disconnect()
        self.playTestButton.clicked.connect(self.stopTrace)
        self.playTraceButton.setEnabled(False)
        self.playTestButton.setText("stop")
        self.timer.start(INTERVAL)

    def overlayTrace(self):
        self.reviewDataSelected.emit(self.current_path, self.current_trace_num, -1)

    def _update_buttons(self):
        # enable/disable buttons appropriate to current location in the data
        if self.current_rep_num > 0 or self.current_trace_num > 0:
            self.prevButton.setEnabled(True)
        else:
            self.prevButton.setEnabled(False)
        if self.current_data_shape[1] > self.current_rep_num + 1 or self.current_data_shape[0] > self.current_trace_num + 1:
            self.nextButton.setEnabled(True)
        else:
            self.nextButton.setEnabled(False)
            self.stopTrace()
        if self.current_rep_num != 0:
            self.firstButton.setEnabled(True)
        else:
            self.firstButton.setEnabled(False)
        if self.current_rep_num < self.current_data_shape[1]-1:
            self.lastButton.setEnabled(True)
        else:
            self.lastButton.setEnabled(False)

class TraceTable(QtGui.QTableWidget):
    left = QtCore.Signal()
    right = QtCore.Signal()
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Left:
            self.left.emit()
        elif event.key() == QtCore.Qt.Key_Right:
            self.right.emit()
        else:
            super(TraceTable, self).keyPressEvent(event)

def makepath(item):
    if item is None:
        return ''
    elif item.text(0).endsWith('.hdf5'):
        return ''
    else:
        return makepath(item.parent()) + '/' + str(item.text(0))

if __name__ == '__main__':
    import sys
    from sparkle.data.open import open_acqdata
    from test import sample

    app = QtGui.QApplication(sys.argv)
    QtGui.qApp = app
    data = open_acqdata(sample.batlabfile()+".raw", filemode='r')
    # data = open_acqdata(sample.datafile(), filemode='r')
    viewer = QDataReviewer()
    viewer.setDataObject(data)
    viewer.show()
    app.exec_()
