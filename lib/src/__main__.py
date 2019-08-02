import sys  # For getting args
import json
import os

import layouts
from empty_container import EmptyContainer
from group_node import GroupNode
from tree_manager import TreeManager
from split_node import SplitNode
from container import Container
from log import log_info, log_error
import config
from enums import PLANE, WINDOW_STATE, OPTIONS, print_options
import helpers
import system_calls
from workspace import Workspace


def check_window():
    if get_active_window() is None:
        log_error(["Window not in woof"])
        exit(0)


def create_new_window_from_active():
    new_window_id = system_calls.get_active_window_id()
    new_woof_id = tree_manager.get_new_woof_id()

    return Container(window_id=new_window_id, woof_id=new_woof_id)


def create_new_split_node(plane_type, child_1, child_2):
    split_node = SplitNode(plane_type=plane_type)
    split_node.set_children([child_1, child_2])

    return split_node


def create_new_group_node(target, window):
    parent = target.get_parent()
    group_node = GroupNode()
    group_node.set_children([window, target])
    parent.replace_child(target, group_node)

    return group_node

def is_window_registered_in_woof(window_id):
    return tree_manager.get_window_from_window_id(window_id) != None


def get_active_window():
    window_id = system_calls.get_active_window_id()
    return tree_manager.get_window_from_window_id(window_id)


def get_active_workspace_index():
    window = get_active_window()
    return window.get_workspace_index()


def get_active_workspace():
    index = get_active_workspace_index()
    return tree_manager.get_child(index)


def debug_print():
    json_data = tree_manager.to_json()
    print(json.dumps(json_data))


def restore_all():
    tree_manager.redraw()


def print_interactable_endpoints(prepend=''):
    active_window = get_active_window()
    interactable_endpoints_strings = [prepend + ep.get_ui_string()
                                      for ep in
                                      tree_manager.get_interactable_endpoints()
                                      if ep != active_window]
    interactable_endpoints_strings.sort()
    print('\n'.join(interactable_endpoints_strings))


def print_interactable_windows(prepend=''):
    active_window = get_active_window()
    interactable_windows = [win for
                            win in tree_manager.get_interactable_endpoints()
                            if isinstance(win, Container)]
    interactable_windows_strings = [prepend + win.get_ui_string()
                                    for win in interactable_windows
                                    if win != active_window]
    interactable_windows_strings.sort()
    print('\n'.join(interactable_windows_strings))


def print_workspaces(prepend=''):
    active_workspace = get_active_workspace()
    workspace_strings = [prepend + 's' +
                         str(tree_manager.get_active_workspace_index(ws)) +
                         " : " + ws.get_name()
                         for ws in tree_manager.get_active_workspaces()
                         if ws != active_workspace]
    workspace_strings += [prepend + str(tree_manager.get_workspace_index(ws)) +
                          " : " + ws.get_name()
                          for ws in tree_manager.get_children()
                          if ws != active_workspace]
    print('\n'.join(workspace_strings))


def remove_pre_existing_window(window_id):
    window = tree_manager.get_window_from_window_id(window_id)
    if not window:
        return False

    window.remove_and_trim()
    restore_all()
    return True


def add_to_screen(target_screen):
    workspace = tree_manager.get_viewable_workspace(int(target_screen))
    new_window = create_new_window_from_active()
    remove_pre_existing_window(new_window.get_window_id())

    workspace.add_child(new_window)
    new_window.activate(True)


def add_split_last_active_window(plane_type):
    last_active_window = tree_manager.get_last_active_window()
    subtree = last_active_window.get_smallest_immutable_subtree()
    parent = subtree.get_parent()
    new_window = create_new_window_from_active()
    remove_pre_existing_window(new_window.get_window_id())

    new_split_node = create_new_split_node(plane_type, subtree, new_window)

    parent.replace_child(subtree, new_split_node)
    new_split_node.redraw()
    new_window.activate(True)


