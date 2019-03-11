from desktop import Desktop


class WorkSpace:
    """Root of all tree structures"""

    def __init__(self, desktop_count, screens_count, horizontal_res, vertical_res):
        self.desktops_count = desktop_count
        self.desktops = []

        for _desktop in range(self.desktops_count):
            new_desktop = Desktop(screens_count, horizontal_res, vertical_res)
            self.desktops.append(new_desktop)

    def debug_print(self):
        print("WorkSpace")
        window_counter = 0
        for desktop in self.desktops:
            window_counter += desktop.debug_print(1)
        return window_counter
