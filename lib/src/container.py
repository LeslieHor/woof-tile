from group_node import GroupNode
from node import Node
import system_calls
import helpers
import config
from log import log_debug
from enums import *


class Container(Node):
    """Leaf node, representing a viewable window"""

    def __init__(self, window_id, woof_id):
        Node.__init__(self, 0)  # This is barely a node at all

        self.window_id = window_id
        self.woof_id = woof_id
        self.state = WINDOW_STATE.NORMAL
        self.window_class = system_calls.get_window_class(self.window_id)

    # ------------------------------------------------------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------------------------------------------------------

    def get_window_id(self):
        return self.window_id

    def get_woof_id(self):
        return self.woof_id

    def get_state(self):
        return self.state

    def get_window_class(self):
        return self.window_class

    def get_window_title(self):
        return system_calls.get_window_title(self.window_id)

    def get_viewport(self):
        if self.get_state() == WINDOW_STATE.MAXIMIZED:
            viewport = self.get_workspace_viewport()
        else:
            viewport = self.parent.get_viewport(self)
        corrected_viewport = self.correct_borders_for_class(viewport)
        return corrected_viewport

    def get_border_class_correction(self):
        if self.get_window_class() in config.BORDER_CLASS_CORRECTIONS:
            return config.BORDER_CLASS_CORRECTIONS[self.get_window_class()]
        else:
            return config.DEFAULT_BORDER_CORRECTIONS

    def get_all_windows(self):
        return [self]

    def is_in_group_node(self):
        return isinstance(self.get_parent(), GroupNode)

    def get_interactable_endpoints(self):
        if self.get_state == WINDOW_STATE.SHADED or \
                self.get_state == WINDOW_STATE.MINIMIZED:
            return []
        return [self]

    def get_ui_string(self):
        return str(self.get_woof_id()) + config.COMMENT_SEP + self.get_window_title()

    def is_shaded(self):
        return self.get_state() == WINDOW_STATE.SHADED

    def is_minimized(self):
        return self.get_state() == WINDOW_STATE.MINIMIZED

    # ------------------------------------------------------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------------------------------------------------------

    def set_window_id(self, new_window_id):
        self.window_id = new_window_id

    def set_woof_id(self, new_woof_id):
        self.woof_id = new_woof_id

    def set_state(self, new_state):
        self.state = new_state

    # ------------------------------------------------------------------------------------------------------------------
    # Trickle downs
    # ------------------------------------------------------------------------------------------------------------------

    def to_json(self):
        json = '{'
        json += '"type":' + helpers.json_com('container') + ','
        json += '"window_id":' + helpers.json_com(self.get_window_id()) + ','
        json += '"woof_id":' + helpers.json_com(self.get_woof_id()) + ','
        json += '"state":' + helpers.json_com(self.get_state()) + ','
        json += '"window_class":' + helpers.json_com(self.get_window_class())
        json += '}'

        return json

    # ------------------------------------------------------------------------------------------------------------------
    # Bubble ups
    # ------------------------------------------------------------------------------------------------------------------

    def remove_and_trim(self, _=None):
        self.get_parent().remove_and_trim(self)

    def get_smallest_immutable_subtree(self, _=None):
        return self.parent.get_smallest_immutable_subtree(self)

    # ------------------------------------------------------------------------------------------------------------------
    # Other
    # ------------------------------------------------------------------------------------------------------------------

    def correct_borders_for_class(self, viewport):
        ((x_pos_1, y_pos_1), (x_size_1, y_size_1)) = viewport
        ((x_pos_2, y_pos_2), (x_size_2, y_size_2)) = self.get_border_class_correction()

        corrected_viewport = (
            (x_pos_1 + x_pos_2, y_pos_1 + y_pos_2),
            (x_size_1 + x_size_2, y_size_1 + y_size_2)
        )

        return corrected_viewport

    def redraw(self):
        """Call into the WM to resize the window"""
        ((px, py), (sx, sy)) = self.get_viewport()
        system_calls.set_window_geometry(self.get_window_id(), px, py, sx, sy)

    def minimize(self):
        """Call into WM to minimize the window"""
        system_calls.minimise_window(self.get_window_id())
        self.set_state(WINDOW_STATE.MINIMIZED)

    def unminimize(self):
        self.activate()
        self.set_state(WINDOW_STATE.NORMAL)

    def activate(self, set_last_active=False):
        """Call into WM to focus the window"""
        if set_last_active:
            self.parent.set_window_active(self)
        system_calls.activate_window(self.window_id)
        self.set_state(WINDOW_STATE.NORMAL)

    def change_plane(self):
        """Request parent to change plane orientation"""
        self.parent.change_plane()

    def maximize(self):
        self.set_state(WINDOW_STATE.MAXIMIZED)
        self.redraw()

    def unmaximize(self):
        self.set_state(WINDOW_STATE.NORMAL)
        self.redraw()

    def shade(self):
        system_calls.shade_window(self.window_id)
        self.state = WINDOW_STATE.SHADED

    def unshade(self):
        system_calls.unshade_window(self.window_id)
        self.state = WINDOW_STATE.NORMAL

    def resize_vertical(self, increment):
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
                next_child.resize_vertical(increment)

    def resize_horizontal(self, increment):
        if not self.parent.resize_horizontal(self, increment):
            log_debug(['Unable to resize. Using alternative'])
            next_child = self.parent.find_earliest_a_but_not_me(self)
            if next_child is not None:
                if not self.parent.all_are_bees(self):
                    log_debug(['All are not bees'])
                    increment *= -1
                elif self.parent.get_plane_type() == PLANE.VERTICAL:
                    increment *= -1
                next_child.resize_horizontal(increment)