def add_split_woof_id(plane_type, target_woof_id):
    target_woof_id = target_woof_id if type(target_woof_id) is int else int(target_woof_id)
    target_window = tree_manager.get_window_from_woof_id(int(target_woof_id))
    subtree = target_window.get_smallest_immutable_subtree()
    parent = subtree.get_parent()
    new_window = create_new_window_from_active()
    remove_pre_existing_window(new_window.get_window_id())

    new_split_node = create_new_split_node(plane_type, target_window, new_window)

    parent.replace_child(subtree, new_split_node)
    new_split_node.redraw()
    new_window.activate(True)


def add_horizontal(target_window):
    if target_window == '':
        print_interactable_endpoints(OPTIONS.ADD_HORIZONTAL)
    elif target_window == 'l':
        add_split_last_active_window(PLANE.VERTICAL)
    elif target_window[0] == 's':
        add_to_screen(target_window[1:])
    else:
        add_split_woof_id(PLANE.VERTICAL, target_window)


def add_vertical(target_window):
    if target_window == '':
        print_interactable_endpoints(OPTIONS.ADD_VERTICAL)
    elif target_window == 'l':
        add_split_last_active_window(PLANE.HORIZONTAL)
    elif target_window[0] == 's':
        add_to_screen(target_window[1:])
    else:
        add_split_woof_id(PLANE.HORIZONTAL, target_window)


def expand_vertical(increment):
    check_window()
    if increment == '':
        increment = config.get_config('resize_increment')
    else:
        increment = int(increment)
    window = get_active_window()
    window.resize_vertical(increment)


def reduce_vertical(increment):
    check_windows()
    if increment == '':
        increment = -1 * config.get_config('resize_increment')
    else:
        increment = -1 * int(increment)
    window = get_active_window()
    window.resize_vertical(increment)


def expand_horizontal(increment):
    check_windows()
    if increment == '':
        increment = config.get_config('resize_increment')
    else:
        increment = int(increment)
    window = get_active_window()
    window.resize_horizontal(increment)


def reduce_horizontal(increment):
    check_windows()
    if increment == '':
        increment = -1 * config.get_config('resize_increment')
    else:
        increment = -1 * int(increment)
    window = get_active_window()
    window.resize_horizontal(increment)


def change_plane():
    check_windows()
    window = get_active_window()
    window.change_plane()


def swap(target_id):
    if target_id == '':
        print_interactable_endpoints(OPTIONS.SWAP)
        return

    container_1 = get_active_window()
    container_2 = tree_manager.get_window_from_woof_id(int(target_id))

    swap_containers(container_1, container_2)


def swap_containers(container_1, container_2):
    parent_1 = container_1.get_parent()
    parent_2 = container_2.get_parent()

    index_1 = parent_1.get_child_index(container_1)
    index_2 = parent_2.get_child_index(container_2)

    parent_1.set_child(index_1, container_2)
    parent_2.set_child(index_2, container_1)

    parent_1.redraw()
    parent_2.redraw()


def swap_pane_positions():
    check_windows()
    active_window = get_active_window()
    split_node = active_window.get_split_node()
    [child_1, child_2] = split_node.get_children()
    split_node.set_children([child_2, child_1])
    inverse_split_ratio = 1.0 - split_node.get_split_ratio()
    split_node.set_split_ratio(inverse_split_ratio)
    split_node.redraw()


def minimize_all():
    tree_manager.minimize()


def maximize():
    check_windows()
    window = get_active_window()
    if window.get_state() == WINDOW_STATE.MAXIMIZED:
        do_unmaximize()
    else:
        do_maximize()


def do_maximize():
    window = get_active_window()
    workspace = get_active_workspace()
    [w.minimize() for w in workspace.get_all_windows() if w != window]
    window.maximize()


