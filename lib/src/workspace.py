from screen import Screen
from enums import SCREEN_STATE


class WorkSpace:
    """Root of all tree structures"""

    def __init__(self, screen_config):
        self.screen_config = screen_config
        self.viewable_screen_count = len(screen_config)
        self.screens = []

        counter = 0
        for config in screen_config:
            new_screen = Screen(self, str(counter), config, SCREEN_STATE.ACTIVE)
            self.screens.append(new_screen)
            counter += 1

    def debug_print(self):
        print("WorkSpace")
        window_counter = 0
        for screen in self.screens:
            window_counter += screen.debug_print(1)
        return window_counter

    def new_screen(self):
        self.screens.append(Screen(self, str(len(self.screens))))

    def swap_screens(self, screen_index_a, screen_index_b):
        if screen_index_a == screen_index_b:
            return False

        screen_a = self.screens[screen_index_a]
        screen_b = self.screens[screen_index_b]

        if screen_a.is_active() and screen_b.is_active():
            self.swap_two_active_screens(screen_a, screen_b)
        elif screen_a.is_active() and not screen_b.is_active():
            self.swap_active_inactive_screens(screen_a, screen_b)
        elif not screen_a.is_active and screen_b.is_active():
            self.swap_active_inactive_screens(screen_b, screen_a)
        else:
            return False

    def swap_two_active_screens(self, screen_a, screen_b):
        screen_a_config = screen_a.get_config()
        screen_b_config = screen_b.get_config()

        screen_a.set_config(screen_b_config)
        screen_b.set_config(screen_a_config)
        screen_a.set_size()
        screen_b.set_size()

    def swap_active_inactive_screens(self, active_screen, inactive_screen):
        active_config = active_screen.get_config()

        inactive_screen.set_active(active_config)

        active_screen.set_inactive()

    def get_screen_index(self, calling_child):
        return self.screens.index(calling_child)

    def viewable_screen_index(self, index):
        """
        Given an index inside of self.screens, get the index of which monitor it is
        """
        target_screen_config = self.screens[index].config
        counter = 0
        for config in self.screen_config:
            if target_screen_config == config:
                return counter
            counter += 1
        return None

    def viewable_screen_index_to_index(self, viewable_screen_index):
        """
        Given an index for a monitor, get the index of where it is in self.screens
        """
        viewable_screen_config = self.screen_config[viewable_screen_index]
        for i in range(len(self.screens)):
            config = self.screens[i].config
            if viewable_screen_config == config:
                return i
        return None

    def get_viewable_windows(self):
        windows = []
        for screen in self.screens:
            if not screen.is_active():
                continue
            window_list = screen.get_window_list()
            if window_list is not None:
                windows += window_list

        return windows
