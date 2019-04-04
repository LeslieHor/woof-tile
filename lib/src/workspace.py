import config
import helpers
from node import Node
from enums import *


class Workspace(Node):
    def __init__(self, tree_manager, name, geometry=None, state=SCREEN_STATE.INACTIVE):
        Node.__init__(self, 1)
        Node.set_parent(self, tree_manager)

        self.name = name
        self.geometry = geometry
        self.state = state
        self.last_active_window_id = None

    # ------------------------------------------------------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------------------------------------------------------

    def get_name(self):
        return self.name

    def get_geometry(self):
        return self.geometry

    def get_state(self):
        return self.state

    def get_last_active_window_id(self):
        return self.last_active_window_id

    def is_active(self):
        return self.state == SCREEN_STATE.ACTIVE

    def get_interactable_endpoints(self):
        if self.get_child_count() == 0:
            return [self]
        return Node.get_interactable_endpoints(self)

    def get_viewable_windows(self):
        return Node.get_interactable_endpoints(self)

    def get_ui_string(self):
        index = self.parent.get_workspace_index(self)
        return 's' + str(index) + config.COMMENT_SEP + self.get_name()

    # ------------------------------------------------------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------------------------------------------------------

    def set_name(self, new_name):
        self.name = new_name

    def set_geometry(self, new_geometry):
        self.geometry = new_geometry

    def set_state(self, new_state):
        self.state = new_state

    def set_last_active_window_id(self, new_last_active_window_id):
        self.last_active_window_id = new_last_active_window_id

    # ------------------------------------------------------------------------------------------------------------------
    # Trickle downs
    # ------------------------------------------------------------------------------------------------------------------

    def to_json(self):
        if self.get_geometry() is None:
            geometry = None
        else:
            ((px, py), (sx, sy)) = self.get_geometry()
            geometry = [[px, py], [sx, sy]]

        json = '{'
        json += '"type":' + helpers.json_com('workspace') + ','
        json += '"name":' + helpers.json_com(self.get_name()) + ','
        json += '"geometry":' + helpers.json_com(geometry) + ','
        json += '"state":' + helpers.json_com(self.get_state()) + ','
        json += '"last_active_window_id":' + helpers.json_com(self.get_last_active_window_id()) + ','
        json += Node.to_json(self)
        json += '}'

        return json

    def restore_splits(self):
        [c.restore_splits() for c in self.get_children()]

    def backup_splits(self):
        [c.backup_splits() for c in self.get_children()]

    # ------------------------------------------------------------------------------------------------------------------
    # Bubble ups
    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def resize_vertical(_caller_child, _increment):
        return False

    @staticmethod
    def resize_horizontal(_caller_child, _increment):
        return False

    def get_screen_index(self):
        return self.parent.get_screen_index(self)

    def set_window_active(self, window):
        self.last_active_window_id = window.window_id
        self.parent.set_window_active(window)

    def replace_and_trim(self, calling_child):
        self.remove_child(calling_child)
        self.set_last_active_window_id(None)

    def get_workspace_viewport(self):
        return self.get_viewport()

    def get_smallest_immutable_subtree(self, calling_child):
        return calling_child
    # ------------------------------------------------------------------------------------------------------------------
    # Child Requests
    # ------------------------------------------------------------------------------------------------------------------

    def get_viewports(self):
        """
        Return geometry with gap correction
        """
        (x_pos, y_pos), (x_size, y_size) = self.get_geometry()

        # Correct for gaps
        x_pos += config.GAP
        y_pos += config.GAP
        x_size -= 2 * config.GAP
        y_size -= 2 * config.GAP

        return [((x_pos, y_pos), (x_size, y_size))]

    def get_viewport(self, _calling_child=None):
        return self.get_viewports()[0]

    # ------------------------------------------------------------------------------------------------------------------
    # Other
    # ------------------------------------------------------------------------------------------------------------------

    def set_active(self, geometry):
        self.set_state(SCREEN_STATE.ACTIVE)
        self.set_geometry(geometry)
        self.restore_splits()
        self.unminimize()
        self.redraw()

    def set_inactive(self):
        self.set_state(SCREEN_STATE.INACTIVE)
        self.set_geometry(None)
        self.minimize()

    def update_status(self):
        self.parent.update_status_for_active(self)

    def activate_last_active_window(self):
        windows = [win for win in self.get_all_windows() if win.window_id == self.get_last_active_window_id()]
        if windows:
            windows[0].activate(True)

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