def do_unmaximize():
    window = get_active_window()
    workspace = get_active_workspace()
    windows = workspace.get_all_windows()
    [w.unminimize() for w in windows if w != window]
    window.unmaximize()
    window.activate()


def remove():
    check_windows()
    window = get_active_window()
    window.remove_and_trim()
    restore_all()  # TODO: Only need to call the survivor to redraw I think
    return window


def kill():
    check_windows()
    window = remove()
    log_info(system_calls.kill_window(window.get_window_id()))


def move_to(target_window):
    check_windows()
    if target_window == '':
        print_interactable_endpoints(OPTIONS.MOVE_TO)
        return

    remove()
    add_horizontal(target_window)


def add_to_group(target_woof_id):
    if target_woof_id == '':
        print_interactable_windows(OPTIONS.ADD_TO_GROUP)
        return
    elif target_woof_id == 'l':
        target = tree_manager.get_last_active_window()
    else:
        target = tree_manager.get_window_from_woof_id(int(target_woof_id))

    window = create_new_window_from_active()
    remove_pre_existing_window(window.get_window_id())
    add_to_group_target(target, window)


def add_to_group_target(target_window, new_window):
    if target_window.is_in_group_node():
        group_node = target_window.get_parent()
        group_node.add_child(new_window)
    else:
        group_node = create_new_group_node(target_window, new_window)

    group_node.redraw()


def activate_next_window_in_group():
    check_windows()
    window = get_active_window()
    if not window.is_in_group_node():
        return
    rotate_window_in_group(1)


def activate_prev_window_in_group():
    check_windows()
    window = get_active_window()
    if not window.is_in_group_node():
        return
    rotate_window_in_group(-1)


def rotate_window_in_group(increment):
    window = get_active_window()
    parent = window.get_parent()
    parent.rotate_active_window(increment)


def swap_screens(target):
    """
    1. x
    2. sx
    3. x,x
    4. x,sx
    5. sx,x
    6. sx,sx
    """
    check_windows()
    if target == '':
        print_workspaces(OPTIONS.SWAP_SCREENS)
        return

    targets = target.split(',')
    target_1 = targets[0]
    target_2 = None if len(targets) == 1 else targets[1]
    workspace_1 = get_screen_target(target_1)
    workspace_2 = get_screen_target(target_2)
    do_swap_screens(workspace_2, workspace_1)  # Flipped to move focus to
                                               # non-active workspace


def get_screen_target(target=None):
    if target is None:
        return get_active_workspace()
    elif target[0] == 's':
        index = int(target[1:])
        return tree_manager.get_active_workspace(index)
    else:
        index = int(target)
        return tree_manager.get_workspace(index)


def do_swap_screens(screen_1, screen_2):
    screen_1_active = screen_1.is_active()
    screen_2_active = screen_2.is_active()
    screen_1_geometry = screen_1.get_geometry()
    screen_2_geometry = screen_2.get_geometry()

    if (screen_1_active, screen_2_active) == (True, True):
        screen_1.set_active(screen_2_geometry)
        screen_2.set_active(screen_1_geometry)
        screen_2.activate_last_active_window()
    elif (screen_1_active, screen_2_active) == (True, False):
        screen_1.set_inactive()
        screen_2.set_active(screen_1_geometry)
        screen_2.activate_last_active_window()
    elif (screen_1_active, screen_2_active) == (False, True):
        screen_1.set_active(screen_2_geometry)
        screen_2.set_inactive()
        screen_1.activate_last_active_window()

    tree_manager.update_active_workspaces_statuses()


def new_workspace(name):
    if name == '':
        name = None
    else:
        name = name.lstrip()
    tree_manager.add_workspace(name)
    tree_manager.update_active_workspaces_statuses()


def list_screens():
    print_workspaces()


def rename_screen(name):
    check_windows()
    if name == '':
        name = None
    else:
        name = name.lstrip()

    workspace = get_active_workspace()
    workspace.set_name(name)
    tree_manager.update_active_workspaces_statuses()


