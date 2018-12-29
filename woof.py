#!/usr/bin/python

import subprocess # For calling into the system
import pickle # For saving the window structure to disk
import sys # For getting args
import time # For calculating acceleration when resizing windows

"""Enum for directions
"""
class DIR:
    L = 0
    D = 1
    U = 2
    R = 3

"""Enum for plane directions
"""
class PLANE:
    HORZ = 0
    VERT = 1

"""Root of all tree structures
"""
class WorkSpace:
    def __init__(self, DesktopCount, ScreensCount, ResHorz, ResVert):
        self.DesktopsCount = DesktopCount
        self.Desktops = []

        for _Desktop in range(self.DesktopsCount):
            NewDesktop = Desktop(ScreensCount, ResHorz, ResVert)
            self.Desktops.append(NewDesktop)

    def DEBUG_PRINT(self):
        print "WorkSpace"
        WindowCounter = 0
        for Desktop in self.Desktops:
            WindowCounter += Desktop.DEBUG_PRINT(1)
        return WindowCounter

"""Container for all screens for a particular desktop

Automatically constructs screen limits and stores a list of screens

# TODO: Allow any even grid-based layout e.g. 1x3, 2x2, 3x2 etc.
"""
class Desktop:
    def __init__(self, ScreensCount, ResHorz, ResVert):
        self.ScreensCount = ScreensCount
        self.Screens = []
        
        ScreenResHorz = ResHorz / self.ScreensCount
        LeftLimit = 0
        for RightLimit in range(ScreenResHorz, ResHorz + ScreenResHorz, ScreenResHorz):
            NewScreen = Screen(LeftLimit, 1080, 0, RightLimit)
            LeftLimit = RightLimit
            self.Screens.append(NewScreen)

    def DEBUG_PRINT(self, Level):
        print "\t" * Level + "Desktop"
        WindowCounter = 0
        for Screen in self.Screens:
            WindowCounter += Screen.DEBUG_PRINT(Level + 1)
        return WindowCounter

    """Returns the screen index the given pixel belongs to
    # TODO Should work for grid-based layouts
    """
    def which_screen(self, LeftPixel):
        ScreenIndex = 0
        for Screen in self.Screens:
            if Screen.L <= LeftPixel and LeftPixel < Screen.R:
                return Screen
            ScreenIndex += 1
        return ScreenIndex

class Screen:
    def __init__(self, L, D, U, R):
        self.L = L
        self.D = D
        self.U = U
        self.R = R

        self.Child = None

    def DEBUG_PRINT(self, Level):
        print "\t" * Level + "Screen"
        if self.Child != None:
            return self.Child.DEBUG_PRINT(Level + 1)
        else:
            return 0

    def get_borders(self, _CallerChild):
        return self.L, self.D, self.U, self.R

    """Initialise a screen with a window

    Screens always start empty. You can't initalise with a node as the
    node will only have one window. So you initialise with a window to
    start with.
    """
    def initialise(self, NewWindow):
        self.Child = NewWindow
        self.Child.Parent = self
        self.Child.set_size()

    """Split screen by adding a node

    When a second window is added to a screeen, we need to initialise a
    node to store the two windows.
    """
    def split(self, CallerChild, NewWindow, PlaneType, Direction):
        NewNode = Node(PlaneType)
        NewNode.Parent = self
        NewNode.set_split_default()

        if Direction == DIR.D or Direction == DIR.R:
            NewNode.ChildA = CallerChild
            NewNode.ChildB = NewWindow
        else:
            NewNode.ChildA = NewWindow
            NewNode.ChildB = CallerChild

        NewNode.ChildA.Parent = NewNode
        NewNode.ChildB.Parent = NewNode

        self.Child = NewNode
        self.Child.set_size()
        
    """Calculates correct gap size

    Gap size for the screen borders are full sized. We add 1 to allow a
    gap size of 1 pixel. Which results in a 1 pixel gap between the
    screen borders and the window, and a 2 pixel gap between windows.

    Gap size between windows are half-size as the other window will have
    the same sized gap.
    """
    def gap_correct_left(self, L):
        if L != self.L:
            return (GAP + 1) / 2
        return GAP
    def gap_correct_down(self, D):
        if D != self.D:
            return (GAP + 1) / 2
        return GAP
    def gap_correct_up(self, U):
        if U != self.U:
            return (GAP + 1) / 2
        return GAP
    def gap_correct_right(self, R):
        if R != self.R:
            return (GAP + 1) / 2
        return GAP

    """Deny resizing if request reaches the screen

    You cannot resize the screen itself.
    """
    def resize_vert(self, CallerChild, _Increment):
        return False
    def resize_horz(self, CallerChild, _Increment):
        return False

    """Reset pointer to child to None
    Return an empty string, as we don't want to activate any particular window, since the call must've come from the only
    window on the screen (i.e. This screen only had one window in it)
    """
    def kill_window(self, CallerChild):
        if CallerChild != self.Child:
            return False
        self.Child = None
        
        return ""

    """Replace current child with a new one.

    Only accept if the call came from the current child.
    """
    def replace_child(self, CallerChild, NewChild):
        if CallerChild != self.Child:
            return False
        self.Child = NewChild
    
    """Request that the child resize itself

    ResetDefault is unused.
    """
    def set_size(self, ResetDefault = False):
        self.Child.set_size()

    """Request that the child return a list of window ids
    """
    def list_screen_windows(self):
        return self.Child.window_ids()

    """Return screen border coordinates
    # TODO: This is a duplicate of get_borders(). Pick one.
    """
    def get_screen_borders(self):
        return self.L, self.D, self.U, self.R

    """If call has gotten to this point, all children to this point must have been 'ChildB'
    So just return true
    """
    def all_are_bees(self, _CallerChild):
        return True

    """If call has gotton to this point, we could not find a 'ChildA' that was not part of the calling stack
    """
    def find_earliest_a_but_not_me(self, _CallerChild):
        return None

