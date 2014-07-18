import numpy as np

class AutoParameterModel():
    def __init__(self):
        self._parameters = []
        self._headers = ['parameter', 'start', 'stop', 'step', 'nsteps']

    def header(self, column):
        return self._headers[column]

    def nrows(self):
        return len(self._parameters)

    def ncols(self):
        return 5

    def clearParameters(self):
        self._parameters = []

    def param(self, row):
        return self._parameters[row]

    def selection(self, row):
        return self._parameters[row]['selection']

    def allData(self):
        return self._parameters

    def toggleSelection(self, row, component):
        selection = self._parameters[row]['selection']
        if component in selection:
            selection.remove(component)
        else:
            selection.append(component)

    def setParamValue(self, row, **kwargs):
        # param_copy = self._parameters[row].copy()
        param = self._parameters[row]
        for key, val in kwargs.items():
            param[key] = val
        #     param_copy[key] = val
        # if self.verify_row(param_copy):
        #     self._parameters[row] = param_copy

    def paramValue(self, row, field):
        param = self._parameters[row]
        return param[field]

    def overwriteParam(self, row, param):
        self._parameters[row] = param

    def getDetail(self, row, detail_field):
        param = self._parameters[row]
        param_type = param['parameter']
        components = param['selection']
        if len(components) == 0 or param_type == '':
            return None
        # all components must match
        matching_details = []
        # for comp in components:
        for comp in components:
            alldetails = comp.auto_details()
            if not param_type in alldetails:
                self.hintRequested.emit('INCOMPATABLE COMPONENTS FOR PARAMETER TYPE {}'.format(param_type))
                return None
            details = alldetails[param_type]
            matching_details.append(details[detail_field])
        matching_details = set(matching_details)
        if len(matching_details) > 1:
            print 'Components with mis-matched units!'
            return None
        return matching_details.pop()

    def checkLimits(self, value, param):
        # extract the selected component names
        components = param['selection']
        ptype = param['parameter']
        if len(components) == 0:
            return False
        mins = []
        maxs = []
        for comp in components:
            # get the limit details for the currently selected parameter type
            try:
                details = comp.auto_details()[ptype]
                mins.append(details['min'])
                maxs.append(details['max'])
            except KeyError:
                raise
                return False
        lower = max(mins)
        upper = min(maxs)
        if lower <= value <= upper:
            return True
        else:
            # print 'value out of bounds:'
            # print 'lower', lower, 'upper', upper, 'value', value
            return False 

    def setParameterList(self, paramlist):
        self._parameters = paramlist

    def insertRow(self, position):
        if position == -1:
            position = self.nrows()
        defaultparam = { 'start': 0,
                         'step': 0,
                         'stop': 0,
                         'parameter': '',
                         'selection' : [],
                        }
        self._parameters.insert(position, defaultparam)

    def removeRow(self, position):
        p = self._parameters.pop(position)
        return p

    def selectedParameterTypes(self, row):
        param = self._parameters[row]
        return self._selectionParameters(param)

    def _selectionParameters(self, param):
        components = param['selection']
        if len(components) == 0:
            return []
        # extract the selected component names
        editable_sets = []
        for comp in components:
            # all the keys (component names) for the auto details for components in selection
            details = comp.auto_details()
            editable_sets.append(set(details.keys()))
        editable_paramters = set.intersection(*editable_sets)
        return list(editable_paramters)

    def verify(self):
        for param in self._parameters:
            result = self.verify_row(param)
            if result != 0:
                return result
        return 0

    def verify_row(self, param):
        if param['parameter'] == '':
            return "Auto-parameter type undefined"
        if param['parameter'] not in self._selectionParameters(param):
            return 'Parameter {} not present in all selected components'.format(param['parameter'])
        if param['step'] == 0 and param['start'] != param['stop']:
            return "Auto-parameter step size of 0 not allowed"
        if abs(param['stop'] - param['start']) < param['step']:
            return "Auto-parameter step size larger than range"
        if not self.checkLimits(param['start'], param):
            return "Auto-parameter start value invalid"
        if not self.checkLimits(param['stop'], param):
            return "Auto-parameter stop value invalid"
        return 0
