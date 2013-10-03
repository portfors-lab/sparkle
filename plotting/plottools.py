from enthought.etsconfig.etsconfig import ETSConfig
ETSConfig.toolkit = "qt4"

from traits.api import Instance, Int, Float
from chaco.tools.api import PanTool, ZoomTool, BroadcasterTool, DragTool
from enthought.enable.api import Component



class LineDraggingTool(DragTool):

    component = Instance(Component)

    # The pixel distance from a point that the cursor is still considered
    # to be 'on' the point
    tolerance = Int(5)

    # value of line at beginning of drag
    _orig_value = Float

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
        self._drag_index = ndx
        self._orig_value = plot_point[1]

    def dragging(self, event):
        plot = self.component

        plot_point = plot.map_data((event.x-self.xoffset, event.y-self.yoffset), all_values=True)
        # data_x, data_y = plot.map_data((event.x, event.y))

        plot.value._data = [plot_point[1]]*len(plot.value._data)
        plot.value.data_changed = True
        plot.request_redraw()

    def drag_cancel(self, event):
        plot = self.component
        plot.value._data[:] = [self._orig_value]*len(plot.value._data)
        plot.value.data_changed = True
        plot.request_redraw()

    def drag_end(self, event):
        return
        plot = self.component
        if plot.index.metadata.has_key('selections'):
            del plot.index.metadata['selections']
        plot.invalidate_draw()
        plot.request_redraw()

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

class SpikeTraceBroadcasterTool(BroadcasterTool):

    component = Instance(Component)
    tolerance = Int(20)
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
            elif not self.pan_enabled:
                # if user clicks on anything apart from threshold line
                self.tools.append(PanTool(self.component))

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
            