#!/usr/bin/python

import subprocess  # For calling into the system
import pickle  # For saving the window structure to disk
import sys  # For getting args
import time  # For calculating acceleration when resizing windows


class DIR:
    """Enum for directions"""
    LEFT = 0
    DOWN = 1
    UP = 2
    RIGHT = 3


class PLANE:
    """Enum for plane directions"""
    HORIZONTAL = 0
    VERTICAL = 1


class WorkSpace:
    """Root of all tree structures"""

    def __init__(self, desktop_count, screens_count, horizontal_res, vertical_res):
        self.desktops_count = desktop_count
        self.desktops = []

        for _desktop in range(self.desktops_count):
            new_desktop = Desktop(screens_count, horizontal_res, vertical_res)
            self.desktops.append(new_desktop)

    def debug_print(self):
        print("WorkSpace")
        window_counter = 0
        for desktop in self.desktops:
            window_counter += desktop.debug_print(1)
        return window_counter


class Desktop:
    """Container for all screens for a particular desktop

    Automatically constructs screen limits and stores a list of screens

    # TODO: Allow any even grid-based layout e.g. 1x3, 2x2, 3x2 etc.
    """

    def __init__(self, screens_count, horizontal_res, _vertical_res):
        self.screens_count = screens_count
        self.screens = []

        screen_horizontal_res = horizontal_res / self.screens_count
        left_limit = 0
        for right_limit in range(screen_horizontal_res, horizontal_res + screen_horizontal_res, screen_horizontal_res):
            new_screen = Screen(left_limit, 1080, 0, right_limit)
            left_limit = right_limit
            self.screens.append(new_screen)

    def debug_print(self, level):
        print("\t" * level + "Desktop")
        window_counter = 0
        for screen in self.screens:
            window_counter += screen.debug_print(level + 1)
        return window_counter

    def which_screen(self, left_pixel):
        """Returns the screen index the given pixel belongs to
        # TODO Should work for grid-based layouts
        """
        screen_index = 0
        for screen in self.screens:
            if screen.left <= left_pixel < screen.right:
                return screen
            screen_index += 1
        return screen_index


class Screen:
    def __init__(self, left, down, up, right):
        self.left = left
        self.down = down
        self.up = up
        self.right = right

        self.child = None

    def debug_print(self, level):
        print("\t" * level + "Screen")
        if self.child is not None:
            return self.child.debug_print(level + 1)
        else:
            return 0

    def get_borders(self, _caller_child):
        return self.left, self.down, self.up, self.right

    def initialise(self, new_window):
        """Initialise a screen with a window

        Screens always start empty. You can't initialise with a node as the
        node will only have one window. So you initialise with a window to
        start with.
        """
        self.child = new_window
        self.child.parent = self
        self.child.set_size()

    def split(self, caller_child, new_window, plane_type, direction):
        """Split screen by adding a node

        When a second window is added to a screen, we need to initialise a
        node to store the two windows.
        """
        new_node = Node(plane_type)
        new_node.parent = self
        new_node.set_split_default()

        if direction == DIR.DOWN or direction == DIR.RIGHT:
            new_node.child_a = caller_child
            new_node.child_b = new_window
        else:
            new_node.child_a = new_window
            new_node.child_b = caller_child

        new_node.child_a.parent = new_node
        new_node.child_b.parent = new_node

        self.child = new_node
        self.child.set_size()

    """Calculates correct gap size

    Gap size for the screen borders are full sized. We add 1 to allow a
    gap size of 1 pixel. Which results in a 1 pixel gap between the
    screen borders and the window, and a 2 pixel gap between windows.

    Gap size between windows are half-size as the other window will have
    the same sized gap.
    """

    def gap_correct_left(self, left):
        if left != self.left:
            return (GAP + 1) / 2
        return GAP

    def gap_correct_down(self, down):
        if down != self.down:
            return (GAP + 1) / 2
        return GAP

    def gap_correct_up(self, up):
        if up != self.up:
            return (GAP + 1) / 2
        return GAP

    def gap_correct_right(self, right):
        if right != self.right:
            return (GAP + 1) / 2
        return GAP

    """Deny resizing if request reaches the screen

    You cannot resize the screen itself.
    """

    @staticmethod
    def resize_vertical(_caller_child, _increment):
        return False

    @staticmethod
    def resize_horizontal(_caller_child, _increment):
        return False

    def kill_window(self, caller_child):
        """Reset pointer to child to None
        Return an empty string, as we don't want to activate any particular window, since the call must've come from
        the only window on the screen (i.e. This screen only had one window in it)
        """
        if caller_child != self.child:
            return False
        self.child = None

        return ""

    def replace_child(self, caller_child, new_child):
        """Replace current child with a new one.

        Only accept if the call came from the current child.
        """
        if caller_child != self.child:
            return False
        self.child = new_child

    def set_size(self, _reset_default=False):
        """Request that the child resize itself

        ResetDefault is unused.
        """
        self.child.set_size()

    def list_screen_windows(self):
        """Request that the child return a list of window ids"""
        return self.child.window_ids()

    def get_screen_borders(self):
        """Return screen border coordinates
        # TODO: This is a duplicate of get_borders(). Pick one.
        """
        return self.left, self.down, self.up, self.right

    # TODO: Refactor function name
    @staticmethod
    def all_are_bees(_caller_child):
        """If call has gotten to this point, all children to this point must have been 'ChildB'
        So just return true
        """
        return True

    # TODO: Refactor function name
    @staticmethod
    def find_earliest_a_but_not_me(_caller_child):
        """If call has gotten to this point, we could not find a 'ChildA' that was not part of the calling stack"""
        return None


