from enthought.etsconfig.etsconfig import ETSConfig
ETSConfig.toolkit = "qt4"

from traits.api import Instance, Int, Float
from chaco.tools.api import PanTool, BroadcasterTool, DragTool, BetterZoom
from enthought.enable.api import Component
from chaco.tools.tool_states import ZoomState, PanState, GroupedToolState, ToolState

class AxisZoomTool(BetterZoom):
    """ Tool to zoom single axis at a time, using mouse location to determine axis"""
    def dispatch(self, event, suffix):
        if (event.x < self.component.padding_left+10) and not (event.y < self.component.padding_bottom+10):
            # mouse is beside y axis
            self.axis = 'value'
        elif (event.y < self.component.padding_bottom+10) and not (event.x < self.component.padding_left+10):
            # mouse is beside x axis
            self.axis = 'index'
        else:
            # don't zoom in middle of plot
            return
        super(AxisZoomTool, self).dispatch(event,suffix)

    def _do_zoom(self, new_index_factor, new_value_factor):

        if self.zoom_to_mouse:
            x_map = self._get_x_mapper()
            y_map = self._get_y_mapper()
            location = self.position

            cx = (x_map.range.high + x_map.range.low)/2
            if self._index_factor == new_index_factor:
                nextx = cx
            else:
                x = x_map.map_data(location[0])
                nextx = x + (cx - x)*(self._index_factor/new_index_factor)

            cy = (y_map.range.high + y_map.range.low)/2
            if self._value_factor == new_value_factor:
                nexty = cy
            else:
                # force y zoom to center point at 0
                y = 0
                nexty = y + (cy - y)*(self._value_factor/new_value_factor)

            # print 'cx', cx, 'cy', cy, 'next x', nextx, 'nexty'
            # print 'index factor', self._index_factor, 'value factor', self._value_factor, 'new index factor', new_index_factor, 'new value factor', new_value_factor
            pan_state = PanState((cx,cy), (nextx, nexty))
            zoom_state = ZoomState((self._index_factor, self._value_factor),
                                   (new_index_factor, new_value_factor))

            states = GroupedToolState([pan_state, zoom_state])
            states.apply(self)
            self._append_state(states)

        else:

            zoom_state = ZoomState((self._index_factor, self._value_factor),
                                   (new_index_factor, new_value_factor))

            zoom_state.apply(self)
            self._append_state(zoom_state)
        self._check_extents()

    def set_xdomain(self, limits):
        x_mapper = self._get_x_mapper()
        x_mapper.domain_limits = limits

    def _check_extents(self):
        """Check that zoom did not overshoot"""
        # This is neccessary because domain_limits are not enforced correctly?
        lims = self._get_x_mapper().domain_limits
        if self.component.index_range.low < lims[0]:
            self.component.index_range.low = lims[0]
        if self.component.index_range.high > lims[1]:
            self.component.index_range.high = lims[1]


class LineDraggingTool(DragTool):

    component = Instance(Component)
    # The pixel distance from a point that the cursor is still considered
    # to be 'on' the point
    tolerance = Int(5)

    # value of line at beginning of drag
    _orig_value = Float

    signal = None

    def is_draggable(self, x, y):
        # Check to see if (x,y) are over one of the points in self.component
        l = self._lookup_point(x, y)
        if l is not None:
            return True
        else:
            return False

    def drag_start(self, event):
        plot = self.component
        # ndx = plot.map_index((event.x, event.y), self.threshold)
        ndx = plot.get_closest_line((event.x-self.xoffset, event.y-self.yoffset), self.tolerance)
        if ndx is None:
            return
        plot_point = plot.map_data((event.x-self.xoffset, event.y-self.yoffset), all_values=True)
        self._orig_value = plot_point[1]

    def dragging(self, event):
        plot = self.component

        plot_point = plot.map_data((event.x-self.xoffset, event.y-self.yoffset), all_values=True)
        # data_x, data_y = plot.map_data((event.x, event.y))

        plot.value._data = [plot_point[1]]*len(plot.value._data)
        plot.value.data_changed = True
        plot.request_redraw()

    def drag_cancel(self, event):
        print 'drag cancel'
        plot = self.component
        plot.value._data = [self._orig_value]*len(plot.value._data)
        plot.value.data_changed = True
        plot.request_redraw()

    def drag_end(self, event):
        if self.signal is not None:
            self.signal.emit(self.component.value._data[0])
        
    def _lookup_point(self, x, y):
        """ Finds the point closest to a screen point if it is within self.threshold

            Parameters
            ==========
            x : float
            screen x-coordinate
            y : float
            screen y-coordinate

            Returns
            =======
            (screen_x, screen_y, distance) of datapoint nearest to the input *(x,y)*.
            If no data points are within *self.threshold* of *(x,y)*, returns None.
            """

        if hasattr(self.component, 'get_closest_line'):
            # This is on BaseXYPlots
            return self.component.get_closest_line((x-self.xoffset, y-self.yoffset), self.tolerance)

        return None

    def set_offsets(self, x, y):
        self.xoffset = x
        self.yoffset = y

    def register_signal(self, signal):
        """ saves signal for emitting value after drag end """
        self.signal = signal


class SpikeTraceBroadcasterTool(BroadcasterTool):

    component = Instance(Component)
    tolerance = Int(5)
    xoffset = 0
    yoffset = 0
    pan_enabled = True # flag saves us from looping through tools

    def dispatch(self, event, suffix):
        if suffix == 'left_down':
            plot = self.component
            ndx = plot.get_closest_line((event.x-self.xoffset, event.y-self.yoffset), self.tolerance)
            if ndx is not None:
                # just remove paning tool, and underlying dragging tool
                # should work
                for t in self.tools:
                    if t.__class__.__name__ == "PanTool":
                        self.tools.remove(t)
                        self.pan_enabled = False
                        self.pt = t
            elif not self.pan_enabled:
                # if user clicks on anything apart from threshold line
                self.tools.append(self.pt)

        BroadcasterTool.dispatch(self, event, suffix)

    def _lookup_point(self, x, y):
        if hasattr(self.component, 'get_closest_line'):
            # This is on BaseXYPlots
            return self.component.get_closest_line((x,y), threshold=self.tolerance)
        else:
            print 'no such method: get_closest_line'

        return None

    def set_offsets(self, x, y):
        self.xoffset = x
        self.yoffset = y
        # also go through and set child tools?
        for t in self.tools:
            if hasattr(t, 'set_offsets'):
                t.set_offsets(x,y)
            