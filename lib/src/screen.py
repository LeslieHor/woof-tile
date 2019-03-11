from config import *
from node import Node
from enums import *


class Screen:
    def __init__(self, left, down, up, right):
        self.left = left
        self.down = down
        self.up = up
        self.right = right

        self.child = None

    def debug_print(self, level):
        print("\t" * level + "Screen")
        if self.child is not None:
            return self.child.debug_print(level + 1)
        else:
            return 0

    def get_borders(self, _caller_child):
        return self.left, self.down, self.up, self.right

    def initialise(self, new_window):
        """Initialise a screen with a window

        Screens always start empty. You can't initialise with a node as the
        node will only have one window. So you initialise with a window to
        start with.
        """
        self.child = new_window
        self.child.parent = self
        self.child.set_size()

    def split(self, caller_child, new_window, plane_type, direction):
        """Split screen by adding a node

        When a second window is added to a screen, we need to initialise a
        node to store the two windows.
        """
        new_node = Node(plane_type)
        new_node.parent = self
        new_node.set_split_default()

        if direction == DIR.DOWN or direction == DIR.RIGHT:
            new_node.child_a = caller_child
            new_node.child_b = new_window
        else:
            new_node.child_a = new_window
            new_node.child_b = caller_child

        new_node.child_a.parent = new_node
        new_node.child_b.parent = new_node

        self.child = new_node
        self.child.set_size()

    """Calculates correct gap size

    Gap size for the screen borders are full sized. We add 1 to allow a
    gap size of 1 pixel. Which results in a 1 pixel gap between the
    screen borders and the window, and a 2 pixel gap between windows.

    Gap size between windows are half-size as the other window will have
    the same sized gap.
    """

    def gap_correct_left(self, left):
        if left != self.left:
            return (GAP + 1) / 2
        return GAP

    def gap_correct_down(self, down):
        if down != self.down:
            return (GAP + 1) / 2
        return GAP

    def gap_correct_up(self, up):
        if up != self.up:
            return (GAP + 1) / 2
        return GAP

    def gap_correct_right(self, right):
        if right != self.right:
            return (GAP + 1) / 2
        return GAP

    """Deny resizing if request reaches the screen

    You cannot resize the screen itself.
    """

    @staticmethod
    def resize_vertical(_caller_child, _increment):
        return False

    @staticmethod
    def resize_horizontal(_caller_child, _increment):
        return False

    def kill_window(self, caller_child):
        """Reset pointer to child to None
        Return an empty string, as we don't want to activate any particular window, since the call must've come from
        the only window on the screen (i.e. This screen only had one window in it)
        """
        if caller_child != self.child:
            return False
        self.child = None

        return ""

    def replace_child(self, caller_child, new_child):
        """Replace current child with a new one.

        Only accept if the call came from the current child.
        """
        if caller_child != self.child:
            return False
        self.child = new_child

    def set_size(self, _reset_default=False):
        """Request that the child resize itself

        ResetDefault is unused.
        """
        self.child.set_size()

    def list_screen_windows(self):
        """Request that the child return a list of window ids"""
        return self.child.window_ids()

    def get_screen_borders(self):
        """Return screen border coordinates
        # TODO: This is a duplicate of get_borders(). Pick one.
        """
        return self.left, self.down, self.up, self.right

    # TODO: Refactor function name
    @staticmethod
    def all_are_bees(_caller_child):
        """If call has gotten to this point, all children to this point must have been 'ChildB'
        So just return true
        """
        return True

    # TODO: Refactor function name
    @staticmethod
    def find_earliest_a_but_not_me(_caller_child):
        """If call has gotten to this point, we could not find a 'ChildA' that was not part of the calling stack"""
        return None