"""Node of the tree

Contains two children, which can be nodes or children.
PlaneType defines whether the node is split horizonally or vertically
"""
class Node:
    def __init__(self, PlaneType):
        self.PlaneType = PlaneType

        self.Parent = None
        self.ChildA = None
        self.ChildB = None

    def DEBUG_PRINT(self, Level):
        if self.PlaneType == PLANE.HORZ:
            PT = "H"
        else:
            PT = "V"
        L, D, U, R = self.Parent.get_borders(self)
        print "\t" * Level + "N (" + PT + ") "  + str(self.Split) + " " + str(L) + "," + str(D) + "," + str(U) + "," + str(R)

        WindowCounter = 0
        WindowCounter += self.ChildA.DEBUG_PRINT(Level + 1)
        WindowCounter += self.ChildB.DEBUG_PRINT(Level + 1)

        return WindowCounter

    """Sets split to 50% of the node's assigned area
    """
    def set_split_default(self):
        L, D, U, R = self.Parent.get_borders(self)

        if self.PlaneType == PLANE.VERT:
            self.Split = (L + R) / 2
        else:
            self.Split = (U + D) / 2

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
    def split(self, CallerChild, NewWindow, PlaneType, Direction):
        NewNode = Node(PlaneType)
        NewNode.Parent = self

        # The calling child is the one to become the new node.
        if CallerChild == self.ChildA:
            self.ChildA = NewNode
        else:
            self.ChildB = NewNode

        NewNode.set_split_default()

        if Direction == DIR.D or Direction == DIR.R:
            NewNode.ChildA = CallerChild
            NewNode.ChildB = NewWindow
        else:
            NewNode.ChildA = NewWindow
            NewNode.ChildB = CallerChild

        NewNode.ChildA.Parent = NewNode
        NewNode.ChildB.Parent = NewNode

        # Force both children to resize
        # TODO: Only need to force the calling child to resize. []
        self.ChildA.set_size()
        self.ChildB.set_size()

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
    def get_borders(self, CallerChild):
        L, D, U, R = self.Parent.get_borders(self)

        if CallerChild == self.ChildA:
            if self.PlaneType == PLANE.HORZ:
                D = self.Split
            else:
                R = self.Split
        else:
            if self.PlaneType == PLANE.HORZ:
                U = self.Split
            else:
                L = self.Split

        return L, D, U, R

    """Ripple gap correction requests up to the root screen
    """
    def gap_correct_left(self, L):
        return self.Parent.gap_correct_left(L)
    def gap_correct_down(self, D):
        return self.Parent.gap_correct_down(D)
    def gap_correct_up(self, U):
        return self.Parent.gap_correct_up(U)
    def gap_correct_right(self, R):
        return self.Parent.gap_correct_right(R)

    """Force both children to resize

    ResetDefault. If true, resets the split to 50%
    """
    def set_size(self, ResetDefault = False):
        if ResetDefault:
            self.set_split_default()

        self.ChildA.set_size(ResetDefault)
        self.ChildB.set_size(ResetDefault)

    """Resize calling child window / node

    If the calling child is child A, simply move the split to give more
    space to child A.
    Otherwise, ripple the request to the parent, to see if they can resize
    

    # TODO: Possible to use a single function to do this?
    """
    def resize_vert(self, CallerChild, Increment):
        if self.PlaneType != PLANE.HORZ:
            return self.Parent.resize_vert(self, Increment)
        if CallerChild == self.ChildB:
            return self.Parent.resize_vert(self, Increment)

        self.Split += Increment
        self.set_size()
        return True
    def resize_horz(self, CallerChild, Increment):
        if self.PlaneType != PLANE.VERT:
            return self.Parent.resize_horz(self, Increment)
        if CallerChild == self.ChildB:
            return self.Parent.resize_horz(self, Increment)

        self.Split += Increment
        self.set_size()
        return True
    
    """If the calling child is 'ChildB', ripple the call up to check if THIS caller is also ChildB'
    Returns True if the entire call stack up to the screen are all 'ChildB's.
    Returns False if any along the call stack are 'ChildA'
    """
    def all_are_bees(self, CallerChild):
        if CallerChild == self.ChildB:
            return self.Parent.all_are_bees(self)
        return False

    """Returns the earliest (deepest in the tree, but above the caller) 'ChildA' that is not part of the call stack
    """
    def find_earliest_a_but_not_me(self, CallerChild):
        if CallerChild == self.ChildA:
            return self.Parent.find_earliest_a_but_not_me(self)
        return self.ChildA

    """Return 'ChildA'
    """
    def get_childa(self):
        return self.ChildA

    """Swap the direction of the split

    In doing so, also force all sub-windows to resize to 50% of their node.
    This is due to the potentially extremely drastic layput changes that 
    can occur when changing the plane.
    """
    def change_plane(self):
        if self.PlaneType == PLANE.VERT:
            PlaneType = PLANE.HORZ
        else:
            PlaneType = PLANE.VERT
        
        self.PlaneType = PlaneType
        self.set_size(True)

    """Swap the positions of the children
    """
    def swap_pane_position(self):
        self.ChildA, self.ChildB = self.ChildB, self.ChildA
        self.set_size()
    
    """Replace the calling child with a new child
    # TODO: Should we handle resizing here?
    """
    def replace_child(self, CallerChild, NewChild):
        if CallerChild == self.ChildA:
            self.ChildA = NewChild
        else:
            self.ChildB = NewChild

    """Remove a window from the tree
    
    Removing a window leaves this node with only a single valid child. So,
    this must be fixed by removing this node from the tree and replacing 
    it with the remaining window.

    Note: Python GC should take care of removing the node from memory. And
    since we are pickling, there should be no leftover nodes / windows.
    """
    def kill_window(self, CallerChild):
        if CallerChild == self.ChildA:
            SurvivingChild = self.ChildB
        else:
            SurvivingChild = self.ChildA

        self.Parent.replace_child(self, SurvivingChild)
        SurvivingChild.Parent = self.Parent

        self.Parent.set_size()

        return ""

    """Request the parent to list all their windows (including yourself)
    """
    def list_screen_windows(self):
        return self.Parent.list_screen_windows()

    """Request all children to return a list of windows and concat them
    """
    def window_ids(self):
        return self.ChildA.window_ids() + self.ChildB.window_ids()

    """Ripple screen border request to parent
    """
    def get_screen_borders(self):
        return self.Parent.get_screen_borders()

    """Return PlaneType
    """
    def get_planetype(self):
        return self.PlaneType

