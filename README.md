# woof-tile

DE/WM agnostic tiling manager.

Calls into other applications to handle window management. Uses rofi to present options.

Dependencies:
* rofi
* wmctrl
* xdotool
* xprop

## Installation

Clone the repo, and run `./install`.

It will copy the `woof` bash script into `~/bin/` and copy `woof.py` into `~/.woof/`.

It might error out if the following directories don't exist (haven't bothered to fix this):
* ~/bin/
* ~/.woof/
* ~/.woof/log/

## Usage

Assign hotkeys using xbindkeys to actually use it

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

"woof maximize"
    m:0x4d + c:94
    Control+Shift+Alt+Mod4 + backslash

"woof activate-next-window" # activate next window in window group
    m:0x4d + c:60
    Control+Shift+Alt+Mod4 + period

"woof activate-prev-window" # activate prev window in window group
    m:0x4d + c:59
    Control+Shift+Alt+Mod4 + comma

```
Use the rofi menu, it will list all options. You probably won't know what parameters to put it though. Use your best judgement or look through the code. I haven't bothered to properly document it all.

## Bugs that still exist

Plenty.