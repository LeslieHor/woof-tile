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

    def set_window(self, Window):
        if self.Child != None:
            return False

        self.Child = Window
        self.Child.set_size(self.LeftLimit, self.DownLimit, self.UpLimit, self.RightLimit)
        self.Child.reset_size()
        return True
    
    def add_node(self, CallerChild, NewWindowId, PlaneType, Direction):
        NewNode = Node(self, PlaneType)
        NewWindow = NewNode.split(CallerChild, NewWindowId, PlaneType, Direction)

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
    

class Node:
    def __init__(self, Parent, PlaneType):
        self.PlaneType = PlaneType
        self.Parent = Parent
        self.ChildA = None
        self.ChildB = None

    def DEBUG_PRINT(self, Level):
        if self.PlaneType == PLANE.HORZ:
            PT = "Horz"
        else:
            PT = "Vert"
        print "\t" * Level + "Node: " + PT
        self.ChildA.DEBUG_PRINT(Level + 1)
        self.ChildB.DEBUG_PRINT(Level + 1)

    def add_node(self, CallerChild, NewWindowId, PlaneType, Direction):
        CallerChildId = CallerChild.WindowIdDec
        
        NewNode = Node(self, PlaneType)
        NewWindow = NewNode.split(CallerChild, NewWindowId, PlaneType, Direction)

        if CallerChildId == self.ChildA.WindowIdDec:
            self.ChildA.Parent = NewNode
            self.ChildA = NewNode
        else:
            self.ChildB.Parent = NewNode
            self.ChildB = NewNode

        return NewWindow

    def split(self, CurrWindow, NewWindowId, PlaneType, Direction):
        NewWindow = Window(NewWindowId, self)
        ALeft, ADown, AUp, ARight = CurrWindow.get_borders()
        BLeft, BDown, BUp, BRight = ALeft, ADown, AUp, ARight 
        
        if Direction == DIRECTION.DOWN or Direction == DIRECTION.RIGHT:
            self.ChildA = CurrWindow
            self.ChildB = NewWindow
        else:
            self.ChildA = NewWindow
            self.ChildB = CurrWindow

        if PlaneType == PLANE.HORZ:
            ADown = ADown - (ADown - AUp) / 2
            BUp = ADown
        else:
            ARight = ARight - (ARight - ALeft) / 2
            BLeft = ARight
        
        self.ChildA.set_size(ALeft, ADown, AUp, ARight)
        self.ChildA.reset_size()
        self.ChildB.set_size(BLeft, BDown, BUp, BRight)
        self.ChildB.reset_size()

        self.ChildA.Parent = self
        self.ChildB.Parent = self

        DEBUG_LOG(["current window id", CurrWindow.WindowIdDec])

        CL, CD, CU, CR = CurrWindow.get_borders()
        DEBUG_LOG(["curr window moved", CL, CD, CU, CR])

        DL, DD, DU, DR = NewWindow.get_borders()
        DEBUG_LOG(["new window split at", DL, DD, DU, DR])

        return NewWindow

    def border_check_left(self, Coord):
        return self.Parent.border_check_left(Coord)

    def border_check_down(self, Coord):
        return self.Parent.border_check_down(Coord)

    def border_check_up(self, Coord):
        return self.Parent.border_check_up(Coord)

    def border_check_right(self, Coord):
        return self.Parent.border_check_right(Coord)

    def expand_right(self):
        self.ChildB.expand_right()
        
        if self.PlaneType == PLANE.HORZ:
            self.ChildA.expand_right()

    def reduce_left(self):
        self.ChildA.reduce_left()

        if self.PlaneType == PLANE.HORZ:
            self.ChildB.reduce_left()

    def expand_horz(self, CallerChild):
        if self.PlaneType == PLANE.HORZ:
            self.Parent.expand_horz(self)
            return

        if CallerChild == self.ChildB:
            self.Parent.expand_horz(self)
            return

        # if CallerChild.Right - CallerChild.Left < 10:
        #     self.Parent.expand_horz(self)

        self.ChildA.expand_right()
        self.ChildB.reduce_left()
        
