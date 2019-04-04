from container import Container
from enums import *


class EmptyContainer(Container):

    def __init__(self, window_class):
        Container.__init__(self, None, None)
        self.window_class = window_class
    # ------------------------------------------------------------------------------------------------------------------
    # Blockers
    # ------------------------------------------------------------------------------------------------------------------

    def get_all_windows(self):
        return []

    def get_interactable_endpoints(self):
        return []

    def redraw(self):
        pass

    def minimize(self):
        self.set_state(WINDOW_STATE.MINIMIZED)

    def unminimize(self):
        self.set_state(WINDOW_STATE.NORMAL)

    def activate(self, set_last_active=False):
        if set_last_active:
            self.parent.set_window_active(self)
        self.set_state(WINDOW_STATE.NORMAL)

    def shade(self):
        self.set_state(WINDOW_STATE.SHADED)

    def unshade(self):
        self.set_state(WINDOW_STATE.NORMAL)

    # ------------------------------------------------------------------------------------------------------------------
    # Other
    # ------------------------------------------------------------------------------------------------------------------

    def swallow(self, window):
        self.parent.replace_child(self, window)

    def get_empty_containers(self):
        return [self]
