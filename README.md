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