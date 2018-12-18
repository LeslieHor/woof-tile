#!/usr/bin/python

import subprocess
import pickle
import sys

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
        for Desktop in self.Desktops:
            Desktop.DEBUG_PRINT(1)

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
        for Screen in self.Screens:
            Screen.DEBUG_PRINT(Level + 1)

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
            self.Child.DEBUG_PRINT(Level + 1)

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
    def expand_vert(self, CallerChild):
        return False
    def reduce_vert(self, CallerChild):
        return False
    def expand_horz(self, CallerChild):
        return False
    def reduce_horz(self, CallerChild):
        return False

    """Reset pointer to child to None
    """
    def kill_window(self, CallerChild):
        if CallerChild != self.Child:
            return False
        self.Child = None

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
            PT = "Horz"
        else:
            PT = "Vert"
        L, D, U, R = self.Parent.get_borders(self)
        print "\t" * Level + "Node: " + PT + ": " + str(L) + ", " + str(D) + ", " + str(U) + ", " + str(R) + " - " + str(self.Split)
        self.ChildA.DEBUG_PRINT(Level + 1)
        self.ChildB.DEBUG_PRINT(Level + 1)

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
    def expand_vert(self, CallerChild):
        if CallerChild == self.ChildB or self.PlaneType == PLANE.VERT:
            return self.Parent.expand_vert(self)
        self.Split += VERTINCREMENT
        self.set_size()
    def reduce_vert(self, CallerChild):
        if CallerChild == self.ChildB or self.PlaneType == PLANE.VERT:
            return self.Parent.reduce_vert(self)
        self.Split -= VERTINCREMENT
        self.set_size()
    def expand_horz(self, CallerChild):
        if CallerChild == self.ChildB or self.PlaneType == PLANE.HORZ:
            return self.Parent.expand_horz(self)
        self.Split += HORZINCREMENT
        self.set_size()
    def reduce_horz(self, CallerChild):
        if CallerChild == self.ChildB or self.PlaneType == PLANE.HORZ:
            return self.Parent.reduce_horz(self)
        self.Split -= HORZINCREMENT
        self.set_size()

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

    """Return the 'other' child
    """
    def other_child(self, CallerChild):
        if CallerChild == self.ChildA:
            return self.ChildB
        return self.ChildA

"""Leaf node, representing a viewable window
"""
class Window:
    def __init__(self, WindowId):
        self.WindowIdDec = WindowId
        self.WindowIdHex = hex(int(WindowId))

        self.Parent = None
        self.Maximized = False

    def DEBUG_PRINT(self, Level):
        # L, D, U, R = self.Parent.get_borders(self)
        # print "\t" * Level + "WindowID: " + str(self.WindowIdDec) + ": " + str(L) + ", " + str(D) + ", " + str(U) + ", " + str(R)
        print "\t" * Level + "WindowID: " + str(self.WindowIdDec) + ": " + call(['xdotool getwindowname', self.WindowIdDec]).rstrip() + str(self.Maximized)

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
    |                             |
    |  +--------+                 |
    |  |        |                 |
    |  |        |                 |
    |  +--------+                 |
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
        WindowClass = call(['xprop -id', self.WindowIdDec, '| grep WM_CLASS | sed \'s/.* = "//\' | sed \'s/".*//\'']).rstrip()
        for Name in BORDER_WHITELIST:
            if Name in WindowClass:
                return 1
        return 0

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
        L, D, U, R = self.get_size()
        PX, PY, SX, SY = self.border_gap_correct(L, D, U, R)
        self.set_size_override(PX, PY, SX, SY)

    """Request the parent to split to add a new window
    """
    def split(self, NewWindow, PlaneType, Direction):
        self.Parent.split(self, NewWindow, PlaneType, Direction)

    """Request parent to resize window.

    If the request fails, attempt to resize sibling window to accomplish the
    resize.
    """
    def expand_vert(self):
        if not self.Parent.expand_vert(self):
            OtherChild = self.Parent.other_child(self)
            self.Parent.reduce_vert(OtherChild)
    def reduce_vert(self):
        if not self.Parent.reduce_vert(self):
            OtherChild = self.Parent.other_child(self)
            self.Parent.expand_vert(OtherChild)
    def expand_horz(self):
        if not self.Parent.expand_horz(self):
            OtherChild = self.Parent.other_child(self)
            self.Parent.reduce_horz(OtherChild)
    def reduce_horz(self):
        if not self.Parent.reduce_horz(self):
            OtherChild = self.Parent.other_child(self)
            self.Parent.expand_horz(OtherChild)

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
        self.Parent.kill_window(self)

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

