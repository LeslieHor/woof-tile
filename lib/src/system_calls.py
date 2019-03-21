import subprocess
from helpers import join_and_sanitize
from log import log_debug
import time


def call(command, response=True):
    """Call into the system and run Command (string)"""
    s = time.time()
    cmd = join_and_sanitize(command)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    result, _err = proc.communicate()
    e = time.time()
    log_debug(["subprocess command:", cmd])
    log_debug(["subprocess time:", (e - s)])
    return result


def verify_window_id(window_id):
    if window_id is None:
        return get_active_window()
    else:
        return window_id


def get_active_window():
    return int(call('xdotool getactivewindow').rstrip())


def activate_window(window_id):
    call(['xdotool windowactivate', window_id])


def get_window_state(window_id=None):
    """Gets the windows state using xprop

     States:
     <BLANK> : Normal
     _NET_WM_STATE_SHADED : Shaded
     _NET_WM_STATE_HIDDEN : Minimized

     """
    return call(['xprop', '-id', verify_window_id(window_id),
                 ' | grep "NET_WM_STATE" | sed \'s/_NET_WM_STATE(ATOM) = //\'']).rstrip()


def get_window_class(window_id=None):
    return call(['xprop -id', verify_window_id(window_id), '| grep WM_CLASS |  sed \'s/^.*, "//\' | sed \'s/"//\'']).rstrip()


def get_window_title(window_id=None):
    return call(['xdotool getwindowname', verify_window_id(window_id)]).rstrip()


def minimise_window(window_id=None):
    call(['xdotool windowminimize', verify_window_id(window_id)])


# TODO: Default window_id to None
def set_window_geometry(window_id, px, py, sx, sy):
    # xdotool will not override the plasma panel border
    # wmctrl is very particular about its args
    mvarg = '0,' + str(px) + ',' + str(py) + ',' + str(sx) + ',' + str(sy)
    call(['wmctrl -ir', window_id, '-e', mvarg], False)


def shade_window(window_id=None):
    call(['wmctrl', '-ir', verify_window_id(window_id), '-b', 'add,shaded'])


def unshade_window(window_id=None):
    call(['wmctrl', '-ir', verify_window_id(window_id), '-b', 'remove,shaded'])


def get_hex_ids():
    hex_ids_str = call('wmctrl -l | awk -F" " \'$2 == 0 {print $1}\'')
    hex_ids = hex_ids_str.split("\n")
    return hex_ids


def remove_system_maximize(window_id=None):
    call(["wmctrl", "-ir", verify_window_id(window_id), "-b", "remove,maximized_vert,maximized_horz"])
