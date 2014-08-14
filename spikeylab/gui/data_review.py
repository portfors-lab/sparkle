from spikeylab.gui.hdftree import H5TreeWidget
from spikeylab.data.dataobjects import AcquisitionData
from spikeylab.gui.stim.component_detail import ComponentsDetailWidget

from PyQt4 import QtCore, QtGui

class QDataReviewer(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        layout = QtGui.QHBoxLayout(self)

        hsplitter = QtGui.QSplitter(QtCore.Qt.Horizontal)

        asplitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.datatree = H5TreeWidget()
        self.datatree.itemClicked.connect(self.setCurrentData)
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

        # traceLayout = QtGui.QVBoxLayout()
        traceSplitter = QtGui.QSplitter(QtCore.Qt.Vertical)

        self.tracetable = QtGui.QTableWidget()
        headers = ['No. Components', 'Stim Type', 'Sample Rate (Hz)']
        self.tracetable.setColumnCount(len(headers))
        self.tracetable.setHorizontalHeaderLabels(headers)
        self.tracetable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tracetable.cellClicked.connect(self.setTraceData)
        traceSplitter.addWidget(self.tracetable)

        self.detailWidget = ComponentsDetailWidget()
        scroller = QtGui.QScrollArea()
        scroller.setWidget(self.detailWidget)
        scroller.setWidgetResizable(True)
        traceSplitter.addWidget(scroller)

        hsplitter.addWidget(traceSplitter)
        layout.addWidget(hsplitter)

    def setDataObject(self, data):
        self.datafile = data
        # display contents as a tree
        self.datatree.addH5Handle(data.hdf5)
        self.datatree.expandItem(self.datatree.topLevelItem(0))

    def update(self):
        self.datatree.update(self.datafile.hdf5)

    def setCurrentData(self, widgetitem, num):
        path = makepath(widgetitem)
        info = self.datafile.get_info(path)
        self.attrtxt.clear()
        for attr in info:
            if attr[0] != 'stim':
                self.attrtxt.appendPlainText(attr[0] + ' : ' + str(attr[1]))

        setname = widgetitem.text(0)
        self.tracetable.setRowCount(0)
        self.derivedtxt.clear()
        if setname.startsWith('test') or setname.startsWith('signal'):
            self.detailWidget.clearDoc()
            trace_data = self.datafile.get(path)
            # input samplerate is stored in group attributes
            group_data = self.datafile.get_info('/'.join(path.split('/')[:-1]))
            fsout = dict(group_data)['samplerate_ad']
            self.derivedtxt.appendPlainText("Dataset dimensions : "+str(trace_data.shape))
            self.derivedtxt.appendPlainText("Recording window duration : "+str(float(trace_data.shape[-1])/fsout) + ' s')
            if self.datafile.get_trace_info(path) is not None:
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


    def setTraceData(self, row, column):
        self.detailWidget.clearDoc()
        self.detailWidget.setDoc(self.current_test[row]['components'])

    def setDisplayAttributes(self, attrs):
        self.detailWidget.setDisplayTable(attrs)

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
    viewer.setDisplayAttributes({'Vocalization': [u'Vocalization', u'risefall', u'intensity', u'file', u'duration', 'start_s'], 'silence': [u'silence', u'duration', u'risefall', u'intensity'], 'Pure Tone': [u'Pure Tone', u'duration', u'risefall', u'intensity', u'frequency']})
    viewer.show()
    app.exec_()