""" Window Groups allow mutliple windows to take the position where normally a single window would appear.
It shades inactive windows and creates fake (non-functional) tabs to display which windows are a part of the group.

Note: The active window of a window group is different from the active window of the entire system. A window group's
active window simply says which window is unshaded, and which window can be focused.

The structure contains a list for all windows in the window group, along with a separate list for the inactive windows
to build the tabs with.
"""
class WindowGroup:
    def __init__(self, Parent, ActiveWindow, InactiveWindows):
        self.AllWindows = [ActiveWindow] + InactiveWindows
        self.ActiveWindow = ActiveWindow
        self.InactiveWindows = InactiveWindows
        self.ActiveWindowIndex = 0

        self.Parent = Parent

    def DEBUG_PRINT(self, Level):
        print "\t" * Level + "WG WinCount: " + str(len(self.AllWindows)) + ". Active: " + str(self.AllWindows.index(self.ActiveWindow))
        WindowCounter = 0
        for Window in self.AllWindows:
            WindowCounter += Window.DEBUG_PRINT(Level + 1)
        return WindowCounter

    """Ripple gap correction requests up to the root screen
    """
    def gap_correct_left(self, L):
        return self.Parent.gap_correct_left(L)
    def gap_correct_down(self, D):
        return self.Parent.gap_correct_down(D)
    def gap_correct_up(self, U):
        return self.Parent.gap_correct_up(U)
    def gap_correct_right(self, R):
        return self.Parent.gap_correct_right(R)

    """ Calculates the shaded size of the particular index
    """
    def get_shaded_size(self, Index):
        L, D, U, R = self.Parent.get_borders(self)
        Increment = (R - L) / len(self.InactiveWindows)
        Borders = range(L, R, Increment) + [R]
        return Borders[Index], D, U, Borders[Index + 1]
    
    """Adds a new window to the window group and focuses it
    """
    def add_window(self, NewWindow):
        self.AllWindows.append(NewWindow)
        self.InactiveWindows.append(NewWindow)
        NewWindowIndex = len(self.InactiveWindows)
        Offset = NewWindowIndex - self.ActiveWindowIndex
        self.activate_next_window(Offset)

    """Sets the size of the tabs and active window
    Implemented separately from the normal set_size due to
    having to calculate shaded sizes.

    # TODO: Decide if you want the gap appearing between tabs or not. Currently gaps appear.
    """
    def set_size(self, _ResizeDefault = False):
        for I in range(len(self.InactiveWindows)):
            InactiveWindow = self.InactiveWindows[I]
            log_debug(['Shading window', InactiveWindow.WindowIdDec])
            L, D, U, R = self.get_shaded_size(I)
            PX, PY, SX, SY = InactiveWindow.border_gap_correct(L, D, U, R)
            InactiveWindow.set_size_override(PX, PY, SX, SY)
            InactiveWindow.shade()

        ActiveWindow = self.ActiveWindow
        L, D, U, R = self.Parent.get_borders(self)
        PX, PY, SX, SY = ActiveWindow.border_gap_correct(L, D, U, R)
        PY += SHADEDSIZE
        SY -= SHADEDSIZE
        ActiveWindow.set_size_override(PX, PY, SX, SY)
        ActiveWindow.unshade()
        
    """Activates whatever window is currently defined as active
    """
    def activate_active_window(self):
        log_debug(['Activating active window'])
        self.set_size()
        self.ActiveWindow.activate()

    """Increments the counter by Increment and activates whatever
    window that is in the list.
    """
    def activate_next_window(self, Increment):
        self.ActiveWindowIndex += Increment
        self.ActiveWindowIndex %= len(self.AllWindows)

        self.ActiveWindow = self.AllWindows[self.ActiveWindowIndex]
        self.InactiveWindows = list(self.AllWindows)
        del self.InactiveWindows[self.ActiveWindowIndex]
        RotatedList = self.InactiveWindows[self.ActiveWindowIndex:] + self.InactiveWindows[: self.ActiveWindowIndex]
        self.InactiveWindows = RotatedList

        self.activate_active_window()

    """Resizes window group
    """
    def resize_vert(self, _CallerChild, Increment):
        return self.Parent.resize_vert(self, Increment)
    def resize_horz(self, _CallerChild, Increment):
        return self.Parent.resize_horz(self, Increment)

    """Returns the earliest 'ChildA' not part of the call stack
    Rippled up as window groups have no ChildA/ChildB
    """
    def find_earliest_a_but_not_me(self, CallerChild):
        return self.Parent.find_earliest_a_but_not_me(self)

    """Returns if all objects in call stack are 'ChildB'
    Rippled up as window groups have no ChildA/ChildB
    """
    def all_are_bees(self, CallerChild):
        return self.Parent.all_are_bees(self)
    
    """Returns borders of the current pane
    """
    def get_borders(self, CallingChild):
        return self.Parent.get_borders(self)

    """Removes the calling window from the windowgroup

    If the size of the window group is two, then removing a window leaves a window group with
    only one window, which should be converted back into a regular window

    Return the ID of which window to activate to keep the system focus within the window group
    """
    def kill_window(self, CallerChild):
        if len(self.AllWindows) == 2:
            # The remaining window will be a single, so we
            # turn it into a normal window
            self.AllWindows.remove(CallerChild)
            log_debug(['Removed calling child:', CallerChild.WindowIdDec])
            log_debug(['AllWindows length:', len(self.AllWindows)])
            SurvivingChild = self.AllWindows[0]
            log_debug(['SurvivingChild:', SurvivingChild.WindowIdDec])
            self.Parent.replace_child(self, SurvivingChild)
            log_debug(['Replacing parent child with surviving child'])
            SurvivingChild.Parent = self.Parent
            log_debug(['Replacing child parent with windowgroup parent'])
            SurvivingChild.unshade()
            SurvivingChild.set_size()
            return str(SurvivingChild.WindowIdDec)
        else:
            self.AllWindows.remove(CallerChild)
            self.activate_next_window(0)
            return str(self.ActiveWindow.WindowIdDec)

    """Splits the window to add a new window beside it
    """    
    def split(self, _CallerChild, NewWindow, PlaneType, Direction):
        self.Parent.split(self, NewWindow, PlaneType, Direction)

    """Returns parent PlaneType
    """
    def get_planetype(self):
        return self.Parent.PlaneType

    def list_screen_windows(self):
        return self.Parent.list_screen_windows()

    def window_ids(self):
        WindowIds = []
        for Win in self.AllWindows:
            WindowIds.append(Win.WindowIdDec)
        return WindowIds
    
    def get_screen_borders(self):
        return self.Parent.get_screen_borders()

