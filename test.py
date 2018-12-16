import os
import subprocess
import time

class DIRECTION:
    LEFT = 0
    DOWN = 1
    UP = 2
    RIGHT = 3

class PLANE:
    HORZ = 0
    VERT = 1

class WorkSpace:
    def __init__(self, DesktopCount, ScreensCount, ResHorz, ResVert):
        self.DesktopsCount = DesktopCount
        self.Desktops = []

        for i in range(self.DesktopsCount):
            NewDesktop = Desktop(ScreensCount, ResHorz, ResVert)
            self.Desktops.append(NewDesktop)

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

class Screen:
    def __init__(self, LeftLimit, DownLimit, UpLimit, RightLimit):
        self.LeftLimit = LeftLimit
        self.DownLimit = DownLimit
        self.UpLimit = UpLimit
        self.RightLimit = RightLimit

        self.Child = None

    def DEBUG_PRINT(self, Level):
        print "\t" * Level + "Screen"
        self.Child.DEBUG_PRINT(Level + 1)

    def get_borders(self, _CallerChild):
            return self.LeftLimit, self.DownLimit, self.UpLimit, self.RightLimit

    def set_window(self, Window):
        if self.Child != None:
            return False

        self.Child = Window
        self.Child.set_size(self.LeftLimit, self.DownLimit, self.UpLimit, self.RightLimit)
        return True
    
    def add_node(self, CallerChild, NewWindowId, PlaneType, Direction):
        NewWindow = Window(NewWindowId)

        if Direction == DIRECTION.DOWN or Direction == DIRECTION.RIGHT:
            ChildA = CallerChild
            ChildB = NewWindow
        else:
            ChildA = NewWindow
            ChildB = CallerChild

        NewNode = Node(self, PlaneType, ChildA, ChildB)
        NewWindow.Parent = NewNode
        NewNode.refresh_children_size()

        self.Child = NewNode

        return NewWindow

    def border_check_left(self, Coord):
        return self.LeftLimit == Coord

    def border_check_down(self, Coord):
        return self.DownLimit == Coord

    def border_check_up(self, Coord):
        return self.UpLimit == Coord

    def border_check_right(self, Coord):
        return self.RightLimit == Coord

    def expand_horz(self, CallerChild):
        return False

    def reduce_horz(self, CallerChild):
        return False
    

class Node:
    def __init__(self, Parent, PlaneType, ChildA = None, ChildB = None):
        self.PlaneType = PlaneType
        self.Parent = Parent
        self.ChildA = ChildA
        self.ChildB = ChildB

    def set_split_coord(self):
        L, D, U, R = self.Parent.get_borders(self)
        if self.PlaneType == PLANE.HORZ:
            self.SplitCoord = (U + D) / 2
        else:
            self.SplitCoord = (L + R) / 2

    def DEBUG_PRINT(self, Level):
        if self.PlaneType == PLANE.HORZ:
            PT = "Horz"
        else:
            PT = "Vert"
        print "\t" * Level + "Node: " + PT
        self.ChildA.DEBUG_PRINT(Level + 1)
        self.ChildB.DEBUG_PRINT(Level + 1)

    def get_borders(self, CallerChild):
        L, D, U, R = self.Parent.get_borders(self)
        if CallerChild == self.ChildA:
            if self.PlaneType == PLANE.HORZ:
                D = self.SplitCoord
            else:
                R = self.SplitCoord
        else:
            if self.PlaneType == PLANE.HORZ:
                U = self.SplitCoord
            else:
                L = self.SplitCoord
        
        return L, D, U, R

    def refresh_children_size(self):
        L, D, U, R = self.Parent.get_borders(self)
        self.set_size(L, D, U, R)
        
    def set_size(self, L, D, U, R):
        if self.PlaneType == PLANE.HORZ:
            self.ChildA.set_size(L, self.SplitCoord, U, R)
            self.ChildB.set_size(L, D, self.SplitCoord, R)
        else:
            self.ChildA.set_size(L, D, U, self.SplitCoord)
            self.ChildB.set_size(self.SplitCoord, D, U, R)

    def add_node(self, CallerChild, NewWindowId, PlaneType, Direction):
        NewWindow = Window(NewWindowId)
        
        if Direction == DIRECTION.DOWN or Direction == DIRECTION.RIGHT:
            ChildA = CallerChild
            ChildB = NewWindow
        else: 
            ChildA = NewWindow
            ChildB = CallerChild

        NewNode = Node(self, PlaneType, ChildA, ChildB)
        ChildA.Parent = NewNode
        ChildB.Parent = NewNode

        if CallerChild == self.ChildA:
            self.ChildA = NewNode
        else:
            self.ChildB = NewNode

        self.refresh_children_size()

        return NewWindow

    def border_check_left(self, Coord):
        return self.Parent.border_check_left(Coord)

    def border_check_down(self, Coord):
        return self.Parent.border_check_down(Coord)

    def border_check_up(self, Coord):
        return self.Parent.border_check_up(Coord)

    def border_check_right(self, Coord):
        return self.Parent.border_check_right(Coord)