class Node:
    """Node of the tree

    Contains two children, which can be nodes or children.
    PlaneType defines whether the node is split horizontally or vertically
    """

    def __init__(self, plane_type):
        self.plane_type = plane_type

        self.parent = None
        self.child_a = None
        self.child_b = None

    def debug_print(self, level):
        if self.plane_type == PLANE.HORIZONTAL:
            plane_type_str = "H"
        else:
            plane_type_str = "V"
        l, d, u, r = self.parent.get_borders(self)
        print("\t" * level + "N (" + plane_type_str + ") " + str(self.split) + " " + str(l) + "," + str(d) + "," + str(
            u) + "," + str(r))

        window_counter = 0
        window_counter += self.child_a.debug_print(level + 1)
        window_counter += self.child_b.debug_print(level + 1)

        return window_counter

    def set_split_default(self):
        """Sets split to 50% of the node's assigned area"""
        l, d, u, r = self.parent.get_borders(self)

        # TODO: self.split is not defined in __init__. Make it so.
        if self.plane_type == PLANE.VERTICAL:
            self.split = (l + r) / 2
        else:
            self.split = (u + d) / 2

    def split(self, caller_child, new_window, plane_type, direction):
        """Alter tree to add a new window

        When a child window requests a split, the parent creates a new node
        to replace the child with.

        E.g.
        Node
         |
         +--> Window A
         |
         +--> Window B

        Window B requests split to add Window C

        Node
         |
         +--> Window A
         |
         +--> Node
               |
               +--> Window B
               |
               +--> Window C
        """
        new_node = Node(plane_type)
        new_node.parent = self

        # The calling child is the one to become the new node.
        if caller_child == self.child_a:
            self.child_a = new_node
        else:
            self.child_b = new_node

        new_node.set_split_default()

        if direction == DIR.DOWN or direction == DIR.RIGHT:
            new_node.child_a = caller_child
            new_node.child_b = new_window
        else:
            new_node.child_a = new_window
            new_node.child_b = caller_child

        new_node.child_a.parent = new_node
        new_node.child_b.parent = new_node

        # Force both children to resize
        # TODO: Only need to force the calling child to resize. []
        self.child_a.set_size()
        self.child_b.set_size()

    def get_borders(self, caller_child):
        """Returns borders for the calling child

        E.g.
              Split
                |
                |
                V
        +-------+--------+
        |       |        |
        |       |        |
        |   A   |   B    |
        |       |        |
        |       |        |
        +-------+--------+

        Child A only gets borders up to the split
        """
        left, down, up, right = self.parent.get_borders(self)

        if caller_child == self.child_a:
            if self.plane_type == PLANE.HORIZONTAL:
                down = self.split
            else:
                right = self.split
        else:
            if self.plane_type == PLANE.HORIZONTAL:
                up = self.split
            else:
                left = self.split

        return left, down, up, right

    """Ripple gap correction requests up to the root screen"""

    def gap_correct_left(self, l):
        return self.parent.gap_correct_left(l)

    def gap_correct_down(self, d):
        return self.parent.gap_correct_down(d)

    def gap_correct_up(self, u):
        return self.parent.gap_correct_up(u)

    def gap_correct_right(self, r):
        return self.parent.gap_correct_right(r)

    def set_size(self, reset_default=False):
        """Force both children to resize

        ResetDefault. If true, resets the split to 50%
        """
        if reset_default:
            self.set_split_default()

        self.child_a.set_size(reset_default)
        self.child_b.set_size(reset_default)

    def resize_vertical(self, caller_child, increment):
        """Resize calling child window / node

        If the calling child is child A, simply move the split to give more
        space to child A.
        Otherwise, ripple the request to the parent, to see if they can resize


        # TODO: Possible to use a single function to do this?
        """
        if self.plane_type != PLANE.HORIZONTAL:
            return self.parent.resize_vertical(self, increment)
        if caller_child == self.child_b:
            return self.parent.resize_vertical(self, increment)

        self.split += increment
        self.set_size()
        return True

    def resize_horizontal(self, caller_child, increment):
        if self.plane_type != PLANE.VERTICAL:
            return self.parent.resize_horizontal(self, increment)
        if caller_child == self.child_b:
            return self.parent.resize_horizontal(self, increment)

        self.split += increment
        self.set_size()
        return True

    def all_are_bees(self, caller_child):
        """If the calling child is 'ChildB', ripple the call up to check if THIS caller is also ChildB'
        Returns True if the entire call stack up to the screen are all 'ChildB's.
        Returns False if any along the call stack are 'ChildA'
        """
        if caller_child == self.child_b:
            return self.parent.all_are_bees(self)
        return False

    def find_earliest_a_but_not_me(self, caller_child):
        """Returns the earliest (deepest in the tree, but above the caller) 'ChildA' that is not part of the call
        stack
        """
        if caller_child == self.child_a:
            return self.parent.find_earliest_a_but_not_me(self)
        return self.child_a

    def get_child_a(self):
        """Return 'ChildA'"""
        return self.child_a

    def change_plane(self):
        """Swap the direction of the split

        In doing so, also force all sub-windows to resize to 50% of their node.
        This is due to the potentially extremely drastic layout changes that
        can occur when changing the plane.
        """
        if self.plane_type == PLANE.VERTICAL:
            plane_type = PLANE.HORIZONTAL
        else:
            plane_type = PLANE.VERTICAL

        self.plane_type = plane_type
        self.set_size(True)

    def swap_pane_position(self):
        """Swap the positions of the children"""
        self.child_a, self.child_b = self.child_b, self.child_a
        self.set_size()

    def replace_child(self, caller_child, new_child):
        """Replace the calling child with a new child
        # TODO: Should we handle resizing here?
        """
        if caller_child == self.child_a:
            self.child_a = new_child
        else:
            self.child_b = new_child

    def kill_window(self, caller_child):
        """Remove a window from the tree

        Removing a window leaves this node with only a single valid child. So,
        this must be fixed by removing this node from the tree and replacing
        it with the remaining window.

        Note: Python GC should take care of removing the node from memory. And
        since we are pickling, there should be no leftover nodes / windows.
        """
        if caller_child == self.child_a:
            surviving_child = self.child_b
        else:
            surviving_child = self.child_a

        self.parent.replace_child(self, surviving_child)
        surviving_child.parent = self.parent

        self.parent.set_size()

        return ""

    def list_screen_windows(self):
        """Request the parent to list all their windows (including yourself)"""
        return self.parent.list_screen_windows()

    def window_ids(self):
        """Request all children to return a list of windows and concat them"""
        return self.child_a.window_ids() + self.child_b.window_ids()

    def get_screen_borders(self):
        """Ripple screen border request to parent"""
        return self.parent.get_screen_borders()

    def get_plane_type(self):
        """Return PlaneType"""
        return self.plane_type


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
        print("\t" * level + "WG WinCount: " + str(len(self.all_windows)) + ". Active: " + str(
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

    def set_size(self, _resize_default=False):
        """Sets the size of the tabs and active window
        Implemented separately from the normal set_size due to
        having to calculate shaded sizes.

        # TODO: Decide if you want the gap appearing between tabs or not. Currently gaps appear.
        """
        for i in range(len(self.inactive_windows)):
            inactive_window = self.inactive_windows[i]
            log_debug(['Shading window', inactive_window.WindowIdDec])
            l, d, u, r = self.get_shaded_size(i)
            px, py, sx, sy = inactive_window.border_gap_correct(l, d, u, r)
            inactive_window.set_size_override(px, py, sx, sy)
            inactive_window.shade()

        active_window = self.active_window
        l, d, u, r = self.parent.get_borders(self)
        px, py, sx, sy = active_window.border_gap_correct(l, d, u, r)
        py += SHADED_SIZE
        sy -= SHADED_SIZE
        active_window.set_size_override(px, py, sx, sy)
        active_window.unshade()

    def activate_active_window(self):
        """Activates whatever window is currently defined as active"""
        log_debug(['Activating active window'])
        self.set_size()
        self.active_window.activate()

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

    def get_borders(self, _calling_child):
        """Returns borders of the current pane"""
        return self.parent.get_borders(self)

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
            log_debug(['Removed calling child:', caller_child.WindowIdDec])
            log_debug(['AllWindows length:', len(self.all_windows)])
            surviving_child = self.all_windows[0]
            log_debug(['SurvivingChild:', surviving_child.WindowIdDec])
            self.parent.replace_child(self, surviving_child)
            log_debug(['Replacing parent child with surviving child'])
            surviving_child.parent = self.parent
            log_debug(['Replacing child parent with windowgroup parent'])
            surviving_child.unshade()
            surviving_child.set_size()
            return str(surviving_child.WindowIdDec)
        else:
            self.all_windows.remove(caller_child)
            self.activate_next_window(0)
            return str(self.active_window.WindowIdDec)

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
        for Win in self.all_windows:
            window_ids.append(Win.WindowIdDec)
        return window_ids

    def get_screen_borders(self):
        return self.parent.get_screen_borders()


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

        print("\t" * level + "WindowID: " + str(self.window_id_dec) + ": " + call(
            ['xdotool getwindowname', self.window_id_dec]).rstrip()[
                                                                             :20] + ". Class: " + self.get_window_class() + ". Parent Type: " + parent_type)
        return 1

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

    def activate(self):
        """Call into WM to focus the window"""
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


class Windows:
    """Stores and manages the workspaces and windows

    Contains pointer to workspace and a dictionary of windows ID --> Window Object
    """

    def __init__(self, desktop_count, screens_count, res_horz, res_vert):
        self.work_space = WorkSpace(desktop_count, screens_count, res_horz, res_vert)
        self.windows = {}
        self.last_resize_ts = 0

    def debug_print(self):
        print("LIST")
        print("----")
        for _win_id, win in self.windows.iteritems():
            print("-" * 40)
            win.debug_print(0)
            if win.is_shaded():
                print("Window is shaded")
            else:
                print("Window is not shaded")

        print()
        print("TREE")
        print("----")
        windows_in_tree = self.work_space.debug_print()

        print()
        print("----")
        print("Windows in list: " + str(len(self.windows)))
        print("Windows in tree: " + str(windows_in_tree))

    def update_resize_ts(self):
        """Updates timing variable for resizing
        Returns normal resize increment if last resize was beyond the timing period
        If within the timing period, returns the rapid resizing increment
        """
        now = time.time() * 1000
        ri = RESIZE_INCREMENT
        if (now - self.last_resize_ts) < RESIZE_RAPID_TIME:
            ri = RAPID_INCREMENT
        self.last_resize_ts = now
        return ri

    def add_window(self, window):
        """Add the window the dictionary"""
        new_window_id = window.window_id_dec
        self.windows[new_window_id] = window

    def get_window(self, window_id):
        """Return the window object of the given ID"""
        return self.windows[window_id]

    def kill_window(self, window_id):
        """Request the window to kill itself and remove from dictionary"""
        window = self.windows[window_id]
        next_active_window = window.kill_window()
        del self.windows[window_id]
        return next_active_window

    def swap_windows(self, target_id):
        """Given a window id, swap the active and target positions in the tree
        # TODO: This really should work even in the same pane. Fix it and use this to
        # TODO: do the swap pane positions thing
        """
        if not self.exists() or not self.exists(target_id):
            return False

        window_id_a = self.get_active_window()
        window_id_b = target_id

        window_a = self.windows[window_id_a]
        window_b = self.windows[window_id_b]

        window_a.replace_child(window_b)
        window_b.replace_child(window_a)

        window_a.parent, window_b.parent = window_b.parent, window_a.parent

        window_a.set_size()
        window_b.set_size()

        # If the swapped window(s) were maximized, re-maximize them after
        # the swap
        if window_a.Maximized:
            main(['', 'maximize', window_a.WindowIdDec])
        if window_b.Maximized:
            main(['', 'maximize', window_b.WindowIdDec])

    def restore_all(self):
        """Unminimize and unmaximize all windows

        Restores all windows to their intended positions
        """
        self.unminimize_all()
        for _window_id, window in self.windows.iteritems():
            window.Maximized = False
            if isinstance(window.parent, WindowGroup):
                window.parent.set_size()
            else:
                window.set_size()

    def check_windows(self):
        """Checks that all windows in the dictionary are still alive

        Removes dead windows and fixes the tree.
        Return True if any windows had to be removed

        # TODO: Temp fixes really should not be here
        """
        hex_ids_str = call('wmctrl -l | awk -F" " \'$2 == 0 {print $1}\'')
        hex_ids = hex_ids_str.split("\n")
        dec_ids = [int(X, 0) for X in hex_ids if X != '']
        fix = False
        window_ids_to_kill = []
        for WinId, _Win in self.windows.iteritems():
            if WinId not in dec_ids:
                window_ids_to_kill.append(WinId)
                fix = True
            else:
                # TEMP FIXES
                None
        for WinId in window_ids_to_kill:
            self.kill_window(WinId)

        return fix

    def list_add_windows(self, prepend, exclude_active=False):
        """Generate a formatted list of windows

        For listing windows in rofi.

        Generates a list of all windows in the tree, with a prepended string.
        Empty screens are also returned in the list.
        """
        window_list = []
        active_window = None
        if exclude_active:
            active_window = self.windows[self.get_active_window()]

        for _WinId, Win in self.windows.iteritems():
            if (not Win.is_shaded()) and (not Win == active_window):
                window_list.append(Win.list_add_window(prepend))

        window_list.sort()
        counter = 0
        for screen in self.work_space.desktops[0].screens:
            if screen.child is None:
                window_list.append(prepend + "Screen " + str(counter))
            counter += 1
        return "\n".join(window_list)

    def list_windows(self):
        """Return a sorted list of all Window ids in the dictionary"""
        window_list = []
        for win_id, _win in self.windows.iteritems():
            window_list.append(win_id)
        window_list.sort()
        return window_list

    def exists(self, win_id=None):
        """Check if a list if already in the dictionary"""
        if win_id is None:
            win_id = self.get_active_window()
        return win_id in self.list_windows()

    def minimize_all(self):
        """Minimize all windows"""
        for _Key, Win in self.windows.iteritems():
            Win.minimize()

    def resize_vertical(self, expand_or_reduce, increment=None):
        win_id = self.get_active_window()
        log_debug(['Active Window ID:', win_id])
        if not self.exists(win_id):
            log_warning(['Window does not exist, exiting.'])
            return False

        if increment is None:
            increment = self.update_resize_ts()

        log_debug(['Resize increment:', increment])
        if expand_or_reduce == 'reduce':
            log_debug(['Reduce size detected. Inverting increment'])
            increment *= -1

        self.windows[win_id].resize_vertical(self, increment)

    def resize_horizontal(self, expand_or_reduce, increment=None):
        win_id = self.get_active_window()
        log_debug(['Active Window ID:', win_id])
        if not self.exists(win_id):
            log_warning(['Window does not exist, exiting.'])
            return False

        if increment is None:
            increment = self.update_resize_ts()

        log_debug(['Resize increment:', increment])
        if expand_or_reduce == 'reduce':
            log_debug(['Reduce size detected. Inverting increment'])
            increment *= -1

        self.windows[win_id].resize_horizontal(self, increment)

    def change_plane(self):
        if not self.exists():
            return False
        self.windows[self.get_active_window()].change_plane()

    def swap_pane_position(self):
        if not self.exists():
            return False
        self.windows[self.get_active_window()].swap_pane_position()

    def unminimize_all(self):
        """Unminimize all windows

        Because we need to unminimize by activating the window, window focus
        will be overwritten. Windows are not restored to their intended
        positions
        """
        active_win_id = self.get_active_window()
        for _Key, Win in self.windows.iteritems():
            Win.activate()
            Win.Maximized = False

        # We active the window through a call, in case it is not in the tree
        call(['xdotool windowactivate', active_win_id])

    def activate_window(self, win_id):
        self.windows[win_id].activate()

    def get_active_window(self):  # Really should be called get_active_window_id
        """Get ID of current active window"""
        return int(call('xdotool getactivewindow').rstrip())

    def add_to_window(self, plane_type, direction, target_id):
        new_window_id = self.get_active_window()
        new_window = Window(new_window_id)
        new_window.remove_wm_maximize()

        target_id = int(target_id)
        if not self.exists(target_id):
            return False

        self.windows[target_id].split(new_window, plane_type, direction)

        self.add_window(new_window)

    def add(self, plane_type, direction, target_id, screen_index=None):
        new_window_id = self.get_active_window()
        if self.exists(new_window_id):
            return False

        new_window = Window(new_window_id)
        new_window.remove_wm_maximize()

        if target_id == 'Screen':
            try:
                screen_index = int(screen_index)
            except:
                return False

            screen = self.work_space.desktops[0].screens[screen_index]
            if screen.child is not None:
                return False
            screen.initialise(new_window)
        else:
            target_id = int(target_id)
            if not self.exists(target_id):
                return False

            self.windows[target_id].split(new_window, plane_type, direction)

        self.add_window(new_window)

    def nav_left(self):
        win_id = self.get_active_window()
        if not self.exists():
            return False
        l, _, t, _ = self.windows[win_id].get_size()
        closest_right_border = 0
        lowest_top_diff = sys.maxint
        closest_window = None

        for _win_id, win in self.windows.iteritems():
            if win.is_shaded() or win.is_minimized():
                continue

            _, _, wt, wr = win.get_size()

            if l < wr:  # Current window is to the right of Win
                continue

            if wr < closest_right_border:
                continue

            top_border_diff = (t - wt) ** 2  # Magnitude of diff
            if lowest_top_diff < top_border_diff:
                continue

            closest_right_border = wr
            lowest_top_diff = top_border_diff
            closest_window = win

        if closest_window is None:
            log_debug(['No valid window found'])
            return
        log_debug(['Closest left window:', closest_window.list_add_window()])
        closest_window.activate()

    def nav_right(self):
        win_id = self.get_active_window()
        if not self.exists():
            return False
        _, _, t, r = self.windows[win_id].get_size()
        closest_left_border = sys.maxint
        lowest_top_diff = sys.maxint
        closest_window = None

        for _win_id, win in self.windows.iteritems():
            if win.is_shaded() or win.is_minimized():
                continue

            wl, _, wt, _ = win.get_size()

            if wl < r:  # Current window is to the left of Win
                continue

            if closest_left_border < wl:
                continue

            top_border_diff = (t - wt) ** 2  # Magnitude of diff
            if lowest_top_diff < top_border_diff:
                continue

            closest_left_border = wl
            lowest_top_diff = top_border_diff
            closest_window = win

        if closest_window is None:
            log_debug(['No valid window found'])
            return
        log_debug(['Closest right window:', closest_window.list_add_window()])
        closest_window.activate()

    def nav_up(self):
        win_id = self.get_active_window()
        if not self.exists():
            return False
        l, _, t, _ = self.windows[win_id].get_size()
        closest_bottom_border = 0
        lowest_left_diff = sys.maxint
        closest_window = None

        for _win_id, win in self.windows.iteritems():
            if win.is_shaded() or win.is_minimized():
                continue

            wl, wb, _, _ = win.get_size()

            if t < wb:  # Current window is to the bottom of Win
                continue

            if wb < closest_bottom_border:
                continue

            left_border_diff = (l - wl) ** 2  # Magnitude of diff
            if lowest_left_diff < left_border_diff:
                continue

            closest_bottom_border = wb
            lowest_left_diff = left_border_diff
            closest_window = win

        if closest_window is None:
            log_debug(['No valid window found'])
            return
        log_debug(['Closest top window:', closest_window.list_add_window()])
        closest_window.activate()

    def nav_down(self):
        win_id = self.get_active_window()
        if not self.exists():
            return False
        l, b, _, _ = self.windows[win_id].get_size()
        closest_top_border = sys.maxint
        lowest_left_diff = sys.maxint
        closest_window = None

        for _win_id, win in self.windows.iteritems():
            if win.is_shaded() or win.is_minimized():
                continue

            wl, _, wt, _ = win.get_size()

            if wt < b:  # Current window is to the bottom of Win
                continue

            if closest_top_border < wt:
                continue

            left_border_diff = (l - wl) ** 2  # Magnitude of diff
            if lowest_left_diff < left_border_diff:
                continue

            closest_top_border = wt
            lowest_left_diff = left_border_diff
            closest_window = win

        if closest_window is None:
            log_debug(['No valid window found'])
            return
        log_debug(['Closest top window:', closest_window.list_add_window()])
        closest_window.activate()

    def add_to_window_group(self, target_id):
        win_id = self.get_active_window()
        target_id = int(target_id)
        if self.exists(win_id) or not self.exists(target_id):
            log_debug(['Active window exists, or target window does not exist'])
            return False

        new_window = Window(win_id)
        target_win = self.windows[target_id]
        node_parent = target_win.parent
        if isinstance(node_parent, WindowGroup):
            new_window.parent = node_parent
            node_parent.add_window(new_window)
        else:  # Create new window group
            new_window_group = WindowGroup(node_parent, new_window, [target_win])

            node_parent.replace_child(target_win, new_window_group)

            new_window.parent = new_window_group
            target_win.parent = new_window_group

            new_window_group.activate_active_window()

        self.add_window(new_window)

    def activate_next_window(self, increment):
        win_id = self.get_active_window()
        if not self.exists(win_id):
            log_debug(['Window doesn\'t exist'])
            return False
        window = self.get_window(win_id)
        if not isinstance(window.parent, WindowGroup):
            log_debug(['Window not in window group'])
            return False

        window.parent.activate_next_window(increment)


# TODO: All of these functions should be moved to Windows
def join_and_sanitize(list_):
    """Join a list of items into a single string"""
    if isinstance(list_, str):
        return list_

    new_list = []
    for item in list_:
        if isinstance(item, str):
            new_list.append(item)
            continue
        elif isinstance(item, int):
            new_list.append(str(item))
            continue
        else:
            raise Exception('Invalid type when attempting to join and santize')

    return ' '.join(new_list)


def call(command):
    """Call into the system and run Command (string)"""
    cmd = join_and_sanitize(command)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    result, _err = proc.communicate()

    return result


def mouse_select_window():
    """Extract window id using mouse to select window"""
    return int(call('xdotool selectwindow').rstrip())


def debug_print():
    WINDOWS_OBJ.debug_print()


def dir_str_to_plane_dir(direction):
    if direction == 'h':
        return dir_str_to_plane_dir('r')
    elif direction == 'v':
        return dir_str_to_plane_dir('d')

    elif direction == 'l':
        return PLANE.VERTICAL, DIR.LEFT
    elif direction == 'd':
        return PLANE.HORIZONTAL, DIR.DOWN
    elif direction == 'u':
        return PLANE.HORIZONTAL, DIR.UP
    elif direction == 'r':
        return PLANE.VERTICAL, DIR.RIGHT
    else:
        return False


def element(list_, index, default):
    try:
        return list_[index]
    except:
        return default


def log_info(log_list):
    log(['[INFO]'] + log_list)


def log_debug(log_list):
    log(['[DEBUG]'] + log_list)


def log_warning(log_list):
    log(['[WARN]'] + log_list)


def log_error(log_list):
    log(['[ERROR]'] + log_list)


def log(log_list):
    string = join_and_sanitize(log_list) + '\n'
    timestamp = time.strftime('%Y-%m-%dT%H:%M:%S ', time.gmtime())
    string = timestamp + string
    with open(LOG_PATH, 'a') as LogFile:
        LogFile.write(string)


def main(args):
    cmd = args[1]
    log_info(['------- Start --------', 'Args:'] + args[1:])
    if cmd == 'debug':
        debug_print()
    elif cmd == 'restore':
        WINDOWS_OBJ.restore_all()
    elif cmd == 'list':
        print(WINDOWS_OBJ.list_add_windows(args[2]))
    elif cmd == 'add':
        # Adding to a window : "add h 32478239 : window title"
        # Adding to a screen : "add h Screen 1"
        plane = element(args, 2, None)
        target_id = element(args, 3, None)
        screen_index = element(args, 4, None)

        if target_id is None:
            log_debug(['No target id. Listing windows.'])
            print(WINDOWS_OBJ.list_add_windows("add " + plane + " "))
            return

        log_debug(['Target ID found. TargetId:', target_id])
        if target_id == 'Screen':
            log_debug(['Detected screen add. Screen Index:', screen_index])
        else:
            log_debug(['Not a screen add'])

        plane_type, direction = dir_str_to_plane_dir(plane)

        WINDOWS_OBJ.add(plane_type, direction, target_id, screen_index)
    elif cmd == 'ev':
        increment = element(args, 2, None)
        if increment is not None:
            increment = int(increment)
        log_debug(['Attempting to expand vertical size.'])
        WINDOWS_OBJ.resize_vertical('expand', increment)
    elif cmd == 'rv':
        log_debug(['Attempting to reduce vertical size.'])
        increment = element(args, 2, None)
        if increment is not None:
            increment = int(increment)
        WINDOWS_OBJ.resize_vertical('reduce', increment)
    elif cmd == 'eh':
        log_debug(['Attempting to expand horizontal size.'])
        increment = element(args, 2, None)
        if increment is not None:
            increment = int(increment)
        WINDOWS_OBJ.resize_horizontal('expand', increment)
    elif cmd == 'rh':
        increment = element(args, 2, None)
        if increment is not None:
            increment = int(increment)
        log_debug(['Attempting to reduce horizontal size.'])
        WINDOWS_OBJ.resize_horizontal('reduce', increment)
    elif cmd == 'change-plane':
        WINDOWS_OBJ.change_plane()
    elif cmd == 'swap-pane':
        WINDOWS_OBJ.swap_pane_position()
    elif cmd == 'swap':
        if len(args) < 3:
            log_debug(['No target found. Listing windows'])
            print(WINDOWS_OBJ.list_add_windows("swap ", True))
            return

        target_id = int(args[2])
        WINDOWS_OBJ.swap_windows(target_id)
    elif cmd == 'min':
        WINDOWS_OBJ.minimize_all()
    elif cmd == 'unmin':
        WINDOWS_OBJ.unminimize_all()
    elif cmd == 'maximize':
        if len(args) > 2:
            win_id = int(args[2])
        else:
            win_id = WINDOWS_OBJ.get_active_window()
        if not WINDOWS_OBJ.exists(win_id):
            exit(1)
        win_ids = WINDOWS_OBJ.windows[win_id].list_screen_windows()
        if WINDOWS_OBJ.windows[win_id].Maximized:
            for win_id in win_ids:
                WINDOWS_OBJ.windows[win_id].activate()
                WINDOWS_OBJ.windows[win_id].set_size()

            WINDOWS_OBJ.windows[win_id].activate()
            WINDOWS_OBJ.windows[win_id].maximized = False
        else:
            for win_id in win_ids:
                if win_id == win_id:
                    continue
                WINDOWS_OBJ.windows[win_id].minimize()
            WINDOWS_OBJ.windows[win_id].maximize()
    elif cmd == 'kill':
        win_id = WINDOWS_OBJ.get_active_window()
        if not WINDOWS_OBJ.exists(win_id):
            exit(1)
        win_id_hex = WINDOWS_OBJ.windows[win_id].WindowIdHex
        next_active_window = WINDOWS_OBJ.kill_window(win_id)
        return_string = win_id_hex + "," + str(next_active_window)
        log_debug(['ReturnString:', return_string])
        print(return_string)
    elif cmd == 'remove':
        win_id = WINDOWS_OBJ.get_active_window()
        if not WINDOWS_OBJ.exists(win_id):
            exit(1)
        WINDOWS_OBJ.kill_window(win_id)
    elif cmd == 'move-to':
        if len(args) < 3:
            log_debug(['No target id. Listing windows.'])
            print(WINDOWS_OBJ.list_add_windows("move-to ", True))
            return

        main(['', 'remove'])
        main(['', 'add', 'h', args[2]])
    elif cmd == 'nav-right':
        WINDOWS_OBJ.nav_right()
    elif cmd == 'nav-left':
        WINDOWS_OBJ.nav_left()
    elif cmd == 'nav-up':
        WINDOWS_OBJ.nav_up()
    elif cmd == 'nav-down':
        WINDOWS_OBJ.nav_down()
    elif cmd == 'add-to-group':
        if WINDOWS_OBJ.exists(WINDOWS_OBJ.get_active_window()):
            exit(1)
        if len(args) < 3:
            log_debug(['No target id. Listing windows.'])
            print(WINDOWS_OBJ.list_add_windows("add-to-group "))
            return

        target_id = args[2]
        WINDOWS_OBJ.add_to_window_group(target_id)
    elif cmd == 'activate-next-window':
        WINDOWS_OBJ.activate_next_window(1)
    elif cmd == 'activate-prev-window':
        WINDOWS_OBJ.activate_next_window(-1)

    pickle.dump(WINDOWS_OBJ, open(DATA_PATH, "wb"))


# TODO: Parameters should be defined by an actual config file
# TODO: Although it would add another IO operation...
# Some initial parameters
GAP = 10
TOP_BORDER = 25
LEFT_BORDER = 2
RIGHT_BORDER = 2
BOTTOM_BORDER = 4
SHADED_SIZE = 25

# Include border calculations for the following programs
BORDER_WHITELIST = [
    'konsole',
    'Spotify',
    'libreoffice',
    'dolphin'
]

SPECIAL_SHITS = {
    'mpv': [2, 12]
}

RESIZE_INCREMENT = 10
RAPID_INCREMENT = 80
RESIZE_RAPID_TIME = 200  # milliseconds

DEBUG = False
DATA_PATH = "~/.woof/windows.dat"
DATA_PATH = call(['readlink -f', DATA_PATH]).rstrip()  # Convert relative path to global path
LOG_PATH = "~/.woof/log/log"
LOG_PATH = call(['readlink -f', LOG_PATH]).rstrip()  # Convert relative path to global path

# TODO: Seriously, clean up this code
# Initialise a tree
if sys.argv[1] == 'reload':
    WINDOWS_OBJ = Windows(4, 3, 5760, 1080)
else:
    WINDOWS_OBJ = pickle.load(open(DATA_PATH, "rb"))
    if WINDOWS_OBJ.check_windows():
        WINDOWS_OBJ.restore_all()

ARGS = sys.argv

main(ARGS)
exit(0)