def swap_screen_left():
    check_windows()
    active_screen_index = tree_manager.get_active_workspace_index(
        get_active_workspace())
    left_index = (active_screen_index - 1) % \
                 tree_manager.get_active_workspaces_count()

    active_workspace = tree_manager.get_active_workspace(active_screen_index)
    left_workspace = tree_manager.get_active_workspace(left_index)

    do_swap_screens(active_workspace, left_workspace)


def swap_screen_right():
    check_windows()
    active_screen_index = tree_manager.get_active_workspace_index(
        get_active_workspace())
    right_index = (active_screen_index + 1) % \
                  tree_manager.get_active_workspaces_count()

    active_workspace = tree_manager.get_active_workspace(active_screen_index)
    right_workspace = tree_manager.get_active_workspace(right_index)

    do_swap_screens(active_workspace, right_workspace)


def move_mouse():
    window = get_active_window()
    window.move_mouse()


def load_layout_data(name):
    return layouts.get_layout(name)


def create_layout_tree(name):
    layout_data = load_layout_data(name)
    return generate_layout_tree(layout_data)


def generate_layout_tree(layout_data):
    if layout_data['type'] == 'empty_container':
        window_class = layout_data.get('window_class')
        window_title = layout_data.get('window_title', None)

        return EmptyContainer(window_class=window_class,
                              window_title=window_title)

    elif layout_data['type'] == 'container':
        window_id = layout_data.get('window_id')
        woof_id = layout_data.get('woof_id')
        state = layout_data.get('state')
        window_class = layout_data.get('window_class')

        return Container(window_id=window_id,
                         woof_id=woof_id,
                         state=state,
                         window_class=window_class)

    elif layout_data['type'] == 'split_node':
        split_ratio = layout_data.get('split_ratio')
        plane_type = layout_data.get('plane_type')

        split_node = SplitNode(split_ratio=split_ratio,
                               plane_type=plane_type)
        children = [generate_layout_tree(c) for c in layout_data['children']]
        split_node.set_children(children)

        return split_node

    elif layout_data['type'] == 'group_node':
        group_node = GroupNode()

        children = [generate_layout_tree(c) for c in layout_data['children']]
        group_node.set_children(children)

        return group_node

    elif layout_data['type'] == 'tree_manager':
        viewable_screen_count = layout_data.get('viewable_screen_count')
        last_active_window_id = layout_data.get('last_active_window_id')
        tm = TreeManager(viewable_screen_count=viewable_screen_count,
                         last_active_window_id=last_active_window_id)

        children = [generate_layout_tree(c) for c in layout_data['children']]
        tm.set_children(children)

        return tm

    elif layout_data['type'] == 'workspace':
        name = layout_data.get('name')
        geometry = layout_data.get('geometry')
        state = layout_data.get('state')
        last_active_window_id = layout_data.get('last_active_window_id')

        workspace = Workspace(name=name,
                              geometry=geometry,
                              state=state,
                              last_active_window_id=last_active_window_id)

        children = [generate_layout_tree(c) for c in layout_data['children']]
        workspace.set_children(children)

        return workspace


def load_layout_to_screen(screen_target, layout_name):
    workspace = get_screen_target(screen_target)
    if workspace.get_child_count() > 0:
        print("Can only apply layouts to empty screens")
    layout_tree = create_layout_tree(layout_name)
    workspace.add_child(layout_tree)
    layout_tree.restore_splits()


def load_layout(args):
    check_windows()
    if args == '':
        print_layouts('ll')
        return
    args = args.split(',')
    screen_target = args[0]
    layout_name = args[1]
    load_layout_to_screen(screen_target, layout_name)


