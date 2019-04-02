import helpers
from node import Node
from enums import *
import config


class SplitNode(Node):
    """Node of the tree

    Contains two children, which can be nodes or children.
    PlaneType defines whether the node is split horizontally or vertically
    """

    def __init__(self, plane_type):
        Node.__init__(self, 2)

        self.plane_type = plane_type
        self.split_coordinate = None
        self.split_ratio = 0.5

    # ------------------------------------------------------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------------------------------------------------------

    def get_plane_type(self):
        return self.plane_type

    def get_split_coordinate(self):
        return self.split_coordinate

    def get_split_ratio(self):
        return self.split_ratio

    # ------------------------------------------------------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------------------------------------------------------

    def set_plane_type(self, new_plane_type):
        self.plane_type = new_plane_type

    def set_split_coordinate(self, new_split_coordinate):
        self.split_coordinate = new_split_coordinate
        self.set_split_ratio_from_split_coordinate()

    def set_split_ratio(self, new_split_ratio):
        self.split_ratio = new_split_ratio
        self.set_split_coordinate_from_split_ratio()

    def alter_split_coordinate(self, increment):
        new_split_coordinate = self.get_split_coordinate() + increment
        self.set_split_coordinate(new_split_coordinate)

    def set_split_coordinate_from_split_ratio(self):
        ((_, _), (x_size, y_size)) = self.parent.get_viewport(self)

        if self.get_plane_type() == PLANE.HORIZONTAL:
            split_coordinate = int(y_size * self.get_split_ratio())
        elif self.get_plane_type() == PLANE.VERTICAL:
            split_coordinate = int(x_size * self.get_split_ratio())
        else:
            raise Exception("Invalid plane")

        self.split_coordinate = split_coordinate

    def set_split_ratio_from_split_coordinate(self):
        ((_, _), (x_size, y_size)) = self.parent.get_viewport(self)

        if self.get_plane_type() == PLANE.HORIZONTAL:
            split_ratio = float(self.get_split_coordinate()) / float(y_size)
        elif self.get_plane_type() == PLANE.VERTICAL:
            split_ratio = float(self.get_split_coordinate()) / float(x_size)
        else:
            raise Exception("Invalid plane")

        self.split_ratio = split_ratio

    # ------------------------------------------------------------------------------------------------------------------
    # Trickle downs
    # ------------------------------------------------------------------------------------------------------------------

    def to_json(self):
        json = '{'
        json += '"type":' + helpers.json_com('split_node') + ','
        json += '"plane_type":' + helpers.json_com(self.get_plane_type()) + ','
        json += '"split_coordinate":' + helpers.json_com(self.get_split_coordinate()) + ','
        json += '"split_ratio":' + helpers.json_com(self.get_split_ratio()) + ','
        json += Node.to_json(self)
        json += '}'

        return json

    def debug_print(self, level):
        s = config.DEBUG_SPACER * level
        s += ' '.join([self.get_plane_type(), self.get_split_coordinate(), self.get_split_ratio()])
        print(s)

        [c.debug_print(level + 1) for c in self.get_children()]

    def restore_splits(self):
        self.set_split_ratio(self.get_split_ratio())
        [c.restore_splits() for c in self.get_children()]

    # ------------------------------------------------------------------------------------------------------------------
    # Bubble ups
    # ------------------------------------------------------------------------------------------------------------------

    def get_split_node(self):
        return self

    def get_smallest_immutable_subtree(self, calling_child):
        return calling_child

    # ------------------------------------------------------------------------------------------------------------------
    # Child Requests
    # ------------------------------------------------------------------------------------------------------------------

    def get_viewports(self):
        """
        Horizontal Split

                 x size
               |-----------|

        (x, y) +-----------+  -        -
               |           |  |        |
               |           |  | y      | split
               +-----------+  | size   -
               |           |  |
               |           |  |
               +-----------+  -


        Vertical Split

                 x size
               |-----------|

        (x, y) +-----+-----+  -
               |     |     |  |
               |     |     |  | y
               |     |     |  | size
               |     |     |  |
               |     |     |  |
               +-----+-----+  -

               |-----|
                split
        """
        (x_pos, y_pos), (x_size, y_size) = self.parent.get_viewport(self)
        split = self.get_split_coordinate()

        if self.get_plane_type() == PLANE.HORIZONTAL:
            x_pos_1 = x_pos
            y_pos_1 = y_pos
            x_size_1 = x_size
            y_size_1 = split

            x_pos_2 = x_pos
            y_pos_2 = y_pos + split
            x_size_2 = x_size
            y_size_2 = y_size - split

            # Gap correction
            y_size_1 -= config.GAP / 2

            y_pos_2 += config.GAP / 2
            y_size_2 -= config.GAP / 2

        elif self.get_plane_type() == PLANE.VERTICAL:
            x_pos_1 = x_pos
            y_pos_1 = y_pos
            x_size_1 = split
            y_size_1 = y_size

            x_pos_2 = x_pos + split
            y_pos_2 = y_pos
            x_size_2 = x_size - split
            y_size_2 = y_size

            # Gap correction
            x_size_1 -= config.GAP / 2

            x_pos_2 += config.GAP / 2
            x_size_2 -= config.GAP / 2
        else:
            raise Exception("Invalid plane")

        viewport_1 = ((x_pos_1, y_pos_1), (x_size_1, y_size_1))
        viewport_2 = ((x_pos_2, y_pos_2), (x_size_2, y_size_2))
        return [viewport_1, viewport_2]

    def get_viewport(self, calling_child):
        index = self.get_child_index(calling_child)
        return self.get_viewports()[index]

    def change_plane(self):
        if self.get_plane_type() == PLANE.HORIZONTAL:
            self.set_plane_type(PLANE.VERTICAL)
        else:
            self.set_plane_type(PLANE.HORIZONTAL)

        self.set_split_ratio(0.5)
        self.restore_splits()
        self.redraw()

    # ------------------------------------------------------------------------------------------------------------------
    # Other
    # ------------------------------------------------------------------------------------------------------------------

    def resize_vertical(self, caller_child, increment):
        """Resize calling child window / node

        If the calling child is child A, simply move the split to give more
        space to child A.
        Otherwise, ripple the request to the parent, to see if they can resize

        """
        if self.get_plane_type() != PLANE.HORIZONTAL:
            return self.parent.resize_vertical(self, increment)
        if self.get_child_index(caller_child) == 1:
            return self.parent.resize_vertical(self, increment)

        self.alter_split_coordinate(increment)
        self.redraw()
        return True

    def resize_horizontal(self, caller_child, increment):
        if self.plane_type != PLANE.VERTICAL:
            return self.parent.resize_horizontal(self, increment)
        if self.get_child_index(caller_child) == 1:
            return self.parent.resize_horizontal(self, increment)

        self.alter_split_coordinate(increment)
        self.redraw()
        return True

    # TODO: Refactor name
    def all_are_bees(self, caller_child):
        """If the calling child is 'ChildB', ripple the call up to check if THIS caller is also ChildB'
        Returns True if the entire call stack up to the screen are all 'ChildB's.
        Returns False if any along the call stack are 'ChildA'
        """
        if self.get_child_index(caller_child) == 1:
            return self.parent.all_are_bees(self)
        return False

    # TODO: Refactor name
    def find_earliest_a_but_not_me(self, caller_child):
        """Returns the earliest (deepest in the tree, but above the caller) 'ChildA' that is not part of the call
        stack
        """
        if self.get_child_index(caller_child) == 0:
            return self.parent.find_earliest_a_but_not_me(self)
        return self.get_child(0)