"""Leaf node, representing a viewable window
"""
class Window:
    def __init__(self, WindowId):
        self.WindowIdDec = WindowId
        self.WindowIdHex = hex(int(WindowId))

        self.Parent = None
        self.Maximized = False

    def DEBUG_PRINT(self, Level):
        ParentType = "unknown"
        if isinstance(self.Parent, WindowGroup):
            ParentType = "WindowGroup"
        elif isinstance(self.Parent, Node):
            ParentType = "Node"
        elif isinstance(self.Parent, Screen):
            ParentType = "Screen"

        print "\t" * Level + "WindowID: " + str(self.WindowIdDec) + ": " + call(['xdotool getwindowname', self.WindowIdDec]).rstrip()[:20] + ". Class: " + self.get_window_class() + ". Parent Type: " + ParentType
        return 1

    """Get the size of the current window

    This is not necessarily the actual window size in the WM. Just the size
    the tree thinks the window should be.
    """
    def get_size(self):
        return self.Parent.get_borders(self)

    """Correct border calculations based on a whitelist

    Some programs will include window decoration as part of their coordinates
    Others will simply make the window size smaller based on the border.
    # TODO: I think this explanation is either badly written or just wrong

    Which application class does what must be defined by a whitelist.
    Whitelist defines programs that ignore borders in their calculations

    E.g.
    Intended window position
    +-Screen----------------------+
    |                             |
    |  +--------+                 |
    |  |        |                 |
    |  |        |                 |
    |  +--------+                 |
    |                             |
    |                             |
    |                             |
    +-----------------------------+

    Actual window position is above and to the left
    +-Screen----------------------+
    | +--------+                  |
    | |        |                  |
    | |        |                  |
    | +--------+                  |
    |                             |
    |                             |
    |                             |
    |                             |
    +-----------------------------+
    """
    def border_multiplier(self):
        WindowClass = self.get_window_class()
        for Name in BORDER_WHITELIST:
            if Name in WindowClass:
                return 1
        return 0
    
    def get_window_class(self):
        return call(['xprop -id', self.WindowIdDec, '| grep WM_CLASS | sed \'s/.* = "//\' | sed \'s/".*//\'']).rstrip()

    """Calculate window size parameters taking gap and borders into account
    
    Given coordinates for left, bottom, top and right borders, calculates
    the following (taking into account gaps and borders):

    - Coordinate of left border
    - Coordinate of top border
    - Width of window
    - Height of window
    """
    def border_gap_correct(self, L, D, U, R):
        BM = self.border_multiplier()
        LB = BM * LEFTBORDER
        TB = BM * TOPBORDER
        if BM == 1:
            RB = BM * RIGHTBORDER
            BB = BM * BOTTOMBORDER
        else:
            RB = LEFTBORDER + RIGHTBORDER
            BB = TOPBORDER + BOTTOMBORDER

        PX = L + LB + self.Parent.gap_correct_left(L)
        PY = U + TB + self.Parent.gap_correct_up(U)
        SX = R - PX - RB - self.Parent.gap_correct_right(R)
        SY = D - PY - BB - self.Parent.gap_correct_down(D)
        return PX, PY, SX, SY

    """Call into the WM to resize the window
    """
    def set_size_override(self, PX, PY, SX, SY):
        # xdotool will not override the plasma panel border
        # wmctrl is very particular about its args
        MVARG = '0,' + str(PX) + ',' + str(PY) + ',' + str(SX) + ',' + str(SY)
        call(['wmctrl -ir', self.WindowIdHex, '-e', MVARG])

    """Set the window location / size
    """
    def set_size(self, _ResetDefault = False):
        if isinstance(self.Parent, WindowGroup):
            self.Parent.set_size()
        else:
            L, D, U, R = self.get_size()
            PX, PY, SX, SY = self.border_gap_correct(L, D, U, R)
            self.set_size_override(PX, PY, SX, SY)

    """Request the parent to split to add a new window
    """
    def split(self, NewWindow, PlaneType, Direction):
        self.Parent.split(self, NewWindow, PlaneType, Direction)

    """Request parent to resize window.
    """
    def resize_vert(self, _CallerChild, Increment):
        if not self.Parent.resize_vert(self, Increment):
            log_debug(['Unable to resize. Using alterative'])
            NextChild = self.Parent.find_earliest_a_but_not_me(self)
            if NextChild != None:
                if not self.Parent.all_are_bees(self):
                    log_debug(['All are not bees'])
                    Increment *= -1
                elif self.Parent.get_planetype() == PLANE.HORZ:
                    Increment *= -1
                NextChild.resize_vert(self, Increment)

    def resize_horz(self, _CallerChild, Increment):
        if not self.Parent.resize_horz(self, Increment):
            log_debug(['Unable to resize. Using alterative'])
            NextChild = self.Parent.find_earliest_a_but_not_me(self)
            if NextChild != None:
                if not self.Parent.all_are_bees(self):
                    log_debug(['All are not bees'])
                    Increment *= -1
                elif self.Parent.get_planetype() == PLANE.VERT:
                    Increment *= -1
                NextChild.resize_horz(self, Increment)

    """Request parent to change plane orientation
    """
    def change_plane(self):
        self.Parent.change_plane()

    """Request parent to swap self and sibling positions
    """
    def swap_pane_position(self):
        self.Parent.swap_pane_position()
   
    """Request parent to replace self with a new child
    """
    def replace_child(self, NewChild):
        self.Parent.replace_child(self, NewChild)

    """Request parent to kill self (this window)
    """
    def kill_window(self):
        return self.Parent.kill_window(self)

    """Call into WM to minimize the window
    """
    def minimize(self):
        call(['xdotool windowminimize', self.WindowIdDec])

    """Call into WM to focus the window
    """
    def activate(self):
        call(['xdotool windowactivate', self.WindowIdDec])
    
    """Request parent to list all their windows

    This will ripple into the root screen, return a list of all windows on
    the screen
    """
    def list_screen_windows(self):
        return self.Parent.list_screen_windows()
    
    """Return window ID in a single-item list
    """
    def window_ids(self):
        return [self.WindowIdDec]

    """Set size of window as if this were the only window on the screen
    """
    def maximize(self):
        self.Maximized = True
        L, D, U, R = self.Parent.get_screen_borders()
        PX, PY, SX, SY = self.border_gap_correct(L, D, U, R)
        self.set_size_override(PX, PY, SX, SY)

    """Remove WM maximization status

    WM maximization status can interfere with resizing
    """
    def remove_wm_maximize(self):
        subprocess.call(["wmctrl", "-ir", self.WindowIdHex, "-b", "remove,maximized_vert,maximized_horz"])

    """List the current window name, pre-pending a given string

    This is used to list windows in rofi
    """    
    def list_add_window(self, Prepend = ''):
        WindowName = call(['xdotool getwindowname', self.WindowIdDec]).rstrip()
        return Prepend + str(self.WindowIdDec) + " : " + WindowName

    """Gets the windows state using xprop

    States:
    <BLANK> : Normal
    _NET_WM_STATE_SHADED : Shaded
    _NET_WM_STATE_HIDDEN : Minimized

    """
    def get_state(self):
        return call(['xprop', '-id', self.WindowIdDec, ' | grep "NET_WM_STATE" | sed \'s/_NET_WM_STATE(ATOM) = //\'']).rstrip()

    def is_shaded(self):
        return self.get_state() == "_NET_WM_STATE_SHADED"
    def shade(self):
        call(['wmctrl', '-ir', self.WindowIdHex, '-b', 'add,shaded'])
    def unshade(self):
        call(['wmctrl', '-ir', self.WindowIdHex, '-b', 'remove,shaded'])

