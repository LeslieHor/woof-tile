from window_group import WindowGroup
from node import Node
from screen import Screen
import system_calls
from config import *
from log import log_info, log_debug, log_warning, log_error
from enums import *


class Window:
    """Leaf node, representing a viewable window"""

    def __init__(self, window_id, woof_id):
        self.window_id = window_id
        self.woof_id = woof_id
        self.state = WINDOW_STATE.NORMAL

        self.window_class = system_calls.get_window_class(self.window_id)
        self.parent = None

    def debug_print(self, level=0):
        l, d, u, r = self.get_size()
        borders = str(l) + ", " + str(d) + ", " + str(u) + ", " + str(r)
        print(str(DEBUG_SPACER * level) + "Woof ID: " + str(self.woof_id)) + " Borders: " + borders

        return 1

    def get_debug_print(self, level=0):
        window_title = self.get_window_title()

        if self.state == WINDOW_STATE.NORMAL:
            state = 'Normal'
        elif self.state == WINDOW_STATE.MINIMIZED:
            state = 'Minimized'
        elif self.state == WINDOW_STATE.MAXIMIZED:
            state = 'Maximized'
        elif self.state == WINDOW_STATE.SHADED:
            state = 'Shaded'
        else:
            state = 'Unknown'

        if isinstance(self.parent, WindowGroup):
            parent_type = "WindowGroup"
        elif isinstance(self.parent, Node):
            parent_type = "Node"
        elif isinstance(self.parent, Screen):
            parent_type = "Screen"
        else:
            parent_type = 'Unknown'

        string = ''
        string += str((DEBUG_SPACER * level)) + 'Woof ID: ' + str(self.woof_id) + '\n'
        string += str((DEBUG_SPACER * level)) + 'Window ID: ' + str(self.window_id) + '\n'
        string += str((DEBUG_SPACER * level)) + 'Window Title: ' + window_title + '\n'
        string += str((DEBUG_SPACER * level)) + 'State: ' + state + '\n'
        string += str((DEBUG_SPACER * level)) + 'Class: ' + self.window_class + '\n'
        string += str((DEBUG_SPACER * level)) + 'Parent Type: ' + parent_type + '\n'

        return string

    def get_window_title(self):
        return system_calls.get_window_title(self.window_id)

    def get_size(self):
        """Get the size of the current window

        This is not necessarily the actual window size in the WM. Just the size
        the tree thinks the window should be.
        """
        return self.parent.get_borders(self)

    def get_window_class(self):
        if self.window_class is None:
            self.window_class = system_calls.get_window_class(self.window_id)
        return self.window_class

    def edges_to_margs(self, l, d, u, r):
        lc, dc, uc, rc = self.border_class_corrections()

        # Corrected coordinates:
        l = l + lc
        d = d + dc
        u = u + uc
        r = r + rc

        px = l
        py = u
        sx = r - l
        sy = d - u

        return px, py, sx, sy

    def border_class_corrections(self):
        if self.window_class in BORDER_CLASS_CORRECTIONS:
            return BORDER_CLASS_CORRECTIONS[self.window_class]
        else:
            return DEFAULT_BORDER_CORRECTIONS

    def set_size_override(self, px, py, sx, sy):
        """Call into the WM to resize the window"""
        system_calls.set_window_geometry(self.window_id, px, py, sx, sy)

    def set_size(self):
        """Set the window location / size"""
        l, d, u, r = self.get_size()
        px, py, sx, sy = self.edges_to_margs(l, d, u, r)
        self.set_size_override(px, py, sx, sy)
        self.state = WINDOW_STATE.NORMAL

    def split(self, new_window, plane_type, direction):
        """Request the parent to split to add a new window"""
        log_debug(["Parent is node: ", str(isinstance(self.parent, Node))])
        self.parent.split(self, new_window, plane_type, direction)

    def resize_vertical(self, _caller_child, increment):
        """Request parent to resize window."""
        if not self.parent.resize_vertical(self, increment):
            log_debug(['Unable to resize. Using alternative'])
            next_child = self.parent.find_earliest_a_but_not_me(self)
            if next_child is not None:
                if not self.parent.all_are_bees(self):
                    log_debug(['All are not bees'])
                    increment *= -1
                elif self.parent.get_plane_type() == PLANE.HORIZONTAL:
                    increment *= -1
                next_child.resize_vertical(self, increment)

    def resize_horizontal(self, _caller_child, increment):
        if not self.parent.resize_horizontal(self, increment):
            log_debug(['Unable to resize. Using alternative'])
            next_child = self.parent.find_earliest_a_but_not_me(self)
            if next_child is not None:
                if not self.parent.all_are_bees(self):
                    log_debug(['All are not bees'])
                    increment *= -1
                elif self.parent.get_plane_type() == PLANE.VERTICAL:
                    increment *= -1
                next_child.resize_horizontal(self, increment)

    def change_plane(self):
        """Request parent to change plane orientation"""
        self.parent.change_plane()

    def swap_pane_position(self):
        """Request parent to swap self and sibling positions"""
        self.parent.swap_pane_position()
        self.parent.set_size()

    def replace_child(self, new_child):
        """Request parent to replace self with a new child"""
        self.parent.replace_child(self, new_child)

    def kill_window(self):
        """Request parent to kill self (this window)"""
        return self.parent.kill_window(self)

    def minimize(self):
        """Call into WM to minimize the window"""
        system_calls.minimise_window(self.window_id)
        self.state = WINDOW_STATE.MINIMIZED

    def activate(self, set_last_active=False):
        """Call into WM to focus the window"""
        if set_last_active:
            self.parent.set_window_active(self)
        system_calls.activate_window(self.window_id)

    def list_screen_windows(self):
        """Request parent to list all their windows

        This will ripple into the root screen, return a list of all windows on
        the screen
        """
        return self.parent.list_screen_windows()

    def window_ids(self):
        """Return window ID in a single-item list"""
        return [self.window_id]

    def maximize(self):
        """Set size of window as if this were the only window on the screen"""
        self.state = WINDOW_STATE.MAXIMIZED
        l, d, u, r = self.parent.get_screen_borders()
        px, py, sx, sy = self.edges_to_margs(l, d, u, r)
        self.set_size_override(px, py, sx, sy)

    def remove_wm_maximize(self):
        """Remove WM maximization status

        WM maximization status can interfere with resizing
        """
        system_calls.remove_system_maximize(self.window_id)

    def list_add_window(self, prepend=''):
        """List the current window name, pre-pending a given string

        This is used to list windows in rofi
        """
        window_name = system_calls.get_window_title(self.window_id)
        return prepend + str(self.woof_id) + " : " + window_name

    def get_state(self):
        return system_calls.get_window_state(self.window_id)

    def is_minimized(self):
        return self.state == WINDOW_STATE.MINIMIZED

    def is_shaded(self):
        return self.state == WINDOW_STATE.SHADED

    def shade(self):
        if self.state == WINDOW_STATE.SHADED:
            return
        system_calls.shade_window(self.window_id)
        self.state = WINDOW_STATE.SHADED

    def unshade(self):
        if self.state == WINDOW_STATE.NORMAL:
            return
        system_calls.unshade_window(self.window_id)
        self.state = WINDOW_STATE.NORMAL

    def get_screen_index(self):
        return self.parent.get_screen_index(self)

    def get_window_list(self):
        return [self]

    def get_available_window_list(self):
        return [self]

    def is_maximized(self):
        return self.state == WINDOW_STATE.MAXIMIZED

    def is_any_maximized(self):
        return self.is_maximized()

    def restore_split(self):
        return None

    def backup_split(self):
        return None
