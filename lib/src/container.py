from group_node import GroupNode
from node import Node
import system_calls
import config
from log import log_debug
from enums import *


class Container(Node):
    """Leaf node, representing a viewable window"""

    def __init__(self, **kwargs):
        Node.__init__(self, 0)  # This is barely a node at all

        self.window_id = kwargs.get('window_id', None)
        self.woof_id = kwargs.get('woof_id', None)
        self.state = kwargs.get('state', WINDOW_STATE.NORMAL)
        if 'window_class' in kwargs:
            self.window_class = kwargs.get('window_class')
        else:
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
        if self.get_window_class() in config.get_config('border_class_corrections'):
            return config.get_config('border_class_corrections')[self.get_window_class()]
        else:
            return config.get_config('default_border_corrections')

    def get_all_windows(self):
        return [self]

    def is_in_group_node(self):
        return isinstance(self.get_parent(), GroupNode)

    def get_interactable_endpoints(self):
        if self.is_shaded() or self.is_minimized():
            return []
        return [self]

    def get_ui_string(self):
        return str(self.get_woof_id()) + config.get_config('comment_sep') + self.get_window_title()

    def is_shaded(self):
        return self.get_state() == WINDOW_STATE.SHADED

    def is_minimized(self):
        return self.get_state() == WINDOW_STATE.MINIMIZED

    # ------------------------------------------------------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------------------------------------------------------

    def set_state(self, new_state):
        self.state = new_state

    # ------------------------------------------------------------------------------------------------------------------
    # Trickle downs
    # ------------------------------------------------------------------------------------------------------------------

    def to_json(self):
        json = {
            'type': 'container',
            'window_id': self.get_window_id(),
            'woof_id': self.get_woof_id(),
            'state': self.get_state(),
            'window_class': self.get_window_class()
        }

        return json

    def get_layout_json(self):
        json = {
            'type': 'empty_container',
            'window_class': self.get_window_class()
        }

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
        self.set_state(WINDOW_STATE.SHADED)

    def unshade(self):
        system_calls.unshade_window(self.window_id)
        self.set_state(WINDOW_STATE.NORMAL)

    def move_mouse(self):
        ((px, py), (sx, sy)) = self.get_viewport()
        x = px + (sx / 2)
        y = py + (sy / 2)

        system_calls.move_mouse(x, y)

    def resize_vertical(self, increment):
        """Resize the height"""
        self.parent.resize(self, PLANE.HORIZONTAL, increment)

    def resize_horizontal(self, increment):
        """Resize the width"""
        self.parent.resize(self, PLANE.VERTICAL, increment)