def print_layouts(prepend=''):
    screens_layout_names = []
    number_of_screens = tree_manager.get_viewable_screen_count()
    for name in layouts.get_layout_names():
        s = [prepend + 's' + str(x) + ',' + name
             for x in range(number_of_screens)
             if tree_manager.get_active_workspace(x).get_child_count() == 0]
        screens_layout_names += s

    print('\n'.join(screens_layout_names))


def save_layout(args):
    check_windows()
    name = args.lstrip()

    active_workspace = get_active_workspace()

    json_data = active_workspace.get_layout_json()

    with open(config.get_config('layouts_dir') + "/" + name, 'w') as f:
        json.dump(json_data, f, indent=4, sort_keys=True)


def attempt_swallow():
    window_ids_in_woof = [win.get_window_id()
                          for win in tree_manager.get_all_windows()]
    non_reg_window_ids = [win
                          for win in system_calls.get_all_system_window_ids()
                          if win not in window_ids_in_woof]
    windows = [{'window_id': wid,
                'window_class': system_calls.get_window_class(wid),
                'window_title': system_calls.get_window_title(wid)}
               for wid in non_reg_window_ids]

    empty_containers = tree_manager.get_empty_containers()

    # Attempt to match on title first
    for ec in empty_containers:
        if ec.get_window_title() is None:
            continue

        title_matches = [win for win in windows
                         if ec.get_window_title() in win.get('window_title')]

        if len(title_matches) > 0:
            chosen_window = title_matches[0]

            new_woof_id = tree_manager.get_new_woof_id()
            new_window = Container(window_id=chosen_window.get('window_id'),
                                   woof_id=new_woof_id)
            ec.swallow(new_window)
            new_window.redraw()

            windows.remove(chosen_window)

    empty_containers = tree_manager.get_empty_containers()

    # Attempt to match on class
    for ec in empty_containers:
        class_matches = [win for win in windows
                         if ec.get_window_class() == win.get('window_class')]

        if len(class_matches) > 0:
            chosen_window = class_matches[0]

            new_woof_id = tree_manager.get_new_woof_id()
            new_window = Container(window_id=chosen_window.get('window_id'),
                                   woof_id=new_woof_id)

            ec.swallow(new_window)
            new_window.redraw()

            windows.remove(chosen_window)


# TODO: These should all be changed. I left it alone because I can't be bothered
# TODO: to change it yet
def left_window():
    window = get_active_window()
    ((l, t), (_, _)) = window.get_viewport()
    closest_valid_border = 0
    lowest_top_diff = sys.maxint
    closest_window = None

    for win in tree_manager.get_viewable_windows():
        if win.is_shaded() or win.is_minimized():
            continue

        ((wl, wt), (ww, wh)) = win.get_viewport()
        wr = wl + ww
        if l < wr or wr < closest_valid_border:
            continue

        top_border_diff = (t - wt) ** 2  # Magnitude of diff

        if wr == closest_valid_border:  # Only compare when the borders are same
                                        # distance apart
            if lowest_top_diff < top_border_diff or \
               (lowest_top_diff == top_border_diff and t < wt):
                continue

            # When two windows are equally apart. Take the to one with greater
            # overlap
            # +------+ +-----+
            # |      | |     |
            # |  1   | +-----+
            # |      | +-----+
            # |      | |  0  |
            # +------+ +-----+
            # +------+
            # |      |
            # |      |
            # |      |
            # |      |
            # +------+
            # 0 Should switch to 1

        closest_valid_border = wr
        lowest_top_diff = top_border_diff
        closest_window = win

    return closest_window


def down_window():
    window = get_active_window()
    ((l, t), (_, h)) = window.get_viewport()
    b = t + h
    closest_top_border = sys.maxint
    lowest_left_diff = sys.maxint
    closest_window = None

    for win in tree_manager.get_viewable_windows():
        if win.is_shaded() or win.is_minimized():
            continue

        ((wl, wt), (_, _)) = win.get_viewport()

        if wt < b or closest_top_border < wt:
            continue

        left_border_diff = (l - wl) ** 2  # Magnitude of diff
        if wt == closest_top_border:
            if lowest_left_diff < left_border_diff or \
              (lowest_left_diff == left_border_diff and wl > l):
                continue

        closest_top_border = wt
        lowest_left_diff = left_border_diff
        closest_window = win

    return closest_window