"""Stores and manages the workspaces and windows

Contains pointer to workspace and a dictionary of windows ID --> Window Object
"""
class Windows:
    def __init__(self, DesktopCount, ScreensCount, ResHorz, ResVert):
        self.WorkSpace = WorkSpace(DesktopCount, ScreensCount, ResHorz, ResVert)
        self.Windows = {}
        self.LastResizeTS = 0

    def DEBUG_PRINT(self):
        print "LIST"
        print "----"
        for _WinID, Win in self.Windows.iteritems():
            print "-" * 40
            Win.DEBUG_PRINT(0)
            if Win.is_shaded():
                print "Window is shaded"
            else:
                print "Window is not shaded"

        print
        print "TREE"
        print "----"
        WindowsInTree = self.WorkSpace.DEBUG_PRINT()

        print
        print "----"
        print "Windows in list: " + str(len(self.Windows))
        print "Windows in tree: " + str(WindowsInTree)

    """Updates timing variable for resizing
    Returns normal resize increment if last resize was beyond the timing period
    If within the timing period, returns the rapid resizing increment
    """
    def update_resize_ts(self):
        Now = time.time() * 1000
        RI = RESIZEINCREMENT
        if (Now - self.LastResizeTS) < RESIZERAPIDTIME:
            RI = RAPIDINCREMENT
        self.LastResizeTS = Now
        return RI

    """Add the window the dictionary
    """
    def add_window(self, Window):
        NewWindowId = Window.WindowIdDec
        self.Windows[NewWindowId] = Window

    """Return the window object of the given ID
    """
    def get_window(self, WindowId):
        return self.Windows[WindowId]

    """Request the window to kill itself and remove from dictionary
    """
    def kill_window(self, WindowId):
        Window = self.Windows[WindowId]
        NextActiveWindow = Window.kill_window()
        del self.Windows[WindowId]
        return NextActiveWindow

    """Given a window id, swap the active and target positions in the tree
    # TODO: This really should work even in the same pane. Fix it and use this to 
    # TODO: do the swap pane positions thing
    """
    def swap_windows(self, TargetId):
        if not self.exists() or not self.exists(TargetId):
            return False

        WindowIdA = self.get_active_window()
        WindowIdB = TargetId

        WindowA = self.Windows[WindowIdA]
        WindowB = self.Windows[WindowIdB]

        WindowA.replace_child(WindowB)
        WindowB.replace_child(WindowA)

        WindowA.Parent, WindowB.Parent = WindowB.Parent, WindowA.Parent

        WindowA.set_size()
        WindowB.set_size()

        # If the swapped window(s) were maximized, re-maximize them after
        # the swap
        if WindowA.Maximized:
            main(['', 'maximize', WindowA.WindowIdDec])
        if WindowB.Maximized:
            main(['', 'maximize', WindowB.WindowIdDec])

    """Unminimize and unmaximize all windows

    Restores all windows to their intended positions
    """
    def restore_all(self):
        self.unminimize_all()
        for _WindowID, Window in self.Windows.iteritems():
            Window.Maximized = False
            if isinstance(Window.Parent, WindowGroup):
                Window.Parent.set_size()
            else:
                Window.set_size()

    """Checks that all windows in the dictionary are still alive

    Removes dead windows and fixes the tree.
    Return True if any windows had to be removed

    # TODO: Temp fixes really should not be here
    """
    def check_windows(self):
        HexIdsStr = call('wmctrl -l | awk -F" " \'$2 == 0 {print $1}\'')
        HexIds = HexIdsStr.split("\n")
        DecIds = [int(X, 0) for X in HexIds if X != '']
        Fix = False
        WindowIdsToKill = []
        for WinId, _Win in self.Windows.iteritems():
            if WinId not in DecIds:
                WindowIdsToKill.append(WinId)
                Fix = True
            else:
                # TEMP FIXES
                None
        for WinId in WindowIdsToKill:
            self.kill_window(WinId)

        return Fix

    """Generate a formatted list of windows

    For listing windows in rofi.

    Generates a list of all windows in the tree, with a prepended string.
    Empty screens are also returned in the list.
    """
    def list_add_windows(self, Prepend, ExcludeActive = False):
        List = []
        ActiveWindow = None
        if ExcludeActive:
            ActiveWindow = self.Windows[self.get_active_window()]

        for _WinId, Win in self.Windows.iteritems():
            if (not Win.is_shaded()) and (not Win == ActiveWindow):
                List.append(Win.list_add_window(Prepend))

        List.sort()
        Counter = 0
        for Screen in self.WorkSpace.Desktops[0].Screens:
            if Screen.Child == None:
                List.append(Prepend + "Screen " + str(Counter))
            Counter += 1
        return "\n".join(List)

    """Return a sorted list of all Window ids in the dictionary
    """
    def list_windows(self):
        List = []
        for WinId, _Win in self.Windows.iteritems():
            List.append(WinId)
        List.sort()
        return List

    """Check if a list if already in the dictionary
    """
    def exists(self, WinId = None):
        if WinId == None:
            WinId = self.get_active_window()
        return WinId in self.list_windows()

    """Minimze all windows
    """
    def minimize_all(self):
        for _Key, Win in self.Windows.iteritems():
            Win.minimize()
        
    def resize_vert(self, ExpandOrReduce, Increment = None):
        WinId = self.get_active_window()
        log_debug(['Active Window ID:', WinId])
        if not self.exists(WinId):
            log_warning(['Window does not exist, exiting.'])
            return False

        if Increment == None:
            Increment = self.update_resize_ts()
        
        log_debug(['Resize increment:', Increment])
        if ExpandOrReduce == 'reduce':
            log_debug(['Reduce size detected. Inverting increment'])
            Increment *= -1

        self.Windows[WinId].resize_vert(self, Increment)

    def resize_horz(self, ExpandOrReduce, Increment = None):
        WinId = self.get_active_window()
        log_debug(['Active Window ID:', WinId])
        if not self.exists(WinId):
            log_warning(['Window does not exist, exiting.'])
            return False

        if Increment == None:
            Increment = self.update_resize_ts()

        log_debug(['Resize increment:', Increment])
        if ExpandOrReduce == 'reduce':
            log_debug(['Reduce size detected. Inverting increment'])
            Increment *= -1

        self.Windows[WinId].resize_horz(self, Increment)

    def change_plane(self):
        if not self.exists():
            return False
        self.Windows[self.get_active_window()].change_plane()

    def swap_pane_position(self):
        if not self.exists():
            return False
        self.Windows[self.get_active_window()].swap_pane_position()

    """Unminimize all windows

    Because we need to unminimize by activating the window, window focus
    will be overwritten. Windows are not restored to their intended
    positions
    """
    def unminimize_all(self):
        ActiveWinId = self.get_active_window()
        for _Key, Win in self.Windows.iteritems():
            Win.activate()
            Win.Maximized = False

        # We active the window through a call, in case it is not in the tree
        call(['xdotool windowactivate', ActiveWinId])

    def activate_window(self, WinId):
        self.Windows[WinId].activate()

    """Get ID of current active window
    """
    def get_active_window(self): # Really should be called get_active_window_id
        return int(call('xdotool getactivewindow').rstrip())

    def add_to_window(self, PlaneType, Direction, TargetId):
        NewWindowId = self.get_active_window()
        NewWindow = Window(NewWindowId)
        NewWindow.remove_wm_maximize()

        TargetId = int(TargetId)
        if not self.exists(TargetId):
            return False
        
        self.Windows[TargetId].split(NewWindow, PlaneType, Direction)

        self.add_window(NewWindow)
 
    def add(self, PlaneType, Direction, TargetId, ScreenIndex = None):
        NewWindowId = self.get_active_window()
        if self.exists(NewWindowId):
            return False

        NewWindow = Window(NewWindowId)
        NewWindow.remove_wm_maximize()

        if TargetId == 'Screen':
            try:
                ScreenIndex = int(ScreenIndex)
            except:
                return False

            Screen = self.WorkSpace.Desktops[0].Screens[ScreenIndex]
            if Screen.Child != None:
                return False
            Screen.initialise(NewWindow)
        else:
            TargetId = int(TargetId)
            if not self.exists(TargetId):
                return False

            self.Windows[TargetId].split(NewWindow, PlaneType, Direction)
            
        self.add_window(NewWindow)

    def nav_left(self):
        WinID = self.get_active_window()
        if not self.exists():
            return False
        L, _, T, _ = self.Windows[WinID].get_size()
        ClosestRightBorder = 0
        LowestTopDiff = sys.maxint
        ClosestWindow = None

        for _WinId, Win in self.Windows.iteritems():
            if Win.is_shaded():
                continue

            _, _, WT, WR = Win.get_size()

            if L < WR: # Current window is to the right of Win
                continue
            
            if WR < ClosestRightBorder:
                continue

            TopBorderDiff = (T - WT) ** 2 # Magnitude of diff
            if LowestTopDiff < TopBorderDiff:
                continue

            ClosestRightBorder = WR
            LowestTopDiff = TopBorderDiff
            ClosestWindow = Win

        if ClosestWindow == None:
            log_debug(['No valid window found'])
            return
        log_debug(['Closest left window:', ClosestWindow.list_add_window()])
        ClosestWindow.activate()
    
    def nav_right(self):
        WinID = self.get_active_window()
        if not self.exists():
            return False
        _, _, T, R = self.Windows[WinID].get_size()
        ClosestLeftBorder = sys.maxint
        LowestTopDiff = sys.maxint
        ClosestWindow = None

        for _WinId, Win in self.Windows.iteritems():
            if Win.is_shaded():
                continue

            WL, _, WT, _ = Win.get_size()

            if WL < R: # Current window is to the left of Win
                continue
            
            if ClosestLeftBorder < WL:
                continue

            TopBorderDiff = (T - WT) ** 2 # Magnitude of diff
            if LowestTopDiff < TopBorderDiff:
                continue

            ClosestLeftBorder = WL
            LowestTopDiff = TopBorderDiff
            ClosestWindow = Win

        if ClosestWindow == None:
            log_debug(['No valid window found'])
            return
        log_debug(['Closest right window:', ClosestWindow.list_add_window()])
        ClosestWindow.activate()

    def nav_up(self):
        WinID = self.get_active_window()
        if not self.exists():
            return False
        L, _, T, _ = self.Windows[WinID].get_size()
        ClosestBottomBorder = 0
        LowestLeftDiff = sys.maxint
        ClosestWindow = None

        for _WinId, Win in self.Windows.iteritems():
            if Win.is_shaded():
                continue

            WL, WB, _, _ = Win.get_size()

            if T < WB: # Current window is to the bottom of Win
                continue
            
            if WB < ClosestBottomBorder:
                continue

            LeftBorderDiff = (L - WL) ** 2 # Magnitude of diff
            if LowestLeftDiff < LeftBorderDiff:
                continue

            ClosestBottomBorder = WB
            LowestLeftDiff = LeftBorderDiff
            ClosestWindow = Win

        if ClosestWindow == None:
            log_debug(['No valid window found'])
            return
        log_debug(['Closest top window:', ClosestWindow.list_add_window()])
        ClosestWindow.activate()

    def nav_down(self):
        WinID = self.get_active_window()
        if not self.exists():
            return False
        L, B, _, _ = self.Windows[WinID].get_size()
        ClosestTopBorder = sys.maxint
        LowestLeftDiff = sys.maxint
        ClosestWindow = None

        for _WinId, Win in self.Windows.iteritems():
            if Win.is_shaded():
                continue

            WL, _, WT, _ = Win.get_size()

            if WT < B: # Current window is to the bottom of Win
                continue
            
            if ClosestTopBorder < WT:
                continue

            LeftBorderDiff = (L - WL) ** 2 # Magnitude of diff
            if LowestLeftDiff < LeftBorderDiff:
                continue

            ClosestTopBorder = WT
            LowestLeftDiff = LeftBorderDiff
            ClosestWindow = Win

        if ClosestWindow == None:
            log_debug(['No valid window found'])
            return
        log_debug(['Closest top window:', ClosestWindow.list_add_window()])
        ClosestWindow.activate()
    
    def add_to_window_group(self, TargetId):
        WinId = self.get_active_window()
        TargetId = int(TargetId)
        if self.exists(WinId) or not self.exists(TargetId):
            log_debug(['Active window exists, or target window does not exist'])
            return False
        
        NewWindow = Window(WinId)
        TargetWin = self.Windows[TargetId]
        NodeParent = TargetWin.Parent
        if isinstance(NodeParent, WindowGroup):
            NewWindow.Parent = NodeParent
            NodeParent.add_window(NewWindow)
        else: # Create new window group
            NewWindowGroup = WindowGroup(NodeParent, NewWindow, [TargetWin])

            NodeParent.replace_child(TargetWin, NewWindowGroup)

            NewWindow.Parent = NewWindowGroup
            TargetWin.Parent = NewWindowGroup

            NewWindowGroup.activate_active_window()

        self.add_window(NewWindow)

    def activate_next_window(self, Increment):
        WinId = self.get_active_window()
        if not self.exists(WinId):
            log_debug(['Window doesn\'t exist'])
            return False
        Window = self.get_window(WinId)
        if not isinstance(Window.Parent, WindowGroup):
            log_debug(['Window not in window group'])
            return False
        
        Window.Parent.activate_next_window(Increment)

