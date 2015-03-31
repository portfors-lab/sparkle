import numpy as np


class AutoParameterModel():
    """Model to hold all the necessary information to generate
    auto-tests, where parameters of components are systematically
    manipulated
    """
    def __init__(self):
        self._parameters = []

    def nrows(self):
        """The number of auto-parameters

        :returns: int -- parameter count
        """
        return len(self._parameters)

    def clearParameters(self):
        """Clears all parameters out of this model"""
        self._parameters = []

    def param(self, row):
        """Gets the parameter indexed by *row*

        :param row: the ith parameter number
        :type row: int
        :returns: dict -- the parameter
        """
        return self._parameters[row]

    def selection(self, row):
        """Gets the component selection for parameter number *row*
        
        :param row: the ith parameter number
        :type row: int
        :returns: list<:class:`AbstractStimulusComponent<sparkle.stim.abstract_component.AbstractStimulusComponent>`>
        """
        return self._parameters[row]['selection']

    def allData(self):
        """Gets a list of all the parameters in this model

        :returns: list<dict> -- all parameters
        """
        return self._parameters

    def toggleSelection(self, row, component):
        """Toggles the *component* in or out of the selection 
        for parameter *row*

        :param row: the ith parameter number
        :type row: int
        :param component: the component to toggle its selection membership
        :type component: :class:`AbstractStimulusComponent<sparkle.stim.abstract_component.AbstractStimulusComponent>`
        """
        selection = self._parameters[row]['selection']
        if component in selection:
            selection.remove(component)
        else:
            selection.append(component)

    def setVerifiedValue(self, row, field, value):
        """Sets the *value* for *field* in the parameter
        indexed by *row*, only if the value is within set limits

        :param row: the ith parameter number
        :type row: int
        :param field: detail of the parameter to set
        :type field: str
        :param value: pre-scaled value to assign to field
        """
        if self._parameters[row]['parameter'] == 'filename':
            return # cannot be set this way?
        if field == 'parameter':
            self.setParamValue(row, parameter=value)
        elif field in ['start', 'stop', 'step']:
            if self.checkLimits(row, value):
                kwd = {field : value}
                self.setParamValue(row, **kwd)

    def setParamValue(self, row, **kwargs):
        """Sets the arguments as field=val for parameter
        indexed by *row*

        :param row: the ith parameter number
        :type row: int
        """
        param = self._parameters[row]
        for key, val in kwargs.items():
            param[key] = val

    def paramValue(self, row, field):
        """Gets the value for *field* for parameter indexed by
        *row*
        
        :param row: the ith parameter number
        :type row: int
        :param field: detail of the parameter to set
        :type field: str
        :returns: value -- type appropriate to parameter
        """
        if field == 'nsteps':
            return self.numSteps(row)
        if field in ['start', 'stop', 'step'] and self._parameters[row]['parameter'] == 'filename':
                return '-'
        else:
            param = self._parameters[row]
            return param[field]

    def overwriteParam(self, row, param):
        """Assigns *param* to index *row*, overwritting the
        parameter at that location

        :param row: the ith parameter number
        :type row: int
        :param param: parameter to set
        :type param: dict
        """
        if row == -1:
            row = self.nrows() - 1
        self._parameters[row] = param

    def numSteps(self, row):
        """Gets the number of steps for the parameter at 
        index *row* will yeild
        """
        param = self._parameters[row]
        return self.nStepsForParam(param)

    def nStepsForParam(self, param):
        """Gets the number of steps *parameter* will yeild

        :param param: parameter to get the expansion count for
        :type param: dict
        """
        if param['parameter'] == 'filename':
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
        """Gets the value of the detail *detail_field* of paramter
        at index *row* from its selected components `auto_details`.
        All of the selected components value for *detail_field* must
        match

        :param row: the ith parameter number
        :type row: int
        :param detail_field: auto_details member key
        :type detail_field: str
        :returns: value type appropriate for parameter
        """
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
        """Verifies the value in *field* for parameter at index 
        *row*

        :param row: the ith parameter number
        :type row: int
        :param field: detail of the parameter to check
        :type field: str
        :returns: bool -- True if valid
        """
        param = self._parameters[row]
        if param['parameter'] == '':
            return False
        if field == 'nsteps':
            return self.numSteps(row) != 0
        if param['parameter'] == 'filename':
            # do something here... check filenames?
            return True
        if field == 'parameter':
            return True
        # else check that value is between min and max allowed
        return self.checkLimits(row, param[field])

    def findFileParam(self, comp):
        """Finds the filename auto-parameter that component *comp* is
        in, and returns all the filenames for that parameter. Notes this
        assumes that *comp* will only be in a single filename auto-parameter.

        :param comp: Component to search parameter membership for
        :type comp: :class:`AbstractStimulusComponent<sparkle.stim.abstract_component.AbstractStimulusComponent>`
        :returns: list<str> -- filenames the found parameter will loop through
        """
        for p in self._parameters:
            if p['parameter'] == 'filename' and comp in p['selection']:
                return p['names']

    def checkLimits(self, row, value):
        """Check that *value* is within the minimum and maximum allowable 
        range for the parameter at index *row*

        :param row: the ith parameter number
        :type row: int
        :param value: the candidate value to for start or stop fields
        :returns: bool -- True if *value* within range
        """
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
        """Clears and sets all parameters to *paramlist*

        :param paramlist: all parameters for this model to have
        :type paramlist: list<dict>
        """
        self._parameters = paramlist

    def insertRow(self, position):
        """Inserts an empty parameter at index *position*

        :param position: order to insert new parameter to
        :type position: int
        """
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
        """Removes the parameter at index *position*

        :param position: the parameter index
        :type position: int
        :returns: dict -- the removed parameter
        """
        p = self._parameters.pop(position)
        return p

    def selectedParameterTypes(self, row):
        """Gets a list of the intersection of the editable properties in the parameteter *param*'s
        component selection. E.g. ['frequency', 'intensity']

        :param row: the ith parameter number
        :type row: int
        :returns: list<str> -- a list of AbstractStimulusComponent attribute names
        """
        param = self._parameters[row]
        return self._selectionParameters(param)

    def ranges(self):
        """The expanded lists of values generated from the parameter fields

        :returns: list<list>, outer list is for each parameter, inner loops are that
        parameter's values to loop through
        """
        steps = []
        for p in self._parameters:
            # inclusive range
            if p['parameter'] == 'filename':
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
                    # print 'start, stop, steps', start, stop, nsteps
                    step_tmp = np.linspace(start, start+step*(nsteps-2), nsteps-1)
                    # print 'step_tmp', step_tmp

                    # if step_tmp[-1] != stop:
                    step_tmp = np.append(step_tmp,stop)
                    # print 'step range', step_tmp

                    steps.append(np.around(step_tmp,4))
                else:
                    assert p['start'] == p['stop']
                    steps.append([p['start']])
        return steps

    def _selectionParameters(self, param):
        """see docstring for selectedParameterTypes"""
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
        # do not allow selecting of filename from here
        return list(editable_paramters)

    def updateComponentStartVals(self):
        """Go through selected components for each auto parameter and set the start value"""
        for param in self._parameters:
            for component in param['selection']:
                if param['parameter'] == 'filename':
                    component.set(param['parameter'], param['names'][0])
                else:
                    component.set(param['parameter'], param['start'])

    def fileParameter(self, comp):
        """Returns the row which component *comp* can be found in the 
        selections of, and is also a filename parameter

        :returns: int -- the index of the (filename) parameter *comp* is a member of 
        """
        for row in range(self.nrows()):
            p = self._parameters[row]
            if p['parameter'] == 'filename':
                # ASSUMES COMPONENT IN ONE SELECTION
                if comp in p['selection']:
                    return row

    def editableRow(self, row):
        """Returns whether parameter at index *row* is editable

        :returns: bool -- True if values can be manipulated
        """
        return self._parameters[row]['parameter'] != 'filename'

    def verify(self):
        """Checks all parameters for invalidating conditions

        :returns: str -- message if error, 0 otherwise
        """
        for row in range(self.nrows()):
            result = self.verify_row(row)
            if result != 0:
                return result
        return 0

    def verify_row(self, row):
        """Checks parameter at index *row* for invalidating conditions

        :returns: str -- message if error, 0 otherwise
        """
        param = self._parameters[row]
        if param['parameter'] == '':
            return "Auto-parameter type undefined"
        if len(param['selection']) == 0:
            return "At least one component must be selected for each auto-parameter"
        if param['parameter'] not in self._selectionParameters(param):
            return 'Parameter {} not present in all selected components'.format(param['parameter'])
        if param['parameter'] == 'filename':
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
