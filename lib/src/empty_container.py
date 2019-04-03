from container import Container
from enums import *


class EmptyContainer(Container):

    def __init__(self, window_id, woof_id):
        Container.__init__(self, window_id, woof_id)

    # ------------------------------------------------------------------------------------------------------------------
    # Blockers
    # ------------------------------------------------------------------------------------------------------------------

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

