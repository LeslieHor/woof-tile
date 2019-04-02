from node import Node
import helpers
import config


class GroupNode(Node):
    """ Window Groups allow multiple windows to take the position where normally a single window would appear.
    It shades inactive windows and creates fake (non-functional) tabs to display which windows are a part of the group.

    Note: The active window of a window group is different from the active window of the entire system. A window group's
    active window simply says which window is unshaded, and which window can be focused.

    The structure contains a list for all windows in the window group, along with a separate list for the inactive
    windows to build the tabs with.
    """

    def __init__(self, active_window):
        Node.__init__(self, None)
        self.set_children([active_window])

        self.active_window_id = active_window.get_window_id()

    # ------------------------------------------------------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------------------------------------------------------

    def get_active_window_id(self):
        return self.active_window_id

    def get_inactive_windows_count(self):
        return self.get_child_count() - 1

    def get_active_window(self):
        [window] = [win for win in self.get_all_windows() if win.window_id == self.get_active_window_id()]
        return window

    def get_active_window_index(self):
        active_window = self.get_active_window()
        return self.get_child_index(active_window)

    def get_inactive_windows(self):
        index = self.get_child_index(self.get_active_window())
        children = self.get_children()
        inactive_children = children[:index] + children[index + 1:]
        return inactive_children

    # ------------------------------------------------------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------------------------------------------------------

    def set_active_window_id(self, new_active_window_id):
        self.active_window_id = new_active_window_id

    # ------------------------------------------------------------------------------------------------------------------
    # Trickle downs
    # ------------------------------------------------------------------------------------------------------------------

    def to_json(self):
        json = '{'
        json += '"type":' + helpers.json_com('group_node') + ','
        json += '"active_window_id":' + helpers.json_com(self.get_active_window_id()) + ','
        json += Node.to_json(self)
        json += '}'

        return json

    def redraw(self):
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
        y_pos += config.TOP_BORDER
        y_size -= config.TOP_BORDER

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
        if calling_child.get_window_id() == self.get_active_window_id():
            return self.get_active_viewport()
        else:
            return self.get_inactive_viewport(calling_child)

    def rotate_active_window(self, increment):
        active_index = self.get_active_window_index()
        active_index = (active_index + increment) % self.get_child_count()
        new_active_window = self.get_child(active_index)
        self.set_active_window_id(new_active_window.window_id)
        self.redraw()
        self.get_active_window().activate(True)