class Window:
    def __init__(self, WindowId, Parent):
        self.WindowIdDec = WindowId
        self.WindowIdHex = hex(int(WindowId))
        self.Parent = Parent

        self.unmaximize()

    def DEBUG_PRINT(self, Level):
        print "\t" * Level + "WindowID: " + str(self.WindowIdDec)

    def get_borders(self):
        return self.Left, self.Down, self.Up, self.Right

    def set_size(self, Left, Down, Up, Right):
        self.Left = Left
        self.Down = Down
        self.Up = Up
        self.Right = Right

    def reset_size(self):
        if self.Parent.border_check_left(self.Left):
            LeftGap = GAP
        else:
            LeftGap = GAP / 2
        if self.Parent.border_check_down(self.Down):
            DownGap = GAP
        else:
            DownGap = GAP / 2
        if self.Parent.border_check_up(self.Up):
            UpGap = GAP
        else:
            UpGap = GAP / 2
        if self.Parent.border_check_right(self.Right):
            RightGap = GAP
        else:
            RightGap = GAP / 2

        PosX = self.Left + LEFTBORDER + LeftGap
        PosY = self.Up  + TOPBORDER + UpGap
        SizeX = self.Right - PosX - RIGHTBORDER - RightGap
        SizeY = self.Down - PosY - BOTTOMBORDER - DownGap

        # xdotool will not override the plasma panel border
        # wmctrl is very particular about its args
        MVARG = '0,' + str(PosX) + ',' + str(PosY) + ',' + str(SizeX) + ',' + str(SizeY)
        call(['wmctrl -ir', self.WindowIdHex, '-e', MVARG])

    def expand_right(self):
        self.Right += HORZINCREMENT
        self.reset_size()
    def reduce_right(self):
        self.Right -= HORZINCREMENT
        self.reset_size()

    def expand_left(self):
        self.Left -= HORZINCREMENT
        self.reset_size()
    def reduce_left(self):
        self.Left += HORZINCREMENT
        self.reset_size()

    def expand_horz(self):
        self.Parent.expand_horz(self)

    def split(self, NewWindowId, PlaneType, Direction):
        NewWindow = self.Parent.add_node(self, NewWindowId, PlaneType, Direction)
        return NewWindow

    def unmaximize(self):
        subprocess.call(["wmctrl", "-ir", self.WindowIdHex, "-b", "remove,maximized_vert,maximized_horz"])
        
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
ActiveWindow = call('xdotool getactivewindow').rstrip()
Window0 = Window(ActiveWindow, WorkSpace.Desktops[0].Screens[0])
WorkSpace.Desktops[0].Screens[0].set_window(Window0)
time.sleep(1.0)
call(['xdotool windowactivate', 113246214])
Window1 = Window0.split(113246214, PLANE.VERT, DIRECTION.LEFT)
time.sleep(1.0)
call(['xdotool windowactivate', 115343366])
Window2 = Window0.split(115343366, PLANE.HORZ, DIRECTION.DOWN)
time.sleep(1.0)
call(['xdotool windowactivate', 117440518])
Window3 = Window1.split(117440518, PLANE.HORZ, DIRECTION.UP)
time.sleep(1.0)
call(['xdotool windowactivate', 119537670])
Window4 = Window2.split(119537670, PLANE.VERT, DIRECTION.RIGHT)

time.sleep(1.0)
for i in range(8):
    Window2.expand_horz()
    time.sleep(0.2)

time.sleep(1.0)
for i in range(5):
    Window1.expand_horz()
    time.sleep(0.2)

time.sleep(1.0)
call(['xdotool windowactivate', 121634822])
Window5 = Window3.split(121634822, PLANE.VERT, DIRECTION.RIGHT)

WorkSpace.Desktops[0].Screens[0].DEBUG_PRINT(0)

time.sleep(1.0)
for i in range(4):
    Window5.expand_horz()
    time.sleep(0.2)

call(['xdotool windowactivate', ActiveWindow])
time.sleep(5.0)
call(['xdotool windowminimize', 113246214])
call(['xdotool windowminimize', 115343366])
call(['xdotool windowminimize', 117440518])
call(['xdotool windowminimize', 119537670])
call(['xdotool windowminimize', 121634822])