def up_window():
    window = get_active_window()
    ((l, t), (_, _)) = window.get_viewport()
    closest_bottom_border = 0
    lowest_left_diff = sys.maxint
    closest_window = None

    for win in tree_manager.get_viewable_windows():
        if win.is_shaded() or win.is_minimized():
            continue

        ((wl, wt), (ww, wh)) = win.get_viewport()
        wb = wt + wh
        if t < wb or wb < closest_bottom_border:
            continue

        left_border_diff = (l - wl) ** 2  # Magnitude of diff
        if wb == closest_bottom_border:
            if lowest_left_diff < left_border_diff or \
               (lowest_left_diff == left_border_diff and wl > l):
                continue

        closest_bottom_border = wb
        lowest_left_diff = left_border_diff
        closest_window = win

    return closest_window


def right_window():
    window = get_active_window()
    ((l, t), (w, _)) = window.get_viewport()
    r = l + w
    closest_left_border = sys.maxint
    lowest_top_diff = sys.maxint
    closest_window = None

    for win in tree_manager.get_viewable_windows():
        if win.is_shaded() or win.is_minimized():
            continue

        ((wl, wt), (_, _)) = win.get_viewport()

        if wl < r or closest_left_border < wl:
            continue

        top_border_diff = (t - wt) ** 2  # Magnitude of diff
        if wl == closest_left_border:
            if lowest_top_diff < top_border_diff or \
               (lowest_top_diff == top_border_diff and t < wt):
                continue

        closest_left_border = wl
        lowest_top_diff = top_border_diff
        closest_window = win

    return closest_window


# TODO: These need error correction for when you don't find a window
def navigate_left():
    check_windows()
    left_window().activate(True)


def navigate_down():
    check_windows()
    down_window().activate(True)


def navigate_up():
    check_windows()
    up_window().activate(True)


def navigate_right():
    check_windows()
    right_window().activate(True)


def swap_left():
    check_windows()
    swap_containers(get_active_window(), left_window())


def swap_down():
    check_windows()
    swap_containers(get_active_window(), down_window())


def swap_up():
    check_windows()
    swap_containers(get_active_window(), up_window())


def swap_right():
    check_windows()
    swap_containers(get_active_window(), right_window())


