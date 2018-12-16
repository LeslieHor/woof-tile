import os
import subprocess
import time
import pickle

class DIR:
    L = 0
    D = 1
    U = 2
    R = 3

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

    def which_screen(self, L):
        Screen = 0
        for S in range(self.Screens):
            if S.L <= S and S < S.R:
                return Screen
            Screen += 1

class Screen:
    def __init__(self, L, D, U, R):
        self.L = L
        self.D = D
        self.U = U
        self.R = R

        self.Child = None

    def DEBUG_PRINT(self, Level):
        print "\t" * Level + "Screen"
        self.Child.DEBUG_PRINT(Level + 1)

    def get_borders(self, _CallerChild):
        return self.L, self.D, self.U, self.R

    def initialise(self, NewWindow):
        self.Child = NewWindow
        self.Child.Parent = self
        self.Child.set_size()

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

    def expand_vert(self, CallerChild):
        return False

    def reduce_vert(self, CallerChild):
        return False

    def expand_horz(self, CallerChild):
        return False

    def reduce_horz(self, CallerChild):
        return False

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

    def set_split_default(self):
        L, D, U, R = self.Parent.get_borders(self)

        if self.PlaneType == PLANE.VERT:
            self.Split = (L + R) / 2
        else:
            self.Split = (U + D) / 2

    def split(self, CallerChild, NewWindow, PlaneType, Direction):
        NewNode = Node(PlaneType)
        NewNode.Parent = self

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

        self.ChildA.set_size()
        self.ChildB.set_size()

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

    def gap_correct_left(self, L):
        return self.Parent.gap_correct_left(L)
    def gap_correct_down(self, D):
        return self.Parent.gap_correct_down(D)
    def gap_correct_up(self, U):
        return self.Parent.gap_correct_up(U)
    def gap_correct_right(self, R):
        return self.Parent.gap_correct_right(R)

    def set_size(self, ResetDefault = False):
        if ResetDefault:
            self.set_split_default()

        self.ChildA.set_size(ResetDefault)
        self.ChildB.set_size(ResetDefault)

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

    def change_plane(self):
        if self.PlaneType == PLANE.VERT:
            PlaneType = PLANE.HORZ
        else:
            PlaneType = PLANE.VERT
        
        self.PlaneType = PlaneType
        self.set_size(True)

    def swap_pane_position(self):
        self.ChildA, self.ChildB = self.ChildB, self.ChildA
        self.set_size()
    
    def replace_child(self, CallerChild, NewChild):
        if CallerChild == self.ChildA:
            self.ChildA = NewChild
        else:
            self.ChildB = NewChild

    def kill_window(self, CallerChild):
        if CallerChild == self.ChildA:
            SurvivingChild = self.ChildB
        else:
            SurvivingChild = self.ChildA

        self.Parent.replace_child(self, SurvivingChild)
        SurvivingChild.Parent = self.Parent

        self.Parent.set_size()

class Window:
    def __init__(self, WindowId):
        self.WindowIdDec = int(WindowId)
        self.WindowIdHex = hex(int(WindowId))

        self.Parent = None

    def DEBUG_PRINT(self, Level):
        L, D, U, R = self.Parent.get_borders(self)
        print "\t" * Level + "WindowID: " + str(self.WindowIdDec) + ": " + str(L) + ", " + str(D) + ", " + str(U) + ", " + str(R)

    def set_size(self, _ResetDefault = False):
        L, D, U, R = self.Parent.get_borders(self)
        PX = L + LEFTBORDER + self.Parent.gap_correct_left(L)
        PY = U + TOPBORDER + self.Parent.gap_correct_up(U)
        SX = R - PX - RIGHTBORDER - self.Parent.gap_correct_right(R)
        SY = D - PY - BOTTOMBORDER - self.Parent.gap_correct_down(D)

        # xdotool will not override the plasma panel border
        # wmctrl is very particular about its args
        MVARG = '0,' + str(PX) + ',' + str(PY) + ',' + str(SX) + ',' + str(SY)
        call(['wmctrl -ir', self.WindowIdHex, '-e', MVARG])

    def split(self, NewWindow, PlaneType, Direction):
        self.Parent.split(self, NewWindow, PlaneType, Direction)

    def expand_vert(self):
        self.Parent.expand_vert(self)

    def reduce_vert(self):
        self.Parent.reduce_vert(self)

    def expand_horz(self):
        self.Parent.expand_horz(self)
    
    def reduce_horz(self):
        self.Parent.reduce_horz(self)

    def change_plane(self):
        self.Parent.change_plane()

    def swap_pane_position(self):
        self.Parent.swap_pane_position()
    
    def replace_child(self, NewChild):
        self.Parent.replace_child(self, NewChild)

    def kill_window(self):
        self.Parent.kill_window(self)

