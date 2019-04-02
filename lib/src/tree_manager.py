from functools import reduce
import helpers
from workspace import Workspace
from enums import SCREEN_STATE
import config


class TreeManager:
    """Root of all tree structures"""

    def __init__(self):
        self.viewable_screen_count = 0
        self.last_active_window_id = None
        self.workspaces = []

        for workspace_config in config.WORKSPACE_CONFIG:
            (name, geometry) = workspace_config
            if geometry is not None:
                new_workspace = Workspace(self, name, geometry, SCREEN_STATE.ACTIVE)
                self.viewable_screen_count += 1
            else:
                new_workspace = Workspace(self, name)

            self.workspaces.append(new_workspace)

        self.update_active_workspaces_statuses()

    # ------------------------------------------------------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------------------------------------------------------

    def get_viewable_screen_count(self):
        return self.viewable_screen_count

    def get_last_active_window_id(self):
        return self.last_active_window_id

    def get_workspaces(self):
        return self.workspaces

    def get_workspaces_count(self):
        return len(self.workspaces)

    def get_workspace(self, index):
        return self.get_workspaces()[index]

    def get_all_windows(self):
        return reduce(lambda acc, c: c.get_all_windows() + acc, self.get_workspaces(), [])

    def get_window_from_window_id(self, window_id):
        windows = [win for win in self.get_all_windows() if win.window_id == window_id]
        if windows:
            return windows[0]
        return None

    def get_window_from_woof_id(self, woof_id):
        [window] = [win for win in self.get_all_windows() if win.woof_id == woof_id]
        return window

    def get_active_workspaces(self):
        return [ws for ws in self.get_workspaces() if ws.is_active()]

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
        (_, geometry) = config.WORKSPACE_CONFIG[index]
        [workspace] = [ws for ws in self.get_active_workspaces() if ws.get_geometry() == geometry]
        return workspace

    def get_last_active_window(self):
        return self.get_window_from_window_id(self.get_last_active_window_id())

    def get_workspace_from_config(self, geometry):
        [workspace] = [ws for ws in self.get_workspaces() if ws.get_geometry() == geometry]
        return workspace

    def get_active_workspace(self, index):
        (_name, geometry) = config.WORKSPACE_CONFIG[index]
        return self.get_workspace_from_config(geometry)

    def get_active_workspace_index(self, workspace):
        counter = 0
        for (_name, geometry) in config.WORKSPACE_CONFIG:
            if geometry is None:
                continue
            if workspace.get_geometry() == geometry:
                return counter

            counter += 1
        return None

    def get_workspace_index(self, calling_child):
        return self.workspaces.index(calling_child)

    def get_new_index(self):
        return str(len(self.get_workspaces()))

    # ------------------------------------------------------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------------------------------------------------------

    def set_viewable_screen_count(self, new_viewable_screen_count):
        self.viewable_screen_count = new_viewable_screen_count

    def set_last_active_window_id(self, new_last_active_window_id):
        self.last_active_window_id = new_last_active_window_id

    def set_workspaces(self, new_workspaces):
        self.workspaces = new_workspaces

    def add_workspace(self, name=None):
        if name is None:
            name = self.get_new_index()
        self.workspaces.append(Workspace(self, name))

    # ------------------------------------------------------------------------------------------------------------------
    # Trickle downs
    # ------------------------------------------------------------------------------------------------------------------

    def to_json(self):
        if self.get_workspaces is None:
            workspaces = None
        else:
            workspaces = '[' + ','.join([w.to_json() for w in self.get_workspaces()]) + ']'

        json = '{'
        json += '"viewable_screen_count":' + helpers.json_com(self.get_viewable_screen_count()) + ','
        json += '"last_active_window_id":' + helpers.json_com(self.get_last_active_window_id()) + ','
        json += '"workspaces":' + workspaces
        json += '}'

        return json

    def debug_print(self):
        json = self.to_json()
        print(json)

    def minimize(self):
        [ws.minimize() for ws in self.get_workspaces()]

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
        for i in range(self.get_workspaces_count()):
            name = str(i) + ': ' + self.get_workspace(i).get_name()
            if i == active_index:
                name = '> ' + name + ' <'
            status.append(name)
        status_line = ' | '.join(status)

        with open(config.STATUSES_PATH + str(target_file_index), 'w') as file_:
            file_.write(status_line)
