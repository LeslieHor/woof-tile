import pickle  # For saving the window structure to disk
import sys  # For getting args
from windows import Windows
from log import log_info, log_debug
from config import *
from enums import PLANE, DIR


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


def element(list_, index, default):
    try:
        return list_[index]
    except:
        return default


def main(args):
    cmd = args[1]
    log_info(['------- Start --------', 'Args:'] + args[1:])
    if cmd == 'debug':
        debug_print()
    elif cmd == 'restore':
        WINDOWS_OBJ.restore_all()
    elif cmd == 'list':
        print(WINDOWS_OBJ.list_add_windows(args[2]))
    elif cmd == 'add':
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
    elif cmd == 'ev':
        increment = element(args, 2, None)
        if increment is not None:
            increment = int(increment)
        log_debug(['Attempting to expand vertical size.'])
        WINDOWS_OBJ.resize_vertical('expand', increment)
    elif cmd == 'rv':
        log_debug(['Attempting to reduce vertical size.'])
        increment = element(args, 2, None)
        if increment is not None:
            increment = int(increment)
        WINDOWS_OBJ.resize_vertical('reduce', increment)
    elif cmd == 'eh':
        log_debug(['Attempting to expand horizontal size.'])
        increment = element(args, 2, None)
        if increment is not None:
            increment = int(increment)
        WINDOWS_OBJ.resize_horizontal('expand', increment)
    elif cmd == 'rh':
        increment = element(args, 2, None)
        if increment is not None:
            increment = int(increment)
        log_debug(['Attempting to reduce horizontal size.'])
        WINDOWS_OBJ.resize_horizontal('reduce', increment)
    elif cmd == 'change-plane':
        WINDOWS_OBJ.change_plane()
    elif cmd == 'swap-pane':
        WINDOWS_OBJ.swap_pane_position()
    elif cmd == 'swap':
        if len(args) < 3:
            log_debug(['No target found. Listing windows'])
            print(WINDOWS_OBJ.list_add_windows("swap ", True))
            return

        target_id = int(args[2])
        WINDOWS_OBJ.swap_windows(target_id)
    elif cmd == 'min':
        WINDOWS_OBJ.minimize_all()
    elif cmd == 'unmin':
        WINDOWS_OBJ.unminimize_all()
    elif cmd == 'maximize':
        if len(args) > 2:
            win_id = int(args[2])
        else:
            win_id = WINDOWS_OBJ.get_active_window()
        if not WINDOWS_OBJ.exists(win_id):
            exit(1)
        win_ids = WINDOWS_OBJ.windows[win_id].list_screen_windows()
        if WINDOWS_OBJ.windows[win_id].Maximized:
            for win_id in win_ids:
                WINDOWS_OBJ.windows[win_id].activate()
                WINDOWS_OBJ.windows[win_id].set_size()

            WINDOWS_OBJ.windows[win_id].activate()
            WINDOWS_OBJ.windows[win_id].maximized = False
        else:
            for win_id in win_ids:
                if win_id == win_id:
                    continue
                WINDOWS_OBJ.windows[win_id].minimize()
            WINDOWS_OBJ.windows[win_id].maximize()
    elif cmd == 'kill':
        win_id = WINDOWS_OBJ.get_active_window()
        if not WINDOWS_OBJ.exists(win_id):
            exit(1)
        win_id_hex = WINDOWS_OBJ.windows[win_id].window_id_hex
        next_active_window = WINDOWS_OBJ.kill_window(win_id)
        return_string = win_id_hex + "," + str(next_active_window)
        log_debug(['ReturnString:', return_string])
        print(return_string)
    elif cmd == 'remove':
        win_id = WINDOWS_OBJ.get_active_window()
        if not WINDOWS_OBJ.exists(win_id):
            exit(1)
        WINDOWS_OBJ.kill_window(win_id)
    elif cmd == 'move-to':
        if len(args) < 3:
            log_debug(['No target id. Listing windows.'])
            print(WINDOWS_OBJ.list_add_windows("move-to ", True))
            return

        main(['', 'remove'])
        main(['', 'add', 'h', args[2]])
    elif cmd == 'nav-right':
        WINDOWS_OBJ.nav_right()
    elif cmd == 'nav-left':
        WINDOWS_OBJ.nav_left()
    elif cmd == 'nav-up':
        WINDOWS_OBJ.nav_up()
    elif cmd == 'nav-down':
        WINDOWS_OBJ.nav_down()
    elif cmd == 'add-to-group':
        if WINDOWS_OBJ.exists(WINDOWS_OBJ.get_active_window()):
            exit(1)
        if len(args) < 3:
            log_debug(['No target id. Listing windows.'])
            print(WINDOWS_OBJ.list_add_windows("add-to-group "))
            return

        target_id = args[2]
        WINDOWS_OBJ.add_to_window_group(target_id)
    elif cmd == 'activate-next-window':
        WINDOWS_OBJ.activate_next_window(1)
    elif cmd == 'activate-prev-window':
        WINDOWS_OBJ.activate_next_window(-1)

    pickle.dump(WINDOWS_OBJ, open(DATA_PATH, "wb"))


# TODO: Seriously, clean up this code
# Initialise a tree
if sys.argv[1] == 'reload':
    WINDOWS_OBJ = Windows(4, 3, 5760, 1080)
else:
    WINDOWS_OBJ = pickle.load(open(DATA_PATH, "rb"))
    if WINDOWS_OBJ.check_windows():
        WINDOWS_OBJ.restore_all()

ARGS = sys.argv

if __name__ == '__main__':
    main(ARGS)

exit(0)