class Windows:
    def __init__(self, DesktopCount, ScreensCount, ResHorz, ResVert):
        self.WorkSpace = WorkSpace(DesktopCount, ScreensCount, ResHorz, ResVert)
        self.Windows = {}

    def add_window(self, Window):
        NewWindowId = Window.WindowIdDec
        self.Windows[NewWindowId] = Window

    def kill_window(self, WindowId):
        Window = self.Windows[WindowId]
        del self.Windows[WindowId]
        Window.kill_window()

    def swap_windows(self, WindowIdA, WindowIdB):
        WindowA = self.Windows[WindowIdA]
        WindowB = self.Windows[WindowIdB]

        WindowA.replace_child(WindowB)
        WindowB.replace_child(WindowA)

        WindowA.Parent, WindowB.Parent = WindowB.Parent, WindowA.Parent

        WindowA.set_size()
        WindowB.set_size()

    def restore_all(self):
        for WindowID, Window in self.Windows.iteritems():
            Window.set_size()

    def minimize_all(self, Except):
        for Key, _Value in self.Windows.iteritems():
            if Key == Except:
                continue
            call(['xdotool windowminimize', Key])

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

def call(Command):
    Cmd = join_and_sanitize(Command)
    proc = subprocess.Popen(Cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    Return, _err = proc.communicate()

    return Return

# Some initial parameters
GAP = 10
TOPBORDER = 25
LEFTBORDER = 2
RIGHTBORDER = 2
BOTTOMBORDER = 4

HORZINCREMENT = 10
VERTINCREMENT = 10

DEBUG = True
WindowsObj = Windows(4, 3, 5760, 1080)
WorkSpaceObj = WindowsObj.WorkSpace


## TESTING

def split_win(ID, OriginWin, PlaneType, Direction):
    time.sleep(0.2)
    call(['xdotool windowactivate', ID])
    NewWindow = Window(ID)
    OriginWin.split(NewWindow, PlaneType, Direction)
    WindowsObj.add_window(NewWindow)
    WorkSpaceObj.Desktops[0].Screens[0].DEBUG_PRINT(0)
    return NewWindow

ActiveWindow = call('xdotool getactivewindow').rstrip()
Window0 = Window(ActiveWindow)
WorkSpaceObj.Desktops[0].Screens[0].initialise(Window0)
WindowsObj.add_window(Window0)
WorkSpaceObj.Desktops[0].Screens[0].DEBUG_PRINT(0)

# Split tests
Window1 = split_win(113246214, Window0, PLANE.VERT, DIR.L)
Window2 = split_win(115343366, Window1, PLANE.VERT, DIR.R)
Window3 = split_win(117440518, Window1, PLANE.HORZ, DIR.D)
Window4 = split_win(119537670, Window2, PLANE.HORZ, DIR.U)
Window5 = split_win(121634822, Window0, PLANE.HORZ, DIR.D)
Window6 = split_win(123731974, Window5, PLANE.VERT, DIR.R)


# Resize tests
def resize(Window):
    for i in range(10):
        Window.expand_horz()
    for i in range(8):
        Window.reduce_horz()
    for i in range(10):
        Window.expand_vert()
    for i in range(8):
        Window.reduce_vert()
    time.sleep(0.5)

resize(Window0)
resize(Window1)
resize(Window2)
resize(Window3)
resize(Window4)
resize(Window5)
resize(Window6)

# Plane change tests
def change_plane(Window):
    time.sleep(0.5)
    Window.change_plane()
    time.sleep(0.5)
    Window.change_plane()

change_plane(Window0)
change_plane(Window1)
change_plane(Window2)
change_plane(Window3)
change_plane(Window4)
change_plane(Window5)
change_plane(Window6)

# Flip node positions
def swap_position(Window):
    time.sleep(0.5)
    Window.swap_pane_position()
    time.sleep(0.5)
    Window.swap_pane_position()

swap_position(Window0)
swap_position(Window1)
swap_position(Window2)
swap_position(Window3)
swap_position(Window4)
swap_position(Window5)
swap_position(Window6)

# Swapping windows test
WindowsObj.swap_windows(Window1.WindowIdDec, Window2.WindowIdDec)
time.sleep(1.0)
WindowsObj.swap_windows(Window0.WindowIdDec, Window4.WindowIdDec)
time.sleep(1.0)
WindowsObj.swap_windows(Window0.WindowIdDec, Window4.WindowIdDec)

call(['xdotool windowactivate', ActiveWindow])
time.sleep(2.0)
#WindowsObj.minimize_all(ActiveWindow)
pickle.dump(WindowsObj, open("windows.dat", "wb"))

for i in range(20):
    Window4.expand_vert()

time.sleep(1.0)

WindowsObj = pickle.load(open("windows.dat", "rb"))

WindowsObj.restore_all()