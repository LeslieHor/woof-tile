from functools import reduce
import helpers
from node import Node
from workspace import Workspace
from enums import SCREEN_STATE
import config


class TreeManager(Node):
    """Root of all tree structures"""

    def __init__(self, **kwargs):
        Node.__init__(self, None)

        self.viewable_screen_count = kwargs.get('viewable_screen_count', 0)
        self.last_active_window_id = kwargs.get('last_active_window_id', None)

    def initialise_workspaces(self):
        for workspace_config in config.get_config('workspace_config'):
            (name, geometry) = workspace_config
            if geometry is not None:
                new_workspace = Workspace(name=name, geometry=geometry, state=SCREEN_STATE.ACTIVE)
                self.viewable_screen_count += 1
            else:
                new_workspace = Workspace(name=name)

            self.add_child(new_workspace)

        self.update_active_workspaces_statuses()

    # ------------------------------------------------------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------------------------------------------------------

    def get_viewable_screen_count(self):
        return self.viewable_screen_count

    def get_last_active_window_id(self):
        return self.last_active_window_id

    def get_window_from_window_id(self, window_id):
        windows = [win for win in self.get_all_windows() if win.window_id == window_id]
        if windows:
            return windows[0]
        return None

    def get_window_from_woof_id(self, woof_id):
        [window] = [win for win in self.get_all_windows() if win.woof_id == woof_id]
        return window

    def get_active_workspaces(self):
        return [ws for ws in self.get_children() if ws.is_active()]

    def get_active_workspaces_count(self):
        return len(self.get_active_workspaces())

    def get_interactable_endpoints(self):
        return reduce(lambda acc, ws: helpers.combine_lists(ws.get_interactable_endpoints(), acc),
                      self.get_active_workspaces(), [])

    def get_viewable_windows(self):
        return reduce(lambda acc, ws: helpers.combine_lists(ws.get_viewable_windows(), acc),
                      self.get_active_workspaces(), [])

    def get_new_woof_id(self):
        in_use_woof_ids = [win.get_woof_id() for win in self.get_all_windows()]
        counter = 0
        while counter in in_use_woof_ids:
            counter += 1
        return counter

    def get_viewable_workspace(self, index):
        (_, geometry) = config.get_config('workspace_config')[index]
        [workspace] = [ws for ws in self.get_active_workspaces() if ws.get_geometry() == geometry]
        return workspace

    def get_last_active_window(self):
        return self.get_window_from_window_id(self.get_last_active_window_id())

    def get_workspace_from_config(self, geometry):
        [workspace] = [ws for ws in self.get_children() if ws.get_geometry() == geometry]
        return workspace

    def get_active_workspace(self, index):
        (_name, geometry) = config.get_config('workspace_config')[index]
        return self.get_workspace_from_config(geometry)

    def get_active_workspace_index(self, workspace):
        counter = 0
        for (_name, geometry) in config.get_config('workspace_config'):
            if geometry is None:
                continue
            if workspace.get_geometry() == geometry:
                return counter

            counter += 1
        return None

    def get_workspace_index(self, calling_child):
        return self.children.index(calling_child)

    def get_new_index(self):
        return str(len(self.get_children()))

    def get_empty_containers(self):
        return reduce(lambda a, c: helpers.combine_lists(c.get_empty_containers(), a), self.get_children(), [])

    # ------------------------------------------------------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------------------------------------------------------

    def set_last_active_window_id(self, new_last_active_window_id):
        self.last_active_window_id = new_last_active_window_id

    def add_workspace(self, name=None):
        if name is None:
            name = self.get_new_index()
        self.add_child(Workspace(name=name))

    # ------------------------------------------------------------------------------------------------------------------
    # Trickle downs
    # ------------------------------------------------------------------------------------------------------------------

    def to_json(self):
        json = Node.to_json(self)
        json['type'] = 'tree_manager'
        json['viewable_screen_count'] = self.get_viewable_screen_count()
        json['last_active_window_id'] = self.get_last_active_window_id()

        return json

    # ------------------------------------------------------------------------------------------------------------------
    # Bubble ups
    # ------------------------------------------------------------------------------------------------------------------

    def change_plane(self):
        return

    def set_window_active(self, window):
        self.set_last_active_window_id(window.window_id)

    # ------------------------------------------------------------------------------------------------------------------
    # Other
    # ------------------------------------------------------------------------------------------------------------------

    def redraw(self):
        [ws.redraw() for ws in self.get_active_workspaces()]

    def update_active_workspaces_statuses(self):
        [ws.update_status() for ws in self.get_active_workspaces()]

    def update_status_for_active(self, active_workspace):
        target_file_index = self.get_active_workspace_index(active_workspace)
        active_index = self.get_workspace_index(active_workspace)
        status = []
        for i in range(self.get_child_count()):
            name = str(i) + ': ' + self.get_child(i).get_name()
            if i == active_index:
                name = '> ' + name + ' <'
            status.append(name)
        status_line = ' | '.join(status)

        with open(config.get_config('statuses_dir') + str(target_file_index), 'w') as file_:
            file_.write(status_line)
