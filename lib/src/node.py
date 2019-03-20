from enums import *


class Node:
    """Node of the tree

    Contains two children, which can be nodes or children.
    PlaneType defines whether the node is split horizontally or vertically
    """

    def __init__(self, plane_type):
        self.plane_type = plane_type

        self.parent = None
        self.child_a = None
        self.child_b = None

    def debug_print(self, level):
        if self.plane_type == PLANE.HORIZONTAL:
            plane_type_str = "H"
        else:
            plane_type_str = "V"
        l, d, u, r = self.parent.get_borders(self)
        print(" " * level + "N (" + plane_type_str + ") " + str(self.split_coordinate) + " " + str(l) + "," + str(d) + "," + str(
            u) + "," + str(r))

        window_counter = 0
        window_counter += self.child_a.debug_print(level + 1)
        window_counter += self.child_b.debug_print(level + 1)

        return window_counter

    def set_split_default(self):
        """Sets split to 50% of the node's assigned area"""
        l, d, u, r = self.parent.get_borders(self)

        # TODO: self.split is not defined in __init__. Make it so.
        if self.plane_type == PLANE.VERTICAL:
            self.split_coordinate = (l + r) / 2
        else:
            self.split_coordinate = (u + d) / 2

    def split(self, caller_child, new_window, plane_type, direction):
        """Alter tree to add a new window

        When a child window requests a split, the parent creates a new node
        to replace the child with.

        E.g.
        Node
         |
         +--> Window A
         |
         +--> Window B

        Window B requests split to add Window C

        Node
         |
         +--> Window A
         |
         +--> Node
               |
               +--> Window B
               |
               +--> Window C
        """
        new_node = Node(plane_type)
        new_node.parent = self

        # The calling child is the one to become the new node.
        if caller_child == self.child_a:
            self.child_a = new_node
        else:
            self.child_b = new_node

        new_node.set_split_default()

        if direction == DIR.DOWN or direction == DIR.RIGHT:
            new_node.child_a = caller_child
            new_node.child_b = new_window
        else:
            new_node.child_a = new_window
            new_node.child_b = caller_child

        new_node.child_a.parent = new_node
        new_node.child_b.parent = new_node

        # Force both children to resize
        # TODO: Only need to force the calling child to resize. []
        self.child_a.set_size()
        self.child_b.set_size()

    def get_borders(self, caller_child):
        """Returns borders for the calling child

        E.g.
              Split
                |
                |
                V
        +-------+--------+
        |       |        |
        |       |        |
        |   A   |   B    |
        |       |        |
        |       |        |
        +-------+--------+

        Child A only gets borders up to the split
        """
        left, down, up, right = self.parent.get_borders(self)

        if caller_child == self.child_a:
            if self.plane_type == PLANE.HORIZONTAL:
                down = self.split_coordinate
            else:
                right = self.split_coordinate
        else:
            if self.plane_type == PLANE.HORIZONTAL:
                up = self.split_coordinate
            else:
                left = self.split_coordinate

        return left, down, up, right

    """Ripple gap correction requests up to the root screen"""

    def gap_correct_left(self, l):
        return self.parent.gap_correct_left(l)

    def gap_correct_down(self, d):
        return self.parent.gap_correct_down(d)

    def gap_correct_up(self, u):
        return self.parent.gap_correct_up(u)

    def gap_correct_right(self, r):
        return self.parent.gap_correct_right(r)

    def set_size(self, reset_default=False):
        """Force both children to resize

        ResetDefault. If true, resets the split to 50%
        """
        if reset_default:
            self.set_split_default()

        self.child_a.set_size(reset_default)
        self.child_b.set_size(reset_default)

    def resize_vertical(self, caller_child, increment):
        """Resize calling child window / node

        If the calling child is child A, simply move the split to give more
        space to child A.
        Otherwise, ripple the request to the parent, to see if they can resize


        # TODO: Possible to use a single function to do this?
        """
        if self.plane_type != PLANE.HORIZONTAL:
            return self.parent.resize_vertical(self, increment)
        if caller_child == self.child_b:
            return self.parent.resize_vertical(self, increment)

        self.split_coordinate += increment
        self.set_size()
        return True

    def resize_horizontal(self, caller_child, increment):
        if self.plane_type != PLANE.VERTICAL:
            return self.parent.resize_horizontal(self, increment)
        if caller_child == self.child_b:
            return self.parent.resize_horizontal(self, increment)

        self.split_coordinate += increment
        self.set_size()
        return True

    def all_are_bees(self, caller_child):
        """If the calling child is 'ChildB', ripple the call up to check if THIS caller is also ChildB'
        Returns True if the entire call stack up to the screen are all 'ChildB's.
        Returns False if any along the call stack are 'ChildA'
        """
        if caller_child == self.child_b:
            return self.parent.all_are_bees(self)
        return False

    def find_earliest_a_but_not_me(self, caller_child):
        """Returns the earliest (deepest in the tree, but above the caller) 'ChildA' that is not part of the call
        stack
        """
        if caller_child == self.child_a:
            return self.parent.find_earliest_a_but_not_me(self)
        return self.child_a

    def get_child_a(self):
        """Return 'ChildA'"""
        return self.child_a

    def change_plane(self):
        """Swap the direction of the split

        In doing so, also force all sub-windows to resize to 50% of their node.
        This is due to the potentially extremely drastic layout changes that
        can occur when changing the plane.
        """
        if self.plane_type == PLANE.VERTICAL:
            plane_type = PLANE.HORIZONTAL
        else:
            plane_type = PLANE.VERTICAL

        self.plane_type = plane_type
        self.set_size(True)

    def swap_pane_position(self):
        """Swap the positions of the children"""
        self.child_a, self.child_b = self.child_b, self.child_a
        self.set_size()

    def replace_child(self, caller_child, new_child):
        """Replace the calling child with a new child
        # TODO: Should we handle resizing here?
        """
        if caller_child == self.child_a:
            self.child_a = new_child
        else:
            self.child_b = new_child

    def kill_window(self, caller_child):
        """Remove a window from the tree

        Removing a window leaves this node with only a single valid child. So,
        this must be fixed by removing this node from the tree and replacing
        it with the remaining window.

        Note: Python GC should take care of removing the node from memory. And
        since we are pickling, there should be no leftover nodes / windows.
        """
        if caller_child == self.child_a:
            surviving_child = self.child_b
        else:
            surviving_child = self.child_a

        self.parent.replace_child(self, surviving_child)
        surviving_child.parent = self.parent

        self.parent.set_size()

        return ""

    def list_screen_windows(self):
        """Request the parent to list all their windows (including yourself)"""
        return self.parent.list_screen_windows()

    def window_ids(self):
        """Request all children to return a list of windows and concat them"""
        return self.child_a.window_ids() + self.child_b.window_ids()

    def get_screen_borders(self):
        """Ripple screen border request to parent"""
        return self.parent.get_screen_borders()

    def get_plane_type(self):
        """Return PlaneType"""
        return self.plane_type

    def minimize(self):
        self.child_a.minimize()
        self.child_b.minimize()

    def get_screen_index(self, _calling_child):
        return self.parent.get_screen_index(self)

    def get_window_list(self):
        return self.child_a.get_window_list() + self.child_b.get_window_list()

    def get_available_window_list(self):
        return self.child_a.get_available_window_list() + self.child_b.get_available_window_list()

    def is_any_maximized(self):
        return self.child_a.is_any_maximized() or self.child_a.is_any_maximized()

    def split_ratio(self):
        if isinstance(self.split_coordinate, float):
            return self.split_coordinate
        length = self.get_length()
        return float(self.split_coordinate) / float(length)

    def get_length(self):
        left, down, up, right = self.parent.get_borders(self)
        if self.plane_type == PLANE.HORIZONTAL:
            length = down - up
        else:
            length = right - left

        return length

    def backup_split(self):
        split_ratio = self.split_ratio()
        self.split_coordinate = split_ratio
        self.child_a.backup_split()
        self.child_b.backup_split()

    def split_coordinates(self):
        left, _, up, _ = self.parent.get_borders(self)
        if isinstance(self.split_coordinate, int):
            return self.split_coordinate
        length = self.get_length()
        offset = int(self.split_coordinate * length)
        if self.plane_type == PLANE.HORIZONTAL:
            start_coord = up
        else:
            start_coord = left
        return start_coord + offset

    def restore_split(self):
        split_coordinate = self.split_coordinates()
        self.split_coordinate = split_coordinate
        self.child_a.restore_split()
        self.child_b.restore_split()
