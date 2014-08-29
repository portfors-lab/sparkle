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

    def setScaledValue(self, row, field, value):
        if self._parameters[row]['parameter'] == 'file':
            return # cannot be set this way?
        if field == 'parameter':
            old_multiplier = self.getDetail(row, 'multiplier')
            self.setParamValue(row, parameter=value)
            # keep the displayed values the same, so multiply to ajust
            # real underlying value
            new_multiplier = self.getDetail(row, 'multiplier')
            if old_multiplier is not None and old_multiplier != new_multiplier:
                new_multiplier = float(new_multiplier)
                for f in ['start', 'stop', 'step']:
                    self.setScaledValue(row, f, (self.paramValue(row, f)/new_multiplier)*(new_multiplier/old_multiplier))
        elif field in ['start', 'stop', 'step']:
            multiplier = self.getDetail(row, 'multiplier')
            if multiplier is not None:
                if self.checkLimits(row, value*multiplier):
                    kwd = {field : value*multiplier}
                    self.setParamValue(row, **kwd)

    def scaledValue(self, row, field):
        if field == 'parameter':            
            return self.paramValue(row, field)
        elif field in ['start', 'stop', 'step']:
            if self._parameters[row]['parameter'] == 'file':
                return 0
            else:
                val = self.paramValue(row, field)
                multiplier = self.getDetail(row, 'multiplier')
                if multiplier is not None:
                    return float(val)/multiplier
        elif field == 'nsteps':
            return self.numSteps(row)

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
        if row == -1:
            row = self.nrows() - 1
        print 'parameters', self._parameters, row
        self._parameters[row] = param

    def numSteps(self, row):
        param = self._parameters[row]
        return self.nStepsForParam(param)

    def nStepsForParam(self, param):
        if param['parameter'] == 'file':
            return len(param['names'])
        else:
            if param['step'] > 0:
                if abs(param['start'] - param['stop']) < param['step']:
                    return 0
                # print 'range', param['start'] - param['stop']
                nsteps = np.around(abs(param['start'] - param['stop']), 4) / float(param['step'])
                item = int(np.ceil(nsteps)+1)
            elif param['start'] == param['stop']:
                item = 1
            else:
                item = 0
            return item
        
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
                # self.hintRequested.emit('INCOMPATABLE COMPONENTS FOR PARAMETER TYPE {}'.format(param_type))
                return None
            details = alldetails[param_type]
            matching_details.append(details[detail_field])
        matching_details = set(matching_details)
        if len(matching_details) > 1:
            print 'Components with mis-matched units!'
            return None
        return matching_details.pop()

    def isFieldValid(self, row, field):
        param = self._parameters[row]
        if param['parameter'] == '':
            return False
        if field == 'nsteps':
            return self.numSteps(row) != 0
        if param['parameter'] == 'file':
            # do something here... check filenames?
            return True
        if field == 'parameter':
            return True
        # else check that value is between min and max allowed
        return self.checkLimits(row, param[field])

    def findFileParam(self, comp):
        for p in self._parameters:
            if p['parameter'] == 'file' and comp in p['selection']:
                return p['names']

    def checkLimits(self, row, value):
        # extract the selected component names
        param = self._parameters[row]
        components = param['selection']
        if len(components) == 0:
            return False
        ptype = param['parameter']
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

    def ranges(self):
        steps = []
        for p in self._parameters:
            # inclusive range
            if p['parameter'] == 'file':
                steps.append(p['names'])
            else:
                if p['step'] > 0:
                    start = p['start']
                    stop = p['stop']
                    if start > stop:
                        step = p['step']*-1
                    else:
                        step = p['step']
                    # nsteps = np.ceil(np.around(abs(start - stop), 4) / p['step'])
                    nsteps = self.nStepsForParam(p)
                    # print 'nsteps', np.around(abs(start - stop), 4), p['step']
                    print 'start, stop, steps', start, stop, nsteps
                    step_tmp = np.linspace(start, start+step*(nsteps-2), nsteps-1)
                    print 'step_tmp', step_tmp

                    # if step_tmp[-1] != stop:
                    step_tmp = np.append(step_tmp,stop)
                    # print 'step range', step_tmp

                    steps.append(np.around(step_tmp,4))
                else:
                    assert p['start'] == p['stop']
                    steps.append([p['start']])
        return steps

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

    def updateComponentStartVals(self):
        """Go through selected components for each auto parameter and set the start value"""
        for param in self._parameters:
            for component in param['selection']:
                if param['parameter'] == 'file':
                    component.set(param['parameter'], param['names'][0])
                else:
                    component.set(param['parameter'], param['start'])

    def fileParameter(self, comp):
        for row in range(self.nrows()):
            p = self._parameters[row]
            if p['parameter'] == 'file':
                # ASSUMES EXACTLY ONE COMPONENT IN SELECTION
                if p['selection'][0] == comp:
                    return row

    def editableRow(self, row):
        return self._parameters[row]['parameter'] != 'file'

    def verify(self):
        # for param in self._parameters:
        for row in range(self.nrows()):
            result = self.verify_row(row)
            if result != 0:
                return result
        return 0

    def verify_row(self, row):
        param = self._parameters[row]
        if param['parameter'] == '':
            return "Auto-parameter type undefined"
        if param['parameter'] not in self._selectionParameters(param):
            return 'Parameter {} not present in all selected components'.format(param['parameter'])
        if param['parameter'] == 'file':
            if len(param['names']) < 1:
                return "No filenames in file auto-parameter list"
        else:
            if param['step'] == 0 and param['start'] != param['stop']:
                return "Auto-parameter step size of 0 not allowed"
            if abs(param['stop'] - param['start']) < param['step']:
                return "Auto-parameter step size larger than range"
            if not self.checkLimits(row, param['start']):
                return "Auto-parameter start value invalid"
            if not self.checkLimits(row, param['stop']):
                return "Auto-parameter stop value invalid"
        return 0
