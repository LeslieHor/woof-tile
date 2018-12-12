import os
import subprocess

class Desktops:
    def __init__(self, Num, ScreensNum, ResHorz, ResVert):
        self.DesktopsCount = Num
        self.Desktops = [Screens(ScreensNum, ResHorz, ResVert)] * self.DesktopsCount

class Screens:
    def __init__(self, Num, ResHorz, ResVert):
        self.ScreensCount = Num
        self.Screens = []

        IncrementSize = ResHorz / self.ScreensCount
        Counter = 0
        for i in range(self.ScreensCount):
            CoordLeft = Counter
            CoordRight = Counter + IncrementSize
            
            NewScreen = Node(CoordLeft, CoordRight, True)
            self.Screens.append(NewScreen)

            Counter = CoordRight + 1

class Node:
    def __init__(self, TopLeftLimit, BottomRightLimit, HardLimits, Window = None):
        # TODO: Limits should actually be bounary-wise (top, left, right, bottom) and dynamically changed
        self.TopLeftLimit = TopLeftLimit
        self.BottomRightLimit = BottomRightLimit
        self.HardLimits = HardLimits

        self.ChildA = None
        self.ChildB = None
        self.WindowId = Window

        # TODO: needs information on desktop and screen indexes

    def become_window(self, WindowId):
        self.WindowId = WindowId

    def maximize_horz(self):
        subprocess.call(["wmctrl", "-ir", self.WindowId, "-b", "add,maximized_horz"])

    def unmaximize_horz(self):
        subprocess.call(["wmctrl", "-ir", self.WindowId, "-b", "remove,maximized_horz"])
        
def call(Command):
    proc = subprocess.Popen(['xdotool', 'getactivewindow'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ActiveWindow, err = proc.communicate()

    return ActiveWindow

def add_window():
    ActiveWindow = call(['xdotool', 'getactivewindow'])
#   ActiveDesktop = int(call(['xdotool', 'get_desktop']))

    return ActiveWindow

def current_desktop():
    call(['xdotool', 'get_desktop'])

WindowList = {}

DesktopsNum = int(call(['xdotool', 'get_num_desktops']))
Desktops = Desktops(DesktopsNum, 3, 5760, 1080)

ActiveWindow = add_window()
NewWindow = Desktops.Desktops[0].Screens[1]
NewWindow.become_window(str(ActiveWindow))

WindowList[ActiveWindow] = NewWindow
WindowList[ActiveWindow].unmaximize_horz()

print WindowList