class Window:
    def __init__(self, WindowId, Parent = None):
        self.WindowIdDec = WindowId
        self.WindowIdHex = hex(int(WindowId))
        self.Parent = Parent

        self.unmaximize()

    def DEBUG_PRINT(self, Level):
        print "\t" * Level + "WindowID: " + str(self.WindowIdDec)

    def set_size(self, L, D, U, R):
        if self.Parent.border_check_left(L):
            LeftGap = GAP
        else:
            LeftGap = GAP / 2
        if self.Parent.border_check_down(D):
            DownGap = GAP
        else:
            DownGap = GAP / 2
        if self.Parent.border_check_up(U):
            UpGap = GAP
        else:
            UpGap = GAP / 2
        if self.Parent.border_check_right(R):
            RightGap = GAP
        else:
            RightGap = GAP / 2

        PosX = L + LEFTBORDER + LeftGap
        PosY = U  + TOPBORDER + UpGap
        SizeX = R - PosX - RIGHTBORDER - RightGap
        SizeY = D - PosY - BOTTOMBORDER - DownGap

        # xdotool will not override the plasma panel border
        # wmctrl is very particular about its args
        MVARG = '0,' + str(PosX) + ',' + str(PosY) + ',' + str(SizeX) + ',' + str(SizeY)
        call(['wmctrl -ir', self.WindowIdHex, '-e', MVARG])

    def split(self, NewWindowId, PlaneType, Direction):
        return self.Parent.add_node(self, NewWindowId, PlaneType, Direction)

    def unmaximize(self):
        subprocess.call(["wmctrl", "-ir", self.WindowIdHex, "-b", "remove,maximized_vert,maximized_horz"])
        
class Windows:
    def __init__(self):
        self.Windows = {}

    def add_window(self, Window):
        NewWindowId = Window.WindowIdDec
        self.Windows[NewWindowId] = Window

    def swap_windows(self, WindowIdA, WindowIdB):
        WindowA = self.Windows[WindowIdA]
        WindowB = self.Windows[WindowIdB]

        WindowA.set_id(WindowIdB)
        WindowB.set_id(WindowIdA)

        print WindowA.WindowIdDec
        print WindowB.WindowIdDec

        WindowA.reset_size()
        WindowB.reset_size()

def call(Command):
    Cmd = join_and_sanitize(Command)
    proc = subprocess.Popen(Cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    Return, err = proc.communicate()

    return Return

def current_desktop():
    return int(call(['xdotool', 'get_desktop']))

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

def DEBUG_LOG(X):
    if not DEBUG:
        return
    print X

# Some initial parameters
GAP = 10
TOPBORDER = 25
LEFTBORDER = 2
RIGHTBORDER = 2
BOTTOMBORDER = 4

HORZINCREMENT = 10
VERTINCREMENT = 10

DEBUG = True
WorkSpace = WorkSpace(4, 3, 5760, 1080)
Windows = Windows()

ActiveWindow = call('xdotool getactivewindow').rstrip()
Window0 = Window(ActiveWindow, WorkSpace.Desktops[0].Screens[0])
WorkSpace.Desktops[0].Screens[0].set_window(Window0)
Windows.add_window(Window0)
WorkSpace.Desktops[0].Screens[0].DEBUG_PRINT(0)

time.sleep(1.0)
call(['xdotool windowactivate', 113246214])
Window1 = Window0.split(113246214, PLANE.VERT, DIRECTION.LEFT)
Windows.add_window(Window1)
WorkSpace.Desktops[0].Screens[0].DEBUG_PRINT(0)

time.sleep(1.0)
call(['xdotool windowactivate', 115343366])
Window2 = Window0.split(115343366, PLANE.HORZ, DIRECTION.DOWN)
Windows.add_window(Window2)
WorkSpace.Desktops[0].Screens[0].DEBUG_PRINT(0)

# time.sleep(1.0)
# call(['xdotool windowactivate', 117440518])
# Window3 = Window1.split(117440518, PLANE.HORZ, DIRECTION.UP)
# Windows.add_window(Window3)

# time.sleep(1.0)
# call(['xdotool windowactivate', 119537670])
# Window4 = Window2.split(119537670, PLANE.VERT, DIRECTION.RIGHT)
# Windows.add_window(Window4)

# time.sleep(1.0)
# for i in range(8):
#     Window2.expand_horz()
#     time.sleep(0.2)

# time.sleep(1.0)
# for i in range(5):
#     Window1.expand_horz()
#     time.sleep(0.2)

# time.sleep(1.0)
# call(['xdotool windowactivate', 121634822])
# Window5 = Window3.split(121634822, PLANE.VERT, DIRECTION.RIGHT)
# Windows.add_window(Window5)

# WorkSpace.Desktops[0].Screens[0].DEBUG_PRINT(0)

# time.sleep(1.0)
# for i in range(4):
#     Window5.expand_horz()
#     time.sleep(0.2)

# time.sleep(1.0)
# for i in range(6):
#     Window3.reduce_horz()
#     time.sleep(0.2)

# time.sleep(1.0)
# for i in range(6):
#     Window1.reduce_horz()
#     time.sleep(0.2)
 
# time.sleep(1.0)
# for i in range(6):
#     Window3.expand_vert()
#     time.sleep(0.2)   
 
# time.sleep(1.0)
# for i in range(6):
#     Window3.reduce_vert()
#     time.sleep(0.2)   
 
# time.sleep(1.0)
# for i in range(8):
#     Window0.expand_vert()
#     time.sleep(0.2)   
 
# time.sleep(1.0)
# for i in range(3):
#     Window0.reduce_vert()
#     time.sleep(0.2)   

# time.sleep(1.0)
# Window3.convert_plane(PLANE.HORZ)
# time.sleep(1.0)
# Window3.convert_plane(PLANE.VERT)

# time.sleep(1.0)
# Window2.convert_plane(PLANE.HORZ)
# time.sleep(1.0)
# Window2.convert_plane(PLANE.VERT)

# time.sleep(1.0)
# Windows.swap_windows(Window2.WindowIdDec, Window5.WindowIdDec)

# time.sleep(1.0)

# call(['xdotool windowactivate', ActiveWindow])
# time.sleep(5.0)
# call(['xdotool windowminimize', 113246214])
# call(['xdotool windowminimize', 115343366])
# call(['xdotool windowminimize', 117440518])
# call(['xdotool windowminimize', 119537670])
# call(['xdotool windowminimize', 121634822])