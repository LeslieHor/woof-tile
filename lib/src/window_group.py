from config import *
from log import log_info, log_debug, log_warning, log_error


class WindowGroup:
    """ Window Groups allow multiple windows to take the position where normally a single window would appear.
    It shades inactive windows and creates fake (non-functional) tabs to display which windows are a part of the group.

    Note: The active window of a window group is different from the active window of the entire system. A window group's
    active window simply says which window is unshaded, and which window can be focused.

    The structure contains a list for all windows in the window group, along with a separate list for the inactive
    windows to build the tabs with.
    """

    def __init__(self, parent, active_window, inactive_windows):
        self.all_windows = [active_window] + inactive_windows
        self.active_window = active_window
        self.inactive_windows = inactive_windows
        self.active_window_index = 0

        self.parent = parent

    def debug_print(self, level):
        print(" " * level + "WG WinCount: " + str(len(self.all_windows)) + ". Active: " + str(
            self.all_windows.index(self.active_window)))
        window_counter = 0
        for window in self.all_windows:
            window_counter += window.debug_print(level + 1)
        return window_counter

    """Ripple gap correction requests up to the root screen"""

    def gap_correct_left(self, l):
        return self.parent.gap_correct_left(l)

    def gap_correct_down(self, d):
        return self.parent.gap_correct_down(d)

    def gap_correct_up(self, u):
        return self.parent.gap_correct_up(u)

    def gap_correct_right(self, r):
        return self.parent.gap_correct_right(r)

    """ Calculates the shaded size of the particular index"""

    def get_shaded_size(self, index):
        l, d, u, r = self.parent.get_borders(self)
        increment = (r - l) / len(self.inactive_windows)
        borders = range(l, r, increment) + [r]
        return borders[index], d, u, borders[index + 1]

    """Adds a new window to the window group and focuses it"""

    def add_window(self, new_window):
        self.all_windows.append(new_window)
        self.inactive_windows.append(new_window)
        new_window_index = len(self.inactive_windows)
        offset = new_window_index - self.active_window_index
        self.activate_next_window(offset)

    def set_size(self):
        """Sets the size of the tabs and active window
        """
        for window in self.inactive_windows:
            window.set_size()
            window.shade()
        self.active_window.set_size()
        self.active_window.unshade()

    def activate_active_window(self):
        """Activates whatever window is currently defined as active"""
        log_debug(['Activating active window'])
        self.set_size()
        self.active_window.activate(True)

    def activate_next_window(self, increment):
        """Increments the counter by Increment and activates whatever
        window that is in the list.
        """
        self.active_window_index += increment
        self.active_window_index %= len(self.all_windows)

        self.active_window = self.all_windows[self.active_window_index]
        self.inactive_windows = list(self.all_windows)
        del self.inactive_windows[self.active_window_index]
        rotated_list = self.inactive_windows[self.active_window_index:] + self.inactive_windows[
                                                                          : self.active_window_index]
        self.inactive_windows = rotated_list

        self.activate_active_window()

    """Resizes window group"""

    def resize_vert(self, _caller_child, increment):
        return self.parent.resize_vertical(self, increment)

    def resize_horz(self, _caller_child, increment):
        return self.parent.resize_horizontal(self, increment)

    def find_earliest_a_but_not_me(self, _caller_child):
        """Returns the earliest 'ChildA' not part of the call stack
        Rippled up as window groups have no ChildA/ChildB
        """
        return self.parent.find_earliest_a_but_not_me(self)

    def all_are_bees(self, _caller_child):
        """Returns if all objects in call stack are 'ChildB'
        Rippled up as window groups have no ChildA/ChildB
        """
        return self.parent.all_are_bees(self)

    def get_borders(self, calling_child):
        """Returns borders of the current pane"""
        if calling_child == self.active_window:
            return self.get_active_size()
        else:
            child_index = self.inactive_windows.index(calling_child)
            return self.get_shaded_size(child_index)

    def get_active_size(self):
        l, d, u, r = self.parent.get_borders(self)
        return l, d, u + TOP_BORDER, r

    def kill_window(self, caller_child):
        """Removes the calling window from the windowgroup

        If the size of the window group is two, then removing a window leaves a window group with
        only one window, which should be converted back into a regular window

        Return the ID of which window to activate to keep the system focus within the window group
        """
        if len(self.all_windows) == 2:
            # The remaining window will be a single, so we
            # turn it into a normal window
            self.all_windows.remove(caller_child)
            log_debug(['Removed calling child:', caller_child.window_id])
            log_debug(['AllWindows length:', len(self.all_windows)])
            surviving_child = self.all_windows[0]
            log_debug(['SurvivingChild:', surviving_child.window_id])
            self.parent.replace_child(self, surviving_child)
            log_debug(['Replacing parent child with surviving child'])
            surviving_child.parent = self.parent
            log_debug(['Replacing child parent with windowgroup parent'])
            surviving_child.unshade()
            surviving_child.set_size()
            return str(surviving_child.window_id)
        else:
            self.all_windows.remove(caller_child)
            self.activate_next_window(0)
            return str(self.active_window.window_id)

    def split(self, _caller_child, new_window, plane_type, direction):
        """Splits the window to add a new window beside it"""
        self.parent.split(self, new_window, plane_type, direction)

    def get_plane_type(self):
        """Returns parent PlaneType"""
        return self.parent.PlaneType

    def list_screen_windows(self):
        return self.parent.list_screen_windows()

    def window_ids(self):
        window_ids = []
        for win in self.all_windows:
            window_ids.append(win.window_id)
        return window_ids

    def get_screen_borders(self):
        return self.parent.get_screen_borders()

    def minimize(self):
        for window in self.all_windows:
            window.minimize()

    def get_screen_index(self, _calling_child):
        return self.parent.get_screen_index(self)

    def get_window_list(self):
        return self.all_windows

    def get_available_window_list(self):
        return [self.active_window]

    def is_any_maximized(self):
        any_maximized = False
        for window in self.all_windows:
            any_maximized = any_maximized or window.is_maximized()
        return any_maximized

    def restore_split(self):
        return None

    def backup_split(self):
        return None

    def set_window_active(self, calling_child):
        self.parent.set_window_active(calling_child)

