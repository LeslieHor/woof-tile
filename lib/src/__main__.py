import pickle  # For saving the window structure to disk
import sys  # For getting args
from windows import Windows
from log import log_info, log_debug, log_error
from config import *
from enums import PLANE, DIR, OPTIONS, print_options
from helpers import element
import system_calls


def debug_print():
    WINDOWS_OBJ.debug_print()


def dir_str_to_plane_dir(direction):
    if direction == 'h':
        return dir_str_to_plane_dir('r')
    elif direction == 'v':
        return dir_str_to_plane_dir('d')

    elif direction == 'l':
        return PLANE.VERTICAL, DIR.LEFT
    elif direction == 'd':
        return PLANE.HORIZONTAL, DIR.DOWN
    elif direction == 'u':
        return PLANE.HORIZONTAL, DIR.UP
    elif direction == 'r':
        return PLANE.VERTICAL, DIR.RIGHT
    else:
        return False


def main(args):

    cmd = args[1]
    log_info(['------- Start --------', 'Args:'] + args[1:])

    if cmd == OPTIONS.DEBUG:
        debug_print()
    elif cmd == OPTIONS.RESTORE:
        WINDOWS_OBJ.restore_all()
    elif cmd == OPTIONS.LIST:
        print(WINDOWS_OBJ.list_add_windows(args[2]))
    elif cmd == OPTIONS.ADD:
        # Adding to a window : "add h 32478239 : window title"
        # Adding to a screen : "add h Screen 1"
        plane = element(args, 2, None)
        target_id = element(args, 3, None)
        screen_index = element(args, 4, None)

        if target_id is None:
            log_debug(['No target id. Listing windows.'])
            print(WINDOWS_OBJ.list_add_windows("add " + plane + " "))
            return

        log_debug(['Target ID found. TargetId:', target_id])
        if target_id == 'Screen':
            log_debug(['Detected screen add. Screen Index:', screen_index])
        else:
            log_debug(['Not a screen add'])

        plane_type, direction = dir_str_to_plane_dir(plane)

        WINDOWS_OBJ.add(plane_type, direction, target_id, screen_index)
    elif cmd == OPTIONS.EXPAND_VERTICAL:
        increment = element(args, 2, None)
        if increment is not None:
            increment = int(increment)
        log_debug(['Attempting to expand vertical size.'])
        WINDOWS_OBJ.resize_vertical('expand', increment)
    elif cmd == OPTIONS.REDUCE_VERTICAL:
        log_debug(['Attempting to reduce vertical size.'])
        increment = element(args, 2, None)
        if increment is not None:
            increment = int(increment)
        WINDOWS_OBJ.resize_vertical('reduce', increment)
    elif cmd == OPTIONS.EXPAND_HORIZONTAL:
        log_debug(['Attempting to expand horizontal size.'])
        increment = element(args, 2, None)
        if increment is not None:
            increment = int(increment)
        WINDOWS_OBJ.resize_horizontal('expand', increment)
    elif cmd == OPTIONS.REDUCE_HORIZONTAL:
        increment = element(args, 2, None)
        if increment is not None:
            increment = int(increment)
        log_debug(['Attempting to reduce horizontal size.'])
        WINDOWS_OBJ.resize_horizontal('reduce', increment)
    elif cmd == OPTIONS.CHANGE_PLANE:
        WINDOWS_OBJ.change_plane()
    elif cmd == OPTIONS.SWAP_PANE:
        WINDOWS_OBJ.swap_pane_position()
    elif cmd == OPTIONS.SWAP:
        if len(args) < 3:
            log_debug(['No target found. Listing windows'])
            print(WINDOWS_OBJ.list_add_windows("swap ", True))
            return

        target_id = int(args[2])
        WINDOWS_OBJ.swap_windows(target_id)
    elif cmd == OPTIONS.MINIMIZE_ALL:
        WINDOWS_OBJ.minimize_all()
    elif cmd == OPTIONS.UNMINIMIZE_ALL:
        WINDOWS_OBJ.unminimize_all()
    elif cmd == OPTIONS.MAXIMIZE:
        if len(args) > 2:
            target_win_id = int(args[2])
        else:
            target_win_id = WINDOWS_OBJ.get_active_window()
        if not WINDOWS_OBJ.exists(target_win_id):
            exit(1)
        win_ids = WINDOWS_OBJ.windows[target_win_id].list_screen_windows()
        if WINDOWS_OBJ.windows[target_win_id].maximized:
            for win_id in win_ids:
                WINDOWS_OBJ.windows[win_id].activate()
                WINDOWS_OBJ.windows[win_id].set_size()

            WINDOWS_OBJ.windows[target_win_id].activate(True)
            WINDOWS_OBJ.windows[target_win_id].maximized = False
        else:
            for win_id in win_ids:
                if win_id == target_win_id:
                    continue
                WINDOWS_OBJ.windows[win_id].minimize()
            WINDOWS_OBJ.windows[target_win_id].maximize()
    elif cmd == OPTIONS.KILL:
        win_id = WINDOWS_OBJ.get_active_window()
        if not WINDOWS_OBJ.exists(win_id):
            exit(1)
        win_id_hex = WINDOWS_OBJ.windows[win_id].window_id_hex
        next_active_window = WINDOWS_OBJ.kill_window(win_id)
        return_string = win_id_hex + "," + str(next_active_window)
        log_debug(['ReturnString:', return_string])
        print(return_string)
    elif cmd == OPTIONS.REMOVE:
        win_id = WINDOWS_OBJ.get_active_window()
        if not WINDOWS_OBJ.exists(win_id):
            exit(1)
        WINDOWS_OBJ.kill_window(win_id)
    elif cmd == OPTIONS.MOVE_TO:
        if len(args) < 3:
            log_debug(['No target id. Listing windows.'])
            print(WINDOWS_OBJ.list_add_windows("move-to ", True))
            return

        main(['', 'remove'])
        main(['', 'add', 'h', args[2]])
    elif cmd == OPTIONS.NAV_RIGHT:
        WINDOWS_OBJ.nav_right()
    elif cmd == OPTIONS.NAV_LEFT:
        WINDOWS_OBJ.nav_left()
    elif cmd == OPTIONS.NAV_UP:
        WINDOWS_OBJ.nav_up()
    elif cmd == OPTIONS.NAV_DOWN:
        WINDOWS_OBJ.nav_down()
    elif cmd == OPTIONS.ADD_TO_GROUP:
        if WINDOWS_OBJ.exists(WINDOWS_OBJ.get_active_window()):
            exit(1)
        if len(args) < 3:
            log_debug(['No target id. Listing windows.'])
            print(WINDOWS_OBJ.list_add_windows("add-to-group "))
            return

        target_id = args[2]
        WINDOWS_OBJ.add_to_window_group(target_id)
    elif cmd == OPTIONS.ACTIVATE_NEXT_WINDOW_IN_GROUP:
        WINDOWS_OBJ.activate_next_window(1)
    elif cmd == OPTIONS.ACTIVATE_PREV_WINDOW_IN_GROUP:
        WINDOWS_OBJ.activate_next_window(-1)
    elif cmd == OPTIONS.SWAP_SCREENS:
        if len(args) < 3:
            if WINDOWS_OBJ.exists(WINDOWS_OBJ.get_active_window()):
                active_screen_index = WINDOWS_OBJ.get_active_screen()
                WINDOWS_OBJ.list_screens('swap-screen', [active_screen_index])
            else:
                log_error(["Attempted to list screens, but current window not registered, so could not exclude current screen"])
                return
        else:
            screen_index_b = parse_screen_index(args[2])
            try:
                screen_index_a = parse_screen_index(args[3])
                if screen_index_a is None:
                    log_error(["Attempted to swap screens but unable to parse second arg:", args[3]])
                    return
                WINDOWS_OBJ.work_space.swap_screens(screen_index_a, screen_index_b)
            except:
                screen_index_a = WINDOWS_OBJ.get_active_screen()
                if screen_index_a is None:
                    log_error(["Attempted to swap screens but active window is not registered"])
                    return
                WINDOWS_OBJ.work_space.swap_screens(screen_index_a, screen_index_b)
                WINDOWS_OBJ.work_space.screens[screen_index_b].activate_last_active_window()
    elif cmd == OPTIONS.NEW_SCREEN:
        WINDOWS_OBJ.work_space.new_screen()
    elif cmd == OPTIONS.LIST_SCREENS:
        WINDOWS_OBJ.list_screens()
    elif cmd == OPTIONS.RENAME_SCREEN:
        name = ' '.join(args[2:])
        active_screen_index = WINDOWS_OBJ.get_active_screen()
        WINDOWS_OBJ.work_space.screens[active_screen_index].set_name(name)

    pickle.dump(WINDOWS_OBJ, open(DATA_PATH, "wb"))


def parse_screen_index(index):
    if index[0] == 'v':
        return WINDOWS_OBJ.work_space.viewable_screen_index_to_index(int(index[1:]))
    else:
        return int(index)


ARGS = sys.argv

if len(ARGS) == 1:
    print_options()
    exit(0)

# Initialise a tree
if ARGS[1] == 'reload':
    WINDOWS_OBJ = Windows(SCREEN_CONFIG)
else:
    try:
        WINDOWS_OBJ = pickle.load(open(DATA_PATH, "rb"))
        if WINDOWS_OBJ.check_windows():
            WINDOWS_OBJ.restore_all()
    except:
        WINDOWS_OBJ = Windows(SCREEN_CONFIG)

if ARGS[1] == "benchmark":
    exit(0)

if __name__ == '__main__':
    main(ARGS)

exit(0)
