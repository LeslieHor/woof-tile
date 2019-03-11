from screen import Screen


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