"""Stores and manages the workspaces and windows

Contains pointer to workspace and a dictionary of windows ID --> Window Object
"""
class Windows:
    def __init__(self, DesktopCount, ScreensCount, ResHorz, ResVert):
        self.WorkSpace = WorkSpace(DesktopCount, ScreensCount, ResHorz, ResVert)
        self.Windows = {}

    def DEBUG_PRINT(self):
        self.WorkSpace.DEBUG_PRINT()

    """Add the window the dictionary
    """
    def add_window(self, Window):
        NewWindowId = Window.WindowIdDec
        self.Windows[NewWindowId] = Window

    """Request the window to kill itself and remove from dictionary
    """
    def kill_window(self, WindowId):
        Window = self.Windows[WindowId]
        Window.kill_window()
        del self.Windows[WindowId]

    """Given two window ids, swap their positions in the tree
    """
    def swap_windows(self, WindowIdA, WindowIdB):
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
            do_it(['', 'maximize', WindowA.WindowIdDec])
        if WindowB.Maximized:
            do_it(['', 'maximize', WindowB.WindowIdDec])

    """Unminimize and unmaximize all windows

    Restores all windows to their intended positions
    """
    def restore_all(self):
        self.unminimize_all()
        for _WindowID, Window in self.Windows.iteritems():
            Window.Maximized = False
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
    def list_add_windows(self, Prepend):
        List = []
        for _WinId, Win in self.Windows.iteritems():
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
    def exists(self, WinId):
        return WinId in self.list_windows()

    """Minimze all windows
    """
    def minimize_all(self):
        for _Key, Win in self.Windows.iteritems():
            Win.minimize()

    """Unminimize all windows

    Because we need to unminimize by activating the window, window focus
    will be overwritten. Windows are not restored to their intended
    positions
    """
    def unminimize_all(self):
        for _Key, Win in self.Windows.iteritems():
            Win.activate()
            Win.Maximized = False

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

"""Get ID of current active window
"""
def get_active_window():
    return int(call('xdotool getactivewindow').rstrip())

"""Extract window id using mouse to select window
"""
def mouse_select_window():
    return int(call('xdotool selectwindow').rstrip())

# TODO: Parameters should be defined by an actual config file
# Some initial parameters
GAP = 10
TOPBORDER = 25
LEFTBORDER = 2
RIGHTBORDER = 2
BOTTOMBORDER = 4

# Include border calculations for the following programs
BORDER_WHITELIST = [
    'konsole',
    'spotify'
]

HORZINCREMENT = 10
VERTINCREMENT = 10

DEBUG = False
DATA_PATH = "~/.woof/windows.dat"
DATA_PATH = call(['readlink -f', DATA_PATH]).rstrip()

# TODO: Seriously, clean up this code
# Initialise a tree
if sys.argv[1] == 'reload':
    WindowsObj = Windows(4, 3, 5760, 1080)
else:
    WindowsObj = pickle.load(open(DATA_PATH, "rb"))
    if WindowsObj.check_windows():
        WindowsObj.restore_all()

ARGS = sys.argv

