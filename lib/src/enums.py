class DIR:
    """Enum for directions"""
    LEFT = 0
    DOWN = 1
    UP = 2
    RIGHT = 3


class PLANE:
    """Enum for plane directions"""
    HORIZONTAL = 0
    VERTICAL = 1


class SCREEN_STATE:
    ACTIVE = 0
    INACTIVE = 1


class WINDOW_STATE:
    NORMAL = 0
    SHADED = 1
    MINIMIZED = 2
    MAXIMIZED = 3


class OPTIONS:
    NONE = ''
    DEBUG = 'db'
    RESTORE = 're'
    LIST = 'la'
    ADD_HORIZONTAL = 'ah'
    ADD_VERTICAL = 'av'
    EXPAND_HORIZONTAL = 'eh'
    REDUCE_HORIZONTAL = 'rh'
    EXPAND_VERTICAL = 'ev'
    REDUCE_VERTICAL = 'rv'
    CHANGE_PLANE = 'cp'
    SWAP_PANE = 'sp'
    SWAP = 'sw'
    MINIMIZE_ALL = 'mn'
    UNMINIMIZE_ALL = 'um'
    MAXIMIZE = 'mx'
    KILL = 'kl'
    REMOVE = 'rm'
    MOVE_TO = 'mv'
    NAV_RIGHT = 'gr'
    NAV_LEFT = 'gl'
    NAV_UP = 'gu'
    NAV_DOWN = 'gd'
    ADD_TO_GROUP = 'ag'
    ACTIVATE_NEXT_WINDOW_IN_GROUP = 'nw'
    ACTIVATE_PREV_WINDOW_IN_GROUP = 'pw'
    SWAP_SCREENS = 'ss'
    NEW_SCREEN = 'ns'
    LIST_SCREENS = 'ls'
    RENAME_SCREEN = 'rs'


def print_options(windows):
    exclude = ['__module__', '__doc__', 'NONE']
    commands = []
    for option, command in vars(OPTIONS).items():
        if option in exclude:
            continue
        commands.append(command)
    # commands += create_specials(windows)
    commands.sort()

    for command in commands:
        print(command)


def create_specials(windows):
    specials = []
    windows_list = windows.list_add_windows()
    specials += prepend_command(OPTIONS.ADD_HORIZONTAL, windows_list)
    specials += prepend_command(OPTIONS.ADD_VERTICAL, windows_list)
    specials += prepend_command(OPTIONS.SWAP, windows_list)
    specials += prepend_command(OPTIONS.MOVE_TO, windows_list)
    specials += prepend_command(OPTIONS.ADD_TO_GROUP, windows_list)
    specials += windows.list_screens(OPTIONS.SWAP_SCREENS, True)

    return specials


def prepend_command(prepend, window_list):
    new_window_list = []
    for print_out in window_list:
        new_window_list.append(prepend + print_out)
    return new_window_list
