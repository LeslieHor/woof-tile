import pickle  # For saving the window structure to disk
import sys  # For getting args
from windows import Windows
from log import log_info, log_debug, log_error
from config import *
from enums import PLANE, DIR, WINDOW_STATE, OPTIONS, print_options
from helpers import element


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


def string_to_integer(value):
    if value == '':
        return None
    else:
        return int(value)


def cut_off_rest(arg):
    return arg.split(' : ')[0]


def main(command_string):

    cmd = command_string[:2]
    args = command_string[2:]
    args = cut_off_rest(args)
    log_info(['------- Start --------', 'Args:', cmd, args])

    if cmd == OPTIONS.DEBUG:
        debug_print()

    elif cmd == OPTIONS.RESTORE:
        WINDOWS_OBJ.restore_all()

    elif cmd == OPTIONS.LIST:
        print(WINDOWS_OBJ.list_add_windows())

    elif cmd == OPTIONS.ADD_HORIZONTAL:
        if args == '':
            print('\n'.join(WINDOWS_OBJ.list_add_windows(OPTIONS.ADD_HORIZONTAL)))
            return

        plane_type = PLANE.VERTICAL
        direction = DIR.RIGHT
        if args[0] == 's':
            target_id = 's'
            screen_index = int(args[1:])
        else:
            target_id = WINDOWS_OBJ.woof_id_to_window_id(int(args))
            screen_index = None

            if not WINDOWS_OBJ.exists(target_id):
                return

        WINDOWS_OBJ.add(plane_type, direction, target_id, screen_index)

    elif cmd == OPTIONS.ADD_VERTICAL:
        if args == '':
            print('\n'.join(WINDOWS_OBJ.list_add_windows(OPTIONS.ADD_VERTICAL)))
            return

        plane_type = PLANE.HORIZONTAL
        direction = DIR.DOWN
        if args[0] == 's':
            target_id = 's'
            screen_index = int(args[1:])
        else:
            target_id = WINDOWS_OBJ.woof_id_to_window_id(int(args))
            screen_index = None

            if not WINDOWS_OBJ.exists(target_id):
                return

        WINDOWS_OBJ.add(plane_type, direction, target_id, screen_index)

    elif cmd == OPTIONS.EXPAND_VERTICAL:
        increment = string_to_integer(args)
        WINDOWS_OBJ.resize_vertical('expand', increment)

    elif cmd == OPTIONS.REDUCE_VERTICAL:
        increment = string_to_integer(args)
        WINDOWS_OBJ.resize_vertical('reduce', increment)

    elif cmd == OPTIONS.EXPAND_HORIZONTAL:
        increment = string_to_integer(args)
        WINDOWS_OBJ.resize_horizontal('expand', increment)

    elif cmd == OPTIONS.REDUCE_HORIZONTAL:
        increment = string_to_integer(args)
        WINDOWS_OBJ.resize_horizontal('reduce', increment)

    elif cmd == OPTIONS.CHANGE_PLANE:
        WINDOWS_OBJ.change_plane()

    elif cmd == OPTIONS.SWAP_PANE:
        WINDOWS_OBJ.swap_pane_position()

    elif cmd == OPTIONS.SWAP:
        if args == '':
            log_debug(['No target found. Listing windows'])
            print('\n'.join(WINDOWS_OBJ.list_add_windows(OPTIONS.SWAP, True)))
            return

        target_id = string_to_integer(args)
        WINDOWS_OBJ.swap_windows(target_id)

    elif cmd == OPTIONS.MINIMIZE_ALL:
        WINDOWS_OBJ.minimize_all()

    elif cmd == OPTIONS.UNMINIMIZE_ALL:
        WINDOWS_OBJ.unminimize_all()

    elif cmd == OPTIONS.MAXIMIZE:
        if len(args) > 0:
            target_win_id = WINDOWS_OBJ.woof_id_to_window_id(string_to_integer(args))
        else:
            target_win_id = WINDOWS_OBJ.get_active_window()

        if not WINDOWS_OBJ.exists(target_win_id):
            exit(1)

        win_ids = WINDOWS_OBJ.windows[target_win_id].list_screen_windows()

        if WINDOWS_OBJ.windows[target_win_id].is_maximized():
            for win_id in win_ids:
                WINDOWS_OBJ.windows[win_id].activate()
                WINDOWS_OBJ.windows[win_id].set_size()

            WINDOWS_OBJ.windows[target_win_id].activate(True)
            WINDOWS_OBJ.windows[target_win_id].state = WINDOW_STATE.NORMAL
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
        next_active_window = WINDOWS_OBJ.kill_window(win_id)

        return_string = str(win_id) + "," + str(next_active_window)
        log_debug(['ReturnString:', return_string])
        print(return_string)

    elif cmd == OPTIONS.REMOVE:
        win_id = WINDOWS_OBJ.get_active_window()
        if not WINDOWS_OBJ.exists(win_id):
            exit(1)
        WINDOWS_OBJ.kill_window(win_id)

    elif cmd == OPTIONS.MOVE_TO:
        if args == '':
            log_debug(['No target id. Listing windows.'])
            print('\n'.join(WINDOWS_OBJ.list_add_windows(OPTIONS.MOVE_TO, True)))
            return

        main('rm')
        main('ah' + args)

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

        if args == '':
            log_debug(['No target id. Listing windows.'])
            print('\n'.join(WINDOWS_OBJ.list_add_windows(OPTIONS.ADD_TO_GROUP)))
            return

        target_id = WINDOWS_OBJ.woof_id_to_window_id(string_to_integer(args))
        WINDOWS_OBJ.add_to_window_group(target_id)

    elif cmd == OPTIONS.ACTIVATE_NEXT_WINDOW_IN_GROUP:
        WINDOWS_OBJ.activate_next_window(1)

    elif cmd == OPTIONS.ACTIVATE_PREV_WINDOW_IN_GROUP:
        WINDOWS_OBJ.activate_next_window(-1)

    elif cmd == OPTIONS.SWAP_SCREENS:
        if args == '':
            if WINDOWS_OBJ.exists(WINDOWS_OBJ.get_active_window()):
                print('\n'.join(WINDOWS_OBJ.list_screens(OPTIONS.SWAP_SCREENS, True)))
            else:
                log_error(["Attempted to list screens, but current window not registered, so could not exclude current screen"])
                return
        else:
            screen_index_b = parse_screen_index(args)
            try:
                screen_index_b, screen_index_a = args.split(',')[0], args.split(',')[1]
                screen_index_a = parse_screen_index(screen_index_a)
                screen_index_b = parse_screen_index(screen_index_b)
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
        # WINDOWS_OBJ.work_space.new_screen()
        WINDOWS_OBJ.work_space.update_statuses()

    elif cmd == OPTIONS.LIST_SCREENS:
        print('\n'.join(WINDOWS_OBJ.list_screens('', False, False)))

    elif cmd == OPTIONS.RENAME_SCREEN:
        name = args[1:]
        active_screen_index = WINDOWS_OBJ.get_active_screen()
        WINDOWS_OBJ.work_space.screens[active_screen_index].set_name(name)
        WINDOWS_OBJ.work_space.update_statuses()

    pickle.dump(WINDOWS_OBJ, open(DATA_PATH, "wb"))
    save_data()


def parse_screen_index(index):
    try:
        if index[0] == 'v':
            return WINDOWS_OBJ.work_space.viewable_screen_index_to_index(int(index[1:]))
        else:
            return int(index)
    except:
        return None


def save_data():
    pickle.dump(WINDOWS_OBJ, open(DATA_PATH, "wb"))


ARGS = sys.argv

try:
    WINDOWS_OBJ = pickle.load(open(DATA_PATH, "rb"))

    # Takes only about 4ms when all windows are valid
    if WINDOWS_OBJ.check_windows():
        WINDOWS_OBJ.restore_all()
except:
    WINDOWS_OBJ = Windows(SCREEN_CONFIG)

if len(ARGS) == 1:
    print_options(WINDOWS_OBJ)
    exit(0)

# Initialise a tree
if ARGS[1] == 'rl':
    WINDOWS_OBJ = Windows(SCREEN_CONFIG)
    save_data()
    exit(0)

if __name__ == '__main__':
    main(' '.join(ARGS[1:]))

exit(0)
