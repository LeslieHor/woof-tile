# woof-tile

DE/WM agnostic tiling manager.

Calls into other applications to handle window management. Uses rofi to present options.

Dependencies:
* rofi
* wmctrl
* xdotool
* xprop

## Warning
This only works for a triple monitor set up with three 1920x1080 monitors arranged landscape in a single row. I hardcoded some stuff for my own set up. Don't worry. Eventually I will make it generalised for other configurations.

## Development
Development is done by implementing a new feature, using it for a while to ensure it works, then merging and tagging when it seems fine. Not great, I know.

## Installation

Clone the repo, and run `make install`.

It will copy the `woof` bash script into `~/bin/` and copy the `woof` python package into `~/.woof/`.


## Usage

Assign hotkeys using xbindkeys to actually use it

Commands:
```
ag : (add to group) add window as a group
ah : (add horizontal) add the active window the the right of a target window
av : (add vertical) add the active window below the target window
cp : (change plane) change a vertical split to a horizontal split and vice versa
db : (debug) print out debug information
eh : (expand horizontal) increase the horizontal size of the active window
ev : (expand vertical) increase the vertical size of the active window
gd : (nav down) focus window to the bottom
gl : (nav left) focus window to the left
gr : (nav right) focus window the the right
gu : (nav up) focus window to the top
kl : (kill) attempt to close the window and remove it from woof
la : (list) list the windows available for interaction
ls : (list screens) list all the screens in woof
mn : (minimize all) minimize all windows in woof
mv : (move to) move the active window to another window as a split
mx : (maximize) maximize the active window as if it was the only window on the screen
ns : (new screen) adds a new screen (not functional)
nw : (next window in group) activate next window in group
pd : (swap pane down) swaps this pane for the one to the down
pl : (swap pane left) swaps this pane for the one to the left
pr : (swap pane right) swaps this pane for the one to the right
pu : (swap pane up) swaps this pane for the one to the up
pw : (prev window in group) activate prev window in group
re : (restore) restore all window positions
rh : (reduce horizontal) decrease the horizontal size of the active window
rm : (remove) remove the window from woof
rs : (rename screen) rename the current screen
rv : (reduce vertical) decrease the vertical size of the active window
sl : (swap screen left) swap this screen for the left one
sp : (swap-pane) swap the two windows in the split
sr : (swap screen right) swap this screen for the right one
ss : (swap screen) swap the two screens
sw : (swap) swap the positions of two windows in the tree
```

Use:
```
rofi -show wf -modi wf:woof
```
To get the rofi menu. Rofi menu is required for adding and swapping windows and additional options

Example entries for xbindkeys:
```
"woof nav-left"
    m:0x4d + c:113
    Control+Shift+Alt+Mod4 + Left

"woof nav-down"
    m:0x4d + c:116
    Control+Shift+Alt+Mod4 + Down

"woof nav-up"
    m:0x4d + c:111
    Control+Shift+Alt+Mod4 + Up

"woof nav-right"
    m:0x4d + c:114
    Control+Shift+Alt+Mod4 + Right

"rofi -show wf -modi wf:woof"
    m:0x4d + c:33
    Control+Shift+Alt+Mod4 + p

"woof rh" # reduce horizontal size
    m:0x4d + c:29
    Control+Shift+Alt+Mod4 + y

"woof ev" # expand horizontal size
    m:0x4d + c:30
    Control+Shift+Alt+Mod4 + u

"woof rv" # reduce vertical size
    m:0x4d + c:31
    Control+Shift+Alt+Mod4 + i

"woof eh" # expand vertical size
    m:0x4d + c:32
    Control+Shift+Alt+Mod4 + o

"woof activate-next-window" # activate next window in window group
    m:0x4d + c:60
    Control+Shift+Alt+Mod4 + period

"woof activate-prev-window" # activate prev window in window group
    m:0x4d + c:59
    Control+Shift+Alt+Mod4 + comma
    
"woof kill"
    m:0x48 + c:53
    Alt+Mod4 + x
    
"woof maximize"
    m:0x48 + c:52
    Alt+Mod4 + z

"woof swap-screen 1"
    m:0x48 + c:10
    Alt+Mod4 + 1

"woof swap-screen 2"
    m:0x48 + c:11
    Alt+Mod4 + 2

"woof swap-screen 3"
    m:0x48 + c:12
    Alt+Mod4 + 3

"woof swap-screen 4"
    m:0x48 + c:13
    Alt+Mod4 + 4

"woof swap-screen 5"
    m:0x48 + c:14
    Alt+Mod4 + 5

"woof swap-screen 6"
    m:0x48 + c:15
    Alt+Mod4 + 6

"woof swap-screen 7"
    m:0x48 + c:16
    Alt+Mod4 + 7

"woof swap-screen 8"
    m:0x48 + c:17
    Alt+Mod4 + 8

"woof swap-screen 9"
    m:0x48 + c:18
    Alt+Mod4 + 9

"woof swap-screen 0"
    m:0x48 + c:19
    Alt+Mod4 + 0
```
Use the rofi menu, it will list all options. You probably won't know what parameters to put it though. Use your best judgement or look through the code. I haven't bothered to properly document it all.

## Bugs that still exist

Plenty.