def main(command_string):
    global tree_manager

    cmd = command_string[:2]
    args = command_string[2:]
    args = helpers.cut_off_rest(args)

    if cmd == OPTIONS.DEBUG:
        debug_print()

    elif cmd == OPTIONS.RESTORE:
        restore_all()

    elif cmd == OPTIONS.LIST:
        print_interactable_endpoints()

    elif cmd == OPTIONS.ADD_HORIZONTAL:
        add_horizontal(args)

    elif cmd == OPTIONS.ADD_VERTICAL:
        add_vertical(args)

    elif cmd == OPTIONS.EXPAND_VERTICAL:
        expand_vertical(args)

    elif cmd == OPTIONS.REDUCE_VERTICAL:
        reduce_vertical(args)

    elif cmd == OPTIONS.EXPAND_HORIZONTAL:
        expand_horizontal(args)

    elif cmd == OPTIONS.REDUCE_HORIZONTAL:
        reduce_horizontal(args)

    elif cmd == OPTIONS.CHANGE_PLANE:
        change_plane()

    elif cmd == OPTIONS.SWAP_PANE:
        swap_pane_positions()

    elif cmd == OPTIONS.SWAP:
        swap(args)

    elif cmd == OPTIONS.MINIMIZE_ALL:
        minimize_all()  # TODO: Gotta think about things about how to restore
                        # TODO: them all

    elif cmd == OPTIONS.MAXIMIZE:
        maximize()

    elif cmd == OPTIONS.KILL:
        kill()

    elif cmd == OPTIONS.REMOVE:
        remove()

    elif cmd == OPTIONS.MOVE_TO:
        move_to(args)

    elif cmd == OPTIONS.NAV_LEFT:
        navigate_left()

    elif cmd == OPTIONS.NAV_RIGHT:
        navigate_right()

    elif cmd == OPTIONS.NAV_UP:
        navigate_up()

    elif cmd == OPTIONS.NAV_DOWN:
        navigate_down()

    elif cmd == OPTIONS.ADD_TO_GROUP:
        add_to_group(args)

    elif cmd == OPTIONS.ACTIVATE_NEXT_WINDOW_IN_GROUP:
        activate_next_window_in_group()

    elif cmd == OPTIONS.ACTIVATE_PREV_WINDOW_IN_GROUP:
        activate_prev_window_in_group()

    elif cmd == OPTIONS.SWAP_SCREENS:
        swap_screens(args)

    elif cmd == OPTIONS.NEW_SCREEN:
        new_workspace(args)

    elif cmd == OPTIONS.LIST_SCREENS:
        list_screens()

    elif cmd == OPTIONS.RENAME_SCREEN:
        rename_screen(args)

    elif cmd == OPTIONS.SWAP_SCREEN_LEFT:
        swap_screen_left()

    elif cmd == OPTIONS.SWAP_SCREEN_RIGHT:
        swap_screen_right()

    elif cmd == OPTIONS.SWAP_PANE_LEFT:
        swap_left()

    elif cmd == OPTIONS.SWAP_PANE_RIGHT:
        swap_right()

    elif cmd == OPTIONS.SWAP_PANE_UP:
        swap_up()

    elif cmd == OPTIONS.SWAP_PANE_DOWN:
        swap_down()

    elif cmd == OPTIONS.MOVE_MOUSE:
        move_mouse()

    elif cmd == OPTIONS.LOAD_LAYOUT:
        load_layout(args)

    elif cmd == OPTIONS.ATTEMPT_SWALLOW:
        attempt_swallow()

    elif cmd == OPTIONS.SAVE_LAYOUT:
        save_layout(args)

    else:
        print("Invalid command")

    save_data()


def check_windows():
    system_ids = system_calls.get_all_system_window_ids()
    dead_windows = [win for win in tree_manager.get_all_windows()
                    if win.window_id not in system_ids]
    [win.remove_and_trim() for win in dead_windows]
    return len(dead_windows) > 0


def load_data():
    global tree_manager
    if os.path.isfile(config.get_config('data_path')):
        with open(config.get_config('data_path')) as json_file:
            json_data = json.load(json_file)
            tree_manager = generate_layout_tree(json_data)
        if check_windows():
            restore_all()
    else:
        tree_manager = TreeManager()
        tree_manager.initialise_workspaces()


def save_data():
    json_data = tree_manager.to_json()
    with open(config.get_config('data_path'), 'w') as f:
        json.dump(json_data, f)


ARGS = sys.argv

if len(ARGS) <= 1:
    exit(0)

if ARGS[1] == 'rl':  # Just in case things go wrong
    tree_manager = TreeManager()
    tree_manager.initialise_workspaces()
    save_data()
    exit(0)
else:
    load_data()

if ARGS[1] == 'help':
    print_options(tree_manager)
    exit(0)

log_info(['------- Start --------', 'Args:'] + ARGS)

start_time = 0.0  # Just to get rid of IDE warnings
if config.get_config('benchmark'):
    import time

    start_time = time.time()

if __name__ == '__main__':
    main(' '.join(ARGS[1:]))

if config.get_config('benchmark'):
    end_time = time.time()
    log_info(['Benchmark:', (end_time - start_time), 'seconds'])

exit(0)