def do_it(ARGS):
    Cmd = ARGS[1]
    if   Cmd == 'debug':
        WindowsObj.DEBUG_PRINT()
    elif Cmd == 'restore':
        WinId = get_active_window()
        WindowsObj.restore_all()
        call(['xdotool windowactivate', WinId])
    elif Cmd == 'list':
        print(WindowsObj.list_add_windows(ARGS[2]))
    elif Cmd == 'select_test':
        print "select_test"
        Id = call('xdotool selectwindow').rstrip()
        print call(['xdotool getwindowgeometry', Id])
    elif Cmd == 'addrofi':
        WinId = get_active_window()
        TargetId = ARGS[3]
        if WindowsObj.exists(WinId):
            exit(1)
        if TargetId == 'Screen':
            ScreenId = int(ARGS[4])
            if WindowsObj.WorkSpace.Desktops[0].Screens[ScreenId].Child != None:
                exit(1)
            NewWindow = Window(WinId)
            NewWindow.remove_wm_maximize()
            WindowsObj.WorkSpace.Desktops[0].Screens[ScreenId].initialise(NewWindow)
            WindowsObj.add_window(NewWindow)
        else:
            TargetId = int(TargetId)

            if ARGS[2] == "h":
                PlaneType = PLANE.VERT
                Dir = DIR.R
            else:
                PlaneType = PLANE.HORZ
                Dir = DIR.D

            NewWindow = Window(WinId)
            NewWindow.remove_wm_maximize()
            WindowsObj.Windows[TargetId].split(NewWindow, PlaneType, Dir)
            WindowsObj.add_window(NewWindow)
    elif Cmd == 'add':
        if len(ARGS) < 3:
            exit(1)
        WinId = get_active_window()
        TargetId = mouse_select_window()
        if WindowsObj.exists(WinId):
            exit(1)
        if not WindowsObj.exists(TargetId):
            XCoord = int(call(['xdotool getwindowgeometry', TargetId, '| grep Position | sed \'s/.*Position: //\' | sed \'s/,.*//\'']).rstrip())
            Screen = WindowsObj.WorkSpace.Desktops[0].which_screen(XCoord)
            if WindowsObj.WorkSpace.Desktops[0].Screens[Screen].Child != None:
                exit(1)
            NewWindow = Window(WinId)
            NewWindow.remove_wm_maximize()
            WindowsObj.WorkSpace.Desktops[0].Screens[Screen].initialise(NewWindow)
            WindowsObj.add_window(NewWindow)
        else:
            Dir = ARGS[2]
            if Dir == 'h':
                Dir = 'r'
            if Dir == 'v':
                Dir = 'd'

            if Dir == 'l':
                PlaneType = PLANE.VERT
                Direction = DIR.L
            elif Dir == 'd':
                PlaneType = PLANE.HORZ
                Direction = DIR.D
            elif Dir == 'u':
                PlaneType = PLANE.HORZ
                Direction = DIR.U
            else: # Dir == 'r'
                PlaneType = PLANE.VERT
                Direction = DIR.R
            
            NewWindow = Window(WinId)
            NewWindow.remove_wm_maximize()
            WindowsObj.Windows[TargetId].split(NewWindow, PlaneType, Direction)
            WindowsObj.add_window(NewWindow)

    elif Cmd == 'expand_vert':
        WinId = get_active_window()
        if not WindowsObj.exists(WinId):
            exit(1)
        WindowsObj.Windows[WinId].expand_vert()
    elif Cmd == 'reduce_vert':
        WinId = get_active_window()
        if not WindowsObj.exists(WinId):
            exit(1)
        WindowsObj.Windows[WinId].reduce_vert()
    elif Cmd == 'expand_horz':
        WinId = get_active_window()
        if not WindowsObj.exists(WinId):
            exit(1)
        WindowsObj.Windows[WinId].expand_horz()
    elif Cmd == 'reduce_horz':
        WinId = get_active_window()
        if not WindowsObj.exists(WinId):
            exit(1)
        WindowsObj.Windows[WinId].reduce_horz()
    elif Cmd == 'change_plane':
        WinId = get_active_window()
        if not WindowsObj.exists(WinId):
            exit(1)
        WindowsObj.Windows[WinId].change_plane()
    elif Cmd == 'swap_pane':
        WinId = get_active_window()
        if not WindowsObj.exists(WinId):
            exit(1)
        WindowsObj.Windows[WinId].swap_pane_position()
    elif Cmd == 'swaprofi':
        WinId = get_active_window()
        TargetId = int(ARGS[2])
        if not WindowsObj.exists(WinId) or not WindowsObj.exists(TargetId):
            exit(1)
        WindowsObj.swap_windows(WinId, TargetId)
    elif Cmd == 'swap':
        WinId = get_active_window()
        TargetId = mouse_select_window()
        if not WindowsObj.exists(WinId) or not WindowsObj.exists(TargetId):
            exit(1)
        WindowsObj.swap_windows(WinId, TargetId)
    elif Cmd == 'min':
        WindowsObj.minimize_all()
    elif Cmd == 'unmin':
        WinId = get_active_window()
        WindowsObj.unminimize_all()
        call(['xdotool windowactivate', WinId])
    elif Cmd == 'maximize':
        if len(ARGS) > 2:
            WinId = int(ARGS[2])
        else:
            WinId = get_active_window()
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
        WinId = get_active_window()
        if not WindowsObj.exists(WinId):
            return
        WindowsObj.kill_window(WinId)
    elif Cmd == 'remove':
        WinId = get_active_window()
        if not WindowsObj.exists(WinId):
            exit(1)
        WindowsObj.kill_window(WinId)



    pickle.dump(WindowsObj, open(DATA_PATH, "wb"))

do_it(ARGS)
exit(0)