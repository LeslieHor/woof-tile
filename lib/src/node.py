from functools import reduce
import helpers


class Node:
    def __init__(self, child_limit):
        self.parent = None
        self.children = []
        self.child_limit = child_limit

    # ------------------------------------------------------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------------------------------------------------------

    def get_parent(self):
        return self.parent

    def get_children(self):
        return self.children

    def get_child_count(self):
        return len(self.children)

    def get_child(self, index):
        return self.children[index]

    def get_child_limit(self):
        return self.child_limit

    def get_child_index(self, child):
        return self.children.index(child)

    def get_all_windows(self):
        return reduce(lambda acc, l: helpers.combine_lists(l.get_all_windows(), acc),
                      self.get_children(), [])

    # ------------------------------------------------------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------------------------------------------------------

    def set_parent(self, new_parent):
        self.parent = new_parent

    def set_children(self, new_children):
        self.children = new_children
        [c.set_parent(self) for c in self.get_children()]

    def set_child(self, index, child):
        self.children[index] = child
        child.set_parent(self)

    def replace_child(self, calling_child, new_child):
        index = self.get_child_index(calling_child)
        self.set_child(index, new_child)
        new_child.set_parent(self)

    def add_child(self, new_child):
        if self.get_child_limit() <= self.get_child_count() and self.get_child_limit() is not None:
            raise Exception("Cannot add child")
        self.children.append(new_child)
        new_child.set_parent(self)
        self.redraw()

    def remove_child(self, child):
        self.children.remove(child)

    # ------------------------------------------------------------------------------------------------------------------
    # Trickle downs
    # ------------------------------------------------------------------------------------------------------------------

    def to_json(self):
        if self.get_child_count() == 0:
            children = "[]"
        else:
            children = '[' + ','.join([c.to_json() for c in self.get_children()]) + ']'

        json = ''
        json += '"child_limit":' + helpers.json_com(self.get_child_limit()) + ','
        json += '"children":' + children

        return json

    def redraw(self):
        [c.redraw() for c in self.get_children()]

    def minimize(self):
        [c.minimize() for c in self.get_children()]

    def unminimize(self):
        [c.unminimize() for c in self.get_children()]

    def get_interactable_endpoints(self):
        return reduce(lambda a, c: helpers.combine_lists(c.get_interactable_endpoints(), a), self.get_children(), [])

    def is_any_maximized(self):
        return any([c.is_any_maximized() for c in self.get_children()])

    def restore_splits(self):
        [c.restore_splits() for c in self.get_children()]

    # ------------------------------------------------------------------------------------------------------------------
    # Bubble ups
    # ------------------------------------------------------------------------------------------------------------------

    def get_workspace_index(self, _=None):
        return self.parent.get_workspace_index(self)

    def set_window_active(self, calling_child):
        self.parent.set_window_active(calling_child)

    def change_plane(self):
        self.parent.change_plane()

    def update_status(self):
        self.parent.update_status()

    def set_active_window(self, window):
        self.parent.set_window_active(window)

    def get_split_node(self):
        return self.parent.get_split_node()

    def get_workspace_viewport(self):
        return self.parent.get_workspace_viewport()

    def get_smallest_immutable_subtree(self, _):
        return self.parent.get_smallest_immutable_subtree(self)

    # ------------------------------------------------------------------------------------------------------------------
    # Other
    # ------------------------------------------------------------------------------------------------------------------

    def replace_self(self, replacement):
        self.parent.replace_child(self, replacement)

    def remove_self(self):
        if self.get_child_count() != 1:
            return
        self.replace_self(self.get_child(0))

    def remove_and_trim(self, calling_child):
        self.remove_child(calling_child)
        if self.get_child_count() == 1:
            [c.unshade() for c in self.get_children()]
            self.remove_self()
