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
    DEBUG = 'debug'
    RESTORE = 'restore'
    LIST = 'list'
    ADD = 'add'
    EXPAND_HORIZONTAL = 'eh'
    REDUCE_HORIZONTAL = 'rh'
    EXPAND_VERTICAL = 'ev'
    REDUCE_VERTICAL = 'rv'
    CHANGE_PLANE = 'change-plane'
    SWAP_PANE = 'swap-pane'
    SWAP = 'swap'
    MINIMIZE_ALL = 'min'
    UNMINIMIZE_ALL = 'unmin'
    MAXIMIZE = 'maximize'
    KILL = 'kill'
    REMOVE = 'remove'
    MOVE_TO = 'move-to'
    NAV_RIGHT = 'nav-right'
    NAV_LEFT = 'nav-left'
    NAV_UP = 'nav-up'
    NAV_DOWN = 'nav-down'
    ADD_TO_GROUP = 'add-to-group'
    ACTIVATE_NEXT_WINDOW_IN_GROUP = 'activate-next-window'
    ACTIVATE_PREV_WINDOW_IN_GROUP = 'activate-prev-window'
    SWAP_SCREENS = 'swap-screen'
    NEW_SCREEN = 'new-screen'
    LIST_SCREENS = 'list-screens'
    RENAME_SCREEN = 'rename-screen'


def print_options():
    commands = []
    for option, command in vars(OPTIONS).items():
        if option == '__module__' or \
                option == '__doc__' or \
                option == 'NONE' or \
                option == "ADD":
            continue
        commands.append(command)
    commands.sort()

    print("add h")
    print("add v")
    for command in commands:
        print(command)
