import time
import sys
from workspace import WorkSpace
from window_group import WindowGroup
from window import Window
import system_calls
from config import *
from log import log_info, log_debug, log_warning, log_error
from enums import WINDOW_STATE


class Windows:
    """Stores and manages the workspaces and windows

    Contains pointer to workspace and a dictionary of windows ID --> Window Object
    """

    def __init__(self, screen_config):
        self.work_space = WorkSpace(screen_config, START_SCREEN_COUNT)
        self.windows = {}
        self.last_resize_ts = 0

    def debug_print(self):
        print("LIST")
        print("----")
        for _win_id, win in self.windows.iteritems():
            print("-" * 40)
            print(win.get_debug_print(0))

        print
        print("TREE")
        print("----")
        windows_in_tree = self.work_space.debug_print()

        print
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
        new_window_id = window.window_id
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
        # if window_a.Maximized:
        #     main(['', 'maximize', window_a.WindowIdDec])
        # if window_b.Maximized:
        #     main(['', 'maximize', window_b.WindowIdDec])

    def restore_all(self):
        """Unminimize and unmaximize all windows

        Restores all windows to their intended positions
        """
        for window in self.work_space.get_viewable_windows():
            window.activate()
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
        hex_ids = system_calls.get_hex_ids()
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

    def list_add_windows(self, prepend='', exclude_active=False):
        """Generate a formatted list of windows

        For listing windows in rofi.

        Generates a list of all windows in the tree, with a prepended string.
        Empty screens are also returned in the list.
        """
        window_list = []
        active_window_id = None
        if exclude_active:
            active_window_id = self.get_active_window()

        for win in self.work_space.get_viewable_windows():
            if (not win.is_shaded()) and (not win.window_id == active_window_id):
                window_list.append(win.list_add_window(prepend))

        window_list.sort()
        counter = 0
        for viewable_screen in range(self.work_space.viewable_screen_count):
            screen_index = self.work_space.viewable_screen_index_to_index(viewable_screen)
            screen = self.work_space.screens[screen_index]
            if screen.child is None:
                window_list.append(prepend + "s" + str(counter))
            counter += 1
        return window_list

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
        # TODO: Doesn't matter, but probably should only minimize viewable windows
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
        for win in self.work_space.get_viewable_windows():
            win.activate()
            win.state = WINDOW_STATE.NORMAL

        # We active the window through a call, in case it is not in the tree
        system_calls.activate_window(active_win_id)

    def activate_window(self, win_id):
        self.windows[win_id].activate()

    def get_active_window(self):  # Really should be called get_active_window_id
        """Get ID of current active window"""
        return system_calls.get_active_window()

    def add_to_window(self, plane_type, direction, target_id):
        new_window_id = self.get_active_window()
        new_window = Window(new_window_id, self.generate_new_window_id())
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

        new_window = Window(new_window_id, self.generate_new_window_id())
        new_window.remove_wm_maximize()

        if target_id == 's':
            screen_index = int(self.work_space.viewable_screen_index_to_index(int(screen_index)))

            screen = self.work_space.screens[screen_index]
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

        for win in self.work_space.get_viewable_windows():
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

            # When two windows are equally apart. Take the to one with greater overlap
            # +------+ +-----+
            # |      | |     |
            # |  1   | +-----+
            # |      | +-----+
            # |      | |  0  |
            # +------+ +-----+
            # +------+
            # |      |
            # |      |
            # |      |
            # |      |
            # +------+
            # 0 Should switch to 1
            if lowest_top_diff == top_border_diff and t < wt:
                continue

            closest_right_border = wr
            lowest_top_diff = top_border_diff
            closest_window = win

        if closest_window is None:
            log_debug(['No valid window found'])
            return
        log_debug(['Closest left window:', closest_window.list_add_window()])
        closest_window.activate(True)

    def nav_right(self):
        win_id = self.get_active_window()
        if not self.exists():
            return False
        _, _, t, r = self.windows[win_id].get_size()
        closest_left_border = sys.maxint
        lowest_top_diff = sys.maxint
        closest_window = None

        for win in self.work_space.get_viewable_windows():
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

            # See comment in nav-left
            if lowest_top_diff == top_border_diff and t < wt:
                continue

            closest_left_border = wl
            lowest_top_diff = top_border_diff
            closest_window = win

        if closest_window is None:
            log_debug(['No valid window found'])
            return
        log_debug(['Closest right window:', closest_window.list_add_window()])
        closest_window.activate(True)

    def nav_up(self):
        win_id = self.get_active_window()
        if not self.exists():
            return False
        l, _, t, _ = self.windows[win_id].get_size()
        closest_bottom_border = 0
        lowest_left_diff = sys.maxint
        closest_window = None

        for win in self.work_space.get_viewable_windows():
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

            # See comment in nav-left
            if lowest_left_diff == left_border_diff and wl > l:
                continue

            closest_bottom_border = wb
            lowest_left_diff = left_border_diff
            closest_window = win

        if closest_window is None:
            log_debug(['No valid window found'])
            return
        log_debug(['Closest top window:', closest_window.list_add_window()])
        closest_window.activate(True)

    def nav_down(self):
        win_id = self.get_active_window()
        if not self.exists():
            return False
        l, b, _, _ = self.windows[win_id].get_size()
        closest_top_border = sys.maxint
        lowest_left_diff = sys.maxint

        for win in self.work_space.get_viewable_windows():
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

            # See comment in nav-left
            if lowest_left_diff == left_border_diff and wl > l:
                continue

            closest_top_border = wt
            lowest_left_diff = left_border_diff
            closest_window = win

        if closest_window is None:
            log_debug(['No valid window found'])
            return
        log_debug(['Closest top window:', closest_window.list_add_window()])
        closest_window.activate(True)

    def add_to_window_group(self, target_id):
        win_id = self.get_active_window()
        target_id = int(target_id)
        if self.exists(win_id) or not self.exists(target_id):
            log_debug(['Active window exists, or target window does not exist'])
            return False

        new_window = Window(win_id, self.generate_new_window_id())
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

    def list_screens(self, prepend='', exclude_active=False, include_views=True):
        screens_list = range(len(self.work_space.screens))
        active_screen_index = self.get_active_screen()
        print_out = []
        for index in screens_list:
            if exclude_active and index == active_screen_index:
                continue
            viewable_screen_index = self.work_space.viewable_screen_index(index)
            name = self.work_space.screens[index].name
            print_out.append(prepend + str(index) + " : v" + str(viewable_screen_index) + " - " + name)
            if include_views and viewable_screen_index is not None:
                print_out.append(prepend + 'v' + str(viewable_screen_index) + " - " + name)

        return print_out

    def get_active_screen(self):
        active_window_id = self.get_active_window()
        if self.exists(active_window_id):
            return self.windows[active_window_id].get_screen_index()
        else:
            return None

    def generate_new_window_id(self):
        return len(self.windows)

    def woof_id_to_window_id(self, woof_id):
        for window_id, window in self.windows.iteritems():
            if window.woof_id == woof_id:
                return window_id
        return None

    def window_id_to_woof_id(self, window_id):
        return self.windows[window_id].woof_id
