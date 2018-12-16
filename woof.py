#!/usr/bin/python

import subprocess
import pickle
import sys

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

    def DEBUG_PRINT(self):
        print "WorkSpace"
        for D in self.Desktops:
            D.DEBUG_PRINT(1)

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
        for S in self.Screens:
            S.DEBUG_PRINT(Level + 1)

    def which_screen(self, L):
        Screen = 0
        for S in self.Screens:
            if S.L <= L and L < S.R:
                return Screen
            Screen += 1
        return Screen

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

    def kill_window(self, CallerChild):
        if CallerChild != self.Child:
            return False
        self.Child = None

    def replace_child(self, CallerChild, NewChild):
        if CallerChild != self.Child:
            return False
        self.Child = NewChild
    
    def set_size(self, ResetDefault = False):
        self.Child.set_size()

    def list_screen_windows(self):
        return self.Child.window_ids()

    def get_screen_borders(self):
        return self.L, self.D, self.U, self.R

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

    def list_screen_windows(self):
        return self.Parent.list_screen_windows()
    
    def window_ids(self):
        return self.ChildA.window_ids() + self.ChildB.window_ids()

    def get_screen_borders(self):
        return self.Parent.get_screen_borders()

class Window:
    def __init__(self, WindowId):
        self.WindowIdDec = WindowId
        self.WindowIdHex = hex(int(WindowId))

        self.Parent = None
        self.Maximized = False

    def DEBUG_PRINT(self, Level):
        L, D, U, R = self.Parent.get_borders(self)
        # print "\t" * Level + "WindowID: " + str(self.WindowIdDec) + ": " + str(L) + ", " + str(D) + ", " + str(U) + ", " + str(R)
        print "\t" * Level + "WindowID: " + str(self.WindowIdDec) + ": " + call(['xdotool getwindowname', self.WindowIdDec]).rstrip() + str(self.Maximized)

    def get_size(self):
        return self.Parent.get_borders(self)

    def border_multiplier(self):
        WindowTitle = call(['xdotool getwindowname', self.WindowIdDec]).rstrip()
        for Name in BORDER_WHITELIST:
            if Name in WindowTitle:
                return 1
        return 0

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

    def set_size_override(self, PX, PY, SX, SY):
        # xdotool will not override the plasma panel border
        # wmctrl is very particular about its args
        MVARG = '0,' + str(PX) + ',' + str(PY) + ',' + str(SX) + ',' + str(SY)
        call(['wmctrl -ir', self.WindowIdHex, '-e', MVARG])

    def set_size(self, _ResetDefault = False):
        L, D, U, R = self.get_size()
        PX, PY, SX, SY = self.border_gap_correct(L, D, U, R)
        self.set_size_override(PX, PY, SX, SY)

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

    def minimize(self):
        call(['xdotool windowminimize', self.WindowIdDec])

    def activate(self):
        call(['xdotool windowactivate', self.WindowIdDec])
    
    def list_screen_windows(self):
        return self.Parent.list_screen_windows()

    def window_ids(self):
        return [self.WindowIdDec]

    def maximize(self):
        self.Maximized = True
        L, D, U, R = self.Parent.get_screen_borders()
        PX, PY, SX, SY = self.border_gap_correct(L, D, U, R)
        self.set_size_override(PX, PY, SX, SY)

    def remove_wm_maximize(self):
        subprocess.call(["wmctrl", "-ir", self.WindowIdHex, "-b", "remove,maximized_vert,maximized_horz"])
    
    def list_add_window(self, Prepend = ''):
        WindowName = call(['xdotool getwindowname', self.WindowIdDec]).rstrip()
        return Prepend + str(self.WindowIdDec) + " : " + WindowName

class Windows:
    def __init__(self, DesktopCount, ScreensCount, ResHorz, ResVert):
        self.WorkSpace = WorkSpace(DesktopCount, ScreensCount, ResHorz, ResVert)
        self.Windows = {}

    def DEBUG_PRINT(self):
        self.WorkSpace.DEBUG_PRINT()

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

        if WindowA.Maximized:
            do_it(['', 'maximize', WindowA.WindowIdDec])
        if WindowB.Maximized:
            do_it(['', 'maximize', WindowB.WindowIdDec])

    def restore_all(self):
        self.unminimize_all()
        for _WindowID, Window in self.Windows.iteritems():
            Window.Maximized = False
            Window.set_size()

    def check_windows(self):
        HexIdsStr = call(' wmctrl -l | awk -F" " \'$2 == 0 {print $1}\'')
        HexIds = HexIdsStr.split("\n")
        DecIds = [int(X, 0) for X in HexIds if X != '']
        Fix = False
        for WinId, Win in self.Windows.iteritems():
            if WinId not in DecIds:
                Win.kill_window()
                Fix = True

            else:
                # TEMP FIXES
                None

        return Fix

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

    def list_windows(self):
        List = []
        for WinId, _Win in self.Windows.iteritems():
            List.append(WinId)
        List.sort()
        return List

    def exists(self, WinId):
        return WinId in self.list_windows()

    def minimize_all(self):
        for _Key, Win in self.Windows.iteritems():
            Win.minimize()

    def unminimize_all(self):
        for _Key, Win in self.Windows.iteritems():
            Win.activate()
            Win.Maximized = False

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

def get_active_window():
    return int(call('xdotool getactivewindow').rstrip())

def mouse_select_window():
    return int(call('xdotool selectwindow').rstrip())

# Some initial parameters
GAP = 10
TOPBORDER = 25
LEFTBORDER = 2
RIGHTBORDER = 2
BOTTOMBORDER = 4

# Include border calculations for the following programs
BORDER_WHITELIST = [
    'Konsole'
]

HORZINCREMENT = 10
VERTINCREMENT = 10

DEBUG = False
DATA_PATH = "~/Git/woof-tile/windows.dat"
DATA_PATH = call(['readlink -f', DATA_PATH]).rstrip()

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
        call(['xdotool windowkill', WinId])
        if not WindowsObj.exists(WinId):
            exit(1)
        WindowsObj.kill_window(WinId)
    elif Cmd == 'remove':
        WinId = get_active_window()
        if not WindowsObj.exists(WinId):
            exit(1)
        WindowsObj.kill_window(WinId)



    pickle.dump(WindowsObj, open(DATA_PATH, "wb"))

do_it(ARGS)