# TODO: All of these functions should be moved to Windows
"""Join a list of items into a single string
"""
def join_and_sanitize(List):
    if isinstance(List, str):
        return List

    NewList = []
    for Item in List:
        if isinstance(Item, str):
            NewList.append(Item)
            continue
        elif isinstance(Item, int):
            NewList.append(str(Item))
            continue
        else:
            raise Exception('Invalid type when attempting to join and santize')
    
    return ' '.join(NewList)

"""Call into the system and run Command (string)
"""
def call(Command):
    Cmd = join_and_sanitize(Command)
    proc = subprocess.Popen(Cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    Return, _err = proc.communicate()

    return Return

"""Extract window id using mouse to select window
"""
def mouse_select_window():
    return int(call('xdotool selectwindow').rstrip())

def debug_print():
    WindowsObj.DEBUG_PRINT()

def dir_str_to_plane_dir(Direction):
    if Direction == 'h':
        return dir_str_to_plane_dir('r')
    elif Direction == 'v':
        return dir_str_to_plane_dir('d')

    elif Direction == 'l':
        return PLANE.VERT, DIR.L
    elif Direction == 'd':
        return PLANE.HORZ, DIR.D
    elif Direction == 'u':
        return PLANE.HORZ, DIR.U
    elif Direction == 'r':
        return PLANE.VERT, DIR.R
    else:
        return False

def element(List, Index, Default):
    try:
        return List[Index]
    except:
        return Default

def log_info(List):
    log(['[INFO]'] + List)
def log_debug(List):
    log(['[DEBUG]'] + List)
def log_warning(List):
    log(['[WARN]'] + List)
def log_error(List):
    log(['[ERROR]'] + List)

def log(List):
    String = join_and_sanitize(List) + '\n'
    Timestamp = time.strftime('%Y-%m-%dT%H:%M:%S ', time.gmtime())
    String = Timestamp + String
    with open(LOG_PATH, 'a') as LogFile:
        LogFile.write(String)

def main(ARGS):
    Cmd = ARGS[1]
    log_info(['------- Start --------', 'Args:'] + ARGS[1:])
    if   Cmd == 'debug':
        debug_print()
    elif Cmd == 'restore':
        WindowsObj.restore_all()
    elif Cmd == 'list':
        print(WindowsObj.list_add_windows(ARGS[2]))
    elif Cmd == 'add':
        # Adding to a window : "add h 32478239 : window title"
        # Adding to a screen : "add h Screen 1"
        Plane = element(ARGS, 2, None)
        TargetId = element(ARGS, 3, None)
        ScreenIndex = element(ARGS, 4, None)

        if TargetId == None:
            log_debug(['No target id. Listing windows.'])
            print(WindowsObj.list_add_windows("add " + Plane + " ")) 
            return

        log_debug(['Target ID found. TargetId:', TargetId])
        if TargetId == 'Screen':
            log_debug(['Detected screen add. Screen Index:', ScreenIndex])
        else:
            log_debug(['Not a screen add'])

        PlaneType, Direction = dir_str_to_plane_dir(Plane)

        WindowsObj.add(PlaneType, Direction, TargetId, ScreenIndex)
    elif Cmd == 'ev':
        Increment = element(ARGS, 2, None)
        if Increment != None:
            Increment = int(Increment)
        log_debug(['Attempting to expand vertical size.'])
        WindowsObj.resize_vert('expand', Increment)
    elif Cmd == 'rv':
        log_debug(['Attempting to reduce vertical size.'])
        Increment = element(ARGS, 2, None)
        if Increment != None:
            Increment = int(Increment)
        WindowsObj.resize_vert('reduce', Increment)
    elif Cmd == 'eh':
        log_debug(['Attempting to expand horizontal size.'])
        Increment = element(ARGS, 2, None)
        if Increment != None:
            Increment = int(Increment)
        WindowsObj.resize_horz('expand', Increment)
    elif Cmd == 'rh':
        Increment = element(ARGS, 2, None)
        if Increment != None:
            Increment = int(Increment)
        log_debug(['Attempting to reduce horizontal size.'])
        WindowsObj.resize_horz('reduce', Increment)
    elif Cmd == 'change-plane':
        WindowsObj.change_plane()
    elif Cmd == 'swap-pane':
        WindowsObj.swap_pane_position()
    elif Cmd == 'swap':
        if len(ARGS) < 3:
            log_debug(['No target found. Listing windows'])
            print(WindowsObj.list_add_windows("swap ", True))
            return

        TargetId = int(ARGS[2])
        WindowsObj.swap_windows(TargetId)
    elif Cmd == 'min':
        WindowsObj.minimize_all()
    elif Cmd == 'unmin':
        WindowsObj.unminimize_all()
    elif Cmd == 'maximize':
        if len(ARGS) > 2:
            WinId = int(ARGS[2])
        else:
            WinId = WindowsObj.get_active_window()
        if not WindowsObj.exists(WinId):
            exit(1)
        WinIds = WindowsObj.Windows[WinId].list_screen_windows()
        if WindowsObj.Windows[WinId].Maximized:
            for Id in WinIds:
                WindowsObj.Windows[Id].activate()
                WindowsObj.Windows[Id].set_size()

            WindowsObj.Windows[WinId].activate()
            WindowsObj.Windows[WinId].Maximized = False
        else:
            for Id in WinIds:
                if Id == WinId:
                    continue
                WindowsObj.Windows[Id].minimize()
            WindowsObj.Windows[WinId].maximize()
    elif Cmd == 'kill':
        WinId = WindowsObj.get_active_window()
        if not WindowsObj.exists(WinId):
            exit(1)
        NextActiveWindow = WindowsObj.kill_window(WinId)
        print str(NextActiveWindow)
    elif Cmd == 'remove':
        WinId = WindowsObj.get_active_window()
        if not WindowsObj.exists(WinId):
            exit(1)
        WindowsObj.kill_window(WinId)
    elif Cmd == 'move-to':
        if len(ARGS) < 3:
            log_debug(['No target id. Listing windows.'])
            print(WindowsObj.list_add_windows("move-to ", True))
            return

        main(['', 'remove'])
        main(['', 'add', 'h', ARGS[2]])
    elif Cmd == 'nav-right':
        WindowsObj.nav_right()
    elif Cmd == 'nav-left':
        WindowsObj.nav_left()
    elif Cmd == 'nav-up':
        WindowsObj.nav_up()
    elif Cmd == 'nav-down':
        WindowsObj.nav_down()
    elif Cmd == 'add-to-group':
        if len(ARGS) < 3:
            log_debug(['No target id. Listing windows.'])
            print(WindowsObj.list_add_windows("move-to ", True))
            return

        TargetId = ARGS[2]
        WindowsObj.add_to_window_group(TargetId)
    elif Cmd == 'activate-next-window':
        WindowsObj.activate_next_window(1)
    elif Cmd == 'activate-prev-window':
        WindowsObj.activate_next_window(-1)

    pickle.dump(WindowsObj, open(DATA_PATH, "wb"))

# TODO: Parameters should be defined by an actual config file
# TODO: Although it would add another IO operation...
# Some initial parameters
GAP = 10
TOPBORDER = 25
LEFTBORDER = 2
RIGHTBORDER = 2
BOTTOMBORDER = 4
SHADEDSIZE = 25

# Include border calculations for the following programs
BORDER_WHITELIST = [
    'konsole',
    'spotify'
]

RESIZEINCREMENT = 10
RAPIDINCREMENT = 80
RESIZERAPIDTIME = 200 # milliseconds

DEBUG = False
DATA_PATH = "~/.woof/windows.dat"
DATA_PATH = call(['readlink -f', DATA_PATH]).rstrip() # Convert relative path to global path
LOG_PATH = "~/.woof/log/log"
LOG_PATH = call(['readlink -f', LOG_PATH]).rstrip() # Convert relative path to global path

# TODO: Seriously, clean up this code
# Initialise a tree
if sys.argv[1] == 'reload':
    WindowsObj = Windows(4, 3, 5760, 1080)
else:
    WindowsObj = pickle.load(open(DATA_PATH, "rb"))
    if WindowsObj.check_windows():
        WindowsObj.restore_all()

ARGS = sys.argv

main(ARGS)
exit(0)
