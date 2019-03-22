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


def get_option_description(option):
    more_prepend = '--more-- '

    if option == OPTIONS.NONE:
        return ''
    elif option == OPTIONS.DEBUG:
        return '(debug) print out debug information'
    elif option == OPTIONS.RESTORE:
        return '(restore) restore all window positions'
    elif option == OPTIONS.LIST:
        return more_prepend + '(list) list the windows available for interaction'
    elif option == OPTIONS.ADD_HORIZONTAL:
        return more_prepend + '(add horizontal) add the active window the the right of a target window'
    elif option == OPTIONS.ADD_VERTICAL:
        return more_prepend + '(add vertical) add the active window below the target window'
    elif option == OPTIONS.EXPAND_HORIZONTAL:
        return '(expand horizontal) increase the horizontal size of the active window'
    elif option == OPTIONS.REDUCE_HORIZONTAL:
        return '(reduce horizontal) decrease the horizontal size of the active window'
    elif option == OPTIONS.EXPAND_VERTICAL:
        return '(expand vertical) increase the vertical size of the active window'
    elif option == OPTIONS.REDUCE_VERTICAL:
        return '(reduce vertical) decrease the vertical size of the active window'
    elif option == OPTIONS.CHANGE_PLANE:
        return '(change plane) change a vertical split to a horizontal split and vice versa'
    elif option == OPTIONS.SWAP_PANE:
        return '(swap-pane) swap the two windows in the split'
    elif option == OPTIONS.SWAP:
        return more_prepend + '(swap) swap the positions of two windows in the tree'
    elif option == OPTIONS.MINIMIZE_ALL:
        return '(minimize all) minimize all windows in woof'
    elif option == OPTIONS.MAXIMIZE:
        return '(maximize) maximize the active window as if it was the only window on the screen'
    elif option == OPTIONS.KILL:
        return '(kill) attempt to close the window and remove it from woof'
    elif option == OPTIONS.REMOVE:
        return '(remove) remove the window from woof'
    elif option == OPTIONS.MOVE_TO:
        return '(move to) move the active window to another window as a split'
    elif option == OPTIONS.NAV_RIGHT:
        return '(nav right) focus window the the right'
    elif option == OPTIONS.NAV_LEFT:
        return '(nav left) focus window to the left'
    elif option == OPTIONS.NAV_UP:
        return '(nav up) focus window to the top'
    elif option == OPTIONS.NAV_DOWN:
        return '(nav down) focus window to the bottom'
    elif option == OPTIONS.ADD_TO_GROUP:
        return more_prepend + '(add to group) add window as a group'
    elif option == OPTIONS.ACTIVATE_NEXT_WINDOW_IN_GROUP:
        return '(next window in group) activate next window in group'
    elif option == OPTIONS.ACTIVATE_PREV_WINDOW_IN_GROUP:
        return '(prev window in group) activate prev window in group'
    elif option == OPTIONS.SWAP_SCREENS:
        return more_prepend + '(swap screen) swap the two screens'
    elif option == OPTIONS.NEW_SCREEN:
        return '(new screen) adds a new screen (not functional)'
    elif option == OPTIONS.LIST_SCREENS:
        return '(list screens) list all the screens in woof'
    elif option == OPTIONS.RENAME_SCREEN:
        return '(rename screen) rename the current screen'

    else:
        return ''


def print_options(_windows):
    exclude = ['__module__', '__doc__', 'NONE']
    commands = []
    for option, command in vars(OPTIONS).items():
        if option in exclude:
            continue
        listing = command
        listing += " : " + get_option_description(command)
        commands.append(listing)
    commands.sort()

    for command in commands:
        print(command)

