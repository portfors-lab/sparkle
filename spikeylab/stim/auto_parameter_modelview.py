import cPickle

from PyQt4 import QtGui, QtCore

from auto_parameter_form import Ui_AutoParamWidget

PARAMETER_TYPES = ['duration', 'intensity', 'frequency']

class AutoParameterListView(QtGui.QListView):
    _selfieList = []

class AutoParameterModel(QtCore.QAbstractListModel):
    _parameters = []
    _stimmodel = None
    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._parameters)

    def data(self, index, role):
        # print 'data role', role
        return self._parameters[index.row()]
        # return cPickle.dumps(self._parameters[index.row()])
        # return QtCore.QVariant(cPickle.dumps(self._parameters[index.row()]))
        if role == QtCore.Qt.UserRole:
            param = self._parameters[index.row()]
            if not isinstance(param, dict):
                print 'waaaah', self._parameters
                param = cPickle.loads(str(param))
            param.pop('components', None)
            # return QtCore.QVariant(cPickle.dumps(param))
            return cPickle.dumps(self._parameters[index.row()])
        if role == QtCore.Qt.DisplayRole:
            # return 'Test display'
            return cPickle.dumps(self._parameters[index.row()])

    def setData(self, index, value, role):
        self._parameters[index.row()] = value
        return True

    def setParameterList(self, paramlist):
        self._parameters = paramlist

    def insertParameter(self, param, position):
        print '!!!!!!!!!!!!!!!!!inserting', position, param
        self.beginInsertRows(QtCore.QModelIndex(), position, position)
        self._parameters.insert(position, param)
        self.endInsertRows()


    def insertRows(self, position, rows, parent = QtCore.QModelIndex()):
        print '!!!!!!!!!!!!!!!!!inserting', position, rows, parent
        self.beginInsertRows(parent, position, position + rows - 1)
        for i in range(rows):
            defaultparam = { 'start': 0,
                             'delta': 1,
                             'stop': 0,
                             'parameter': 'duration',
                             # 'components' : QtGui.QItemSelectionModel(self._stimmodel)
                            }
            self._parameters.insert(position, defaultparam)
        print 'param list', self._parameters
        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent = QtCore.QModelIndex()):
        print '!!!!!!!!!!!removing'
        self.beginRemoveRows(parent, position, position + rows - 1)
        for i in range(rows):
            self._parameters.pop(position)
        self.endRemoveRows()
        return True

    def flags(self, index):
        if index.isValid():
            return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled
        else:
            return QtCore.Qt.ItemIsDropEnabled

    def setStimModel(self, stimmodel):
        self._stimmodel = stimmodel

    def edit(self, index):
        print 'edit triggered'
        param = self._parameters[index.row()]
        self._stimmodel.setSelectionModel(param['components'])
        super(AutoParameterModel, self).edit(index)

    def supportedDropActions(self):
        return QtCore.Qt.MoveAction

class AutoParameterDelegate(QtGui.QStyledItemDelegate):

    def paint(self, painter, option, index):
        # paint a fake editor widget
        painter.drawRect(option.rect)
        param = index.model().data(index, QtCore.Qt.UserRole)
        # param = cPickle.loads(param)
        # param = cPickle.loads(str(param.toString()))
        # print 'param type', param
        # param = filterdict(param)
        if isinstance(param, dict):
            if option.state & QtGui.QStyle.State_Selected:
                painter.fillRect(option.rect, option.palette.highlight())
            else:
                try:
                    tmpedit = AutoParamWidget()
                    tmpedit.setParamValues(param)
                    tmpedit.setGeometry(option.rect)
                    selfie = QtGui.QPixmap.grabWidget(tmpedit, QtCore.QRect(0,0, tmpedit.width(), tmpedit.height()))
                    painter.drawPixmap(option.rect, selfie)
                    tmpedit.close()
                except:
                    print '!!!!!!!!!!!problem wit dict'
                    print 'param', param
        else:
            painter.drawText(option.rect, QtCore.Qt.AlignLeft, "Lost the parameter")

    def sizeHint(self, option, index):
        #this will always be the same?
        return QtCore.QSize(100,150)

    def createEditor(self, parent, option, index):
        editor = AutoParamWidget(parent)
        return editor

    def setEditorData(self, editor, index):
        param = index.data(QtCore.Qt.UserRole)
        # param = cPickle.loads(str(param))

        # also need to set the selection model on the stim view
        editor.setParamValues(param)

    def setModelData(self, editor, model, index):
        param = editor.paramValues()
        # FIXME! save selection model
        # param['selfie'] = QtGui.QPixmap.grabWidget(editor, editor.geometry())

        model.setData(index, param, QtCore.Qt.EditRole)

class AutoParamWidget(QtGui.QWidget, Ui_AutoParamWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        for pt in PARAMETER_TYPES:
            self.type_cmbx.addItem(pt)

    def setParamValues(self, paramdict):
        self.step_lnedt.setText(str(paramdict['delta']))
        self.stop_lnedt.setText(str(paramdict['stop']))
        self.start_lnedt.setText(str(paramdict['start']))
        typeidx = PARAMETER_TYPES.index(paramdict['parameter'])
        self.type_cmbx.setCurrentIndex(typeidx)

        # self.membersview.setModel(paramdict['components'])

    def paramValues(self):
        paramdict = {}
        paramdict['start'] = float(self.start_lnedt.text())
        paramdict['delta'] = float(self.step_lnedt.text())
        paramdict['stop'] = float(self.stop_lnedt.text())
        paramdict['parameter'] = self.type_cmbx.currentText()
        # paramdict['components'] = self.membersview.model()
        return paramdict

def filterdict(d):
    newd ={}
    try:
        for k,v in d.iteritems():
            k = str(k)
            if isinstance(v, QtCore.QString):
                v = str(v)
            newd[k] = v
    except:
        print '!!!!!!!!!!!problem with dict'
        print d   
        raise     

    return newd