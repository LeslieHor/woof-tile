from node import Node
import config


class GroupNode(Node):
    """ Window Groups allow multiple windows to take the position where normally a single window would appear.
    It shades inactive windows and creates fake (non-functional) tabs to display which windows are a part of the group.

    Note: The active window of a window group is different from the active window of the entire system. A window group's
    active window simply says which window is unshaded, and which window can be focused.

    The structure contains a list for all windows in the window group, along with a separate list for the inactive
    windows to build the tabs with.
    """

    def __init__(self, **kwargs):
        Node.__init__(self, None)

    # ------------------------------------------------------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------------------------------------------------------

    def get_inactive_windows_count(self):
        return self.get_child_count() - 1

    def get_active_window(self):
        return self.get_child(0)

    def get_inactive_windows(self):
        return self.get_children()[1:]

    def is_active(self, calling_child):
        return self.get_child_index(calling_child) == 0

    def is_group_node(self):
        return True

    # ------------------------------------------------------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------------------------
    # Trickle downs
    # ------------------------------------------------------------------------------------------------------------------

    def to_json(self):
        json = Node.to_json(self)
        json['type'] = 'group_node'

        return json

    def get_layout_json(self):
        json = Node.get_layout_json(self)
        json['type'] = 'group_node'

        return json

    def redraw(self):
        if self.get_child_count() == 0:
            return
        self.get_active_window().redraw()
        self.get_active_window().unshade()
        [win.redraw() for win in self.get_inactive_windows()]
        [win.shade() for win in self.get_inactive_windows()]

    # ------------------------------------------------------------------------------------------------------------------
    # Bubble ups
    # ------------------------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------------------------
    # Other
    # ------------------------------------------------------------------------------------------------------------------

    def get_active_viewport(self):
        (x_pos, y_pos), (x_size, y_size) = self.parent.get_viewport(self)
        y_pos += config.get_config('top_border')
        y_size -= config.get_config('top_border')

        return (x_pos, y_pos), (x_size, y_size)

    def get_inactive_viewports(self):
        (x_pos, y_pos), (x_size, y_size) = self.parent.get_viewport(self)

        x_pos_temp = x_pos
        increment = x_size / self.get_inactive_windows_count()

        viewports = []
        for _ in range(self.get_inactive_windows_count()):
            viewports.append(((x_pos_temp, y_pos), (increment, y_size)))
            x_pos_temp += increment

        return viewports

    def get_inactive_viewport(self, calling_child):
        index = self.get_inactive_windows().index(calling_child)
        return self.get_inactive_viewports()[index]

    def get_viewport(self, calling_child):
        if self.is_active(calling_child):
            return self.get_active_viewport()
        else:
            return self.get_inactive_viewport(calling_child)

    def rotate_active_window(self, increment):
        self.rotate_children(increment)
        self.redraw()
        self.get_active_window().activate(True)
