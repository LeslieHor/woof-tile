import subprocess
from window_group import WindowGroup
from node import Node
from screen import Screen
from system_calls import call
from config import *
from log import log_info, log_debug, log_warning, log_error
from enums import *


class Window:
    """Leaf node, representing a viewable window"""

    def __init__(self, window_id):
        self.window_id_dec = window_id
        self.window_id_hex = hex(int(window_id))

        self.parent = None
        self.maximized = False

    def debug_print(self, level):
        parent_type = "unknown"
        if isinstance(self.parent, WindowGroup):
            parent_type = "WindowGroup"
        elif isinstance(self.parent, Node):
            parent_type = "Node"
        elif isinstance(self.parent, Screen):
            parent_type = "Screen"

        print(" " * level + "WindowID: " + str(self.window_id_dec) + ": " + self.get_window_title()[:20] + ". Class: " + self.get_window_class() + ". Parent Type: " + parent_type)
        return 1

    def get_window_title(self):
        return call(['xdotool getwindowname', self.window_id_dec]).rstrip()

    def get_size(self):
        """Get the size of the current window

        This is not necessarily the actual window size in the WM. Just the size
        the tree thinks the window should be.
        """
        return self.parent.get_borders(self)

    def border_multiplier(self):
        """Correct border calculations based on a whitelist

        Some programs will include window decoration as part of their coordinates
        Others will simply make the window size smaller based on the border.
        # TODO: I think this explanation is either badly written or just wrong

        Which application class does what must be defined by a whitelist.
        Whitelist defines programs that ignore borders in their calculations

        E.g.
        Intended window position
        +-Screen----------------------+
        |                             |
        |  +--------+                 |
        |  |        |                 |
        |  |        |                 |
        |  +--------+                 |
        |                             |
        |                             |
        |                             |
        +-----------------------------+

        Actual window position is above and to the left
        +-Screen----------------------+
        | +--------+                  |
        | |        |                  |
        | |        |                  |
        | +--------+                  |
        |                             |
        |                             |
        |                             |
        |                             |
        +-----------------------------+
        """
        window_class = self.get_window_class()
        for name in BORDER_WHITELIST:
            if name in window_class:
                return 1
        return 0

    def get_window_class(self):
        return call(['xprop -id', self.window_id_dec, '| grep WM_CLASS |  sed \'s/^.*, "//\' | sed \'s/"//\'']).rstrip()

    def border_gap_correct(self, l, d, u, r):
        """Calculate window size parameters taking gap and borders into account

        Given coordinates for left, bottom, top and right borders, calculates
        the following (taking into account gaps and borders):

        - Coordinate of left border
        - Coordinate of top border
        - Width of window
        - Height of window
        """
        bm = self.border_multiplier()
        lb = bm * LEFT_BORDER
        tb = bm * TOP_BORDER
        if bm == 1:
            rb = bm * RIGHT_BORDER
            bb = bm * BOTTOM_BORDER
        else:
            rb = LEFT_BORDER + RIGHT_BORDER
            bb = TOP_BORDER + BOTTOM_BORDER

        scx, scy = 0, 0
        window_class = self.get_window_class()
        if window_class in SPECIAL_SHITS:
            scx, scy = SPECIAL_SHITS[window_class][0], SPECIAL_SHITS[window_class][1]

        px = l + lb + scx + self.parent.gap_correct_left(l)
        py = u + tb + scy + self.parent.gap_correct_up(u)
        sx = r - px + scx - rb - self.parent.gap_correct_right(r)
        sy = d - py + scy - bb - self.parent.gap_correct_down(d)
        return px, py, sx, sy

    def set_size_override(self, px, py, sx, sy):
        """Call into the WM to resize the window"""
        # xdotool will not override the plasma panel border
        # wmctrl is very particular about its args
        mvarg = '0,' + str(px) + ',' + str(py) + ',' + str(sx) + ',' + str(sy)
        call(['wmctrl -ir', self.window_id_hex, '-e', mvarg])

    def set_size(self, _reset_default=False):
        """Set the window location / size"""
        if isinstance(self.parent, WindowGroup):
            self.parent.set_size()
        else:
            l, d, u, r = self.get_size()
            px, py, sx, sy = self.border_gap_correct(l, d, u, r)
            self.set_size_override(px, py, sx, sy)

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

    def replace_child(self, new_child):
        """Request parent to replace self with a new child"""
        self.parent.replace_child(self, new_child)

    def kill_window(self):
        """Request parent to kill self (this window)"""
        return self.parent.kill_window(self)

    def minimize(self):
        """Call into WM to minimize the window"""
        call(['xdotool windowminimize', self.window_id_dec])

    def activate(self, set_last_active=False):
        """Call into WM to focus the window"""
        if set_last_active:
            self.parent.set_window_active(self)
        call(['xdotool windowactivate', self.window_id_dec])

    def list_screen_windows(self):
        """Request parent to list all their windows

        This will ripple into the root screen, return a list of all windows on
        the screen
        """
        return self.parent.list_screen_windows()

    def window_ids(self):
        """Return window ID in a single-item list"""
        return [self.window_id_dec]

    def maximize(self):
        """Set size of window as if this were the only window on the screen"""
        self.maximized = True
        l, d, u, r = self.parent.get_screen_borders()
        px, py, sx, sy = self.border_gap_correct(l, d, u, r)
        self.set_size_override(px, py, sx, sy)

    def remove_wm_maximize(self):
        """Remove WM maximization status

        WM maximization status can interfere with resizing
        """
        subprocess.call(["wmctrl", "-ir", self.window_id_hex, "-b", "remove,maximized_vert,maximized_horz"])

    def list_add_window(self, prepend=''):
        """List the current window name, pre-pending a given string

        This is used to list windows in rofi
        """
        window_name = call(['xdotool getwindowname', self.window_id_dec]).rstrip()
        return prepend + str(self.window_id_dec) + " : " + window_name

    def get_state(self):
        """Gets the windows state using xprop

        States:
        <BLANK> : Normal
        _NET_WM_STATE_SHADED : Shaded
        _NET_WM_STATE_HIDDEN : Minimized

        """
        return call(['xprop', '-id', self.window_id_dec,
                     ' | grep "NET_WM_STATE" | sed \'s/_NET_WM_STATE(ATOM) = //\'']).rstrip()

    def is_minimized(self):
        return self.get_state() == "_NET_WM_STATE_HIDDEN"

    def is_shaded(self):
        return self.get_state() == "_NET_WM_STATE_SHADED"

    def shade(self):
        call(['wmctrl', '-ir', self.window_id_hex, '-b', 'add,shaded'])

    def unshade(self):
        call(['wmctrl', '-ir', self.window_id_hex, '-b', 'remove,shaded'])

    def get_screen_index(self):
        return self.parent.get_screen_index(self)

    def get_window_list(self):
        return [self]

    def get_available_window_list(self):
        return [self]

    def is_any_maximized(self):
        return self.maximized

    def restore_split(self):
        return None

    def backup_split(self):
        return None
