# woof-tile

DE/WM agnostic tiling manager

## TODO 
* ~~Make tree structure persistant~~
* ~~Dynamically add windows to tree~~
* ~~Enable splitting of nodes~~
* ~~Resize Horizontally~~
* ~~Resize Vertically~~
* ~~Allow swapping of windows~~
* Clean the code to not require the bash file
* Comment the code
* Document the application
* Use a dedicated config file
* ~~Use dedicated dir for data store~~
* Make it work for multiple desktops
* Allow resizing of Bottom/Right windows

## Notes

Assign hotkeys using xbindkeys to actually use it

Use:
```
rofi -show wf -modi wf:woof
```
To get the rofi menu. Rofi menu is required for adding and swapping windows

Entries for xbindkeys:
```
"rofi -show wf -modi wf:woof"
    m:0x4d + c:33
    Control+Shift+Alt+Mod4 + p

"woof reduce_horz"
    m:0x4d + c:29
    Control+Shift+Alt+Mod4 + y

"woof expand_vert"
    m:0x4d + c:30
    Control+Shift+Alt+Mod4 + u

"woof reduce_vert"
    m:0x4d + c:31
    Control+Shift+Alt+Mod4 + i

"woof expand_horz"
    m:0x4d + c:32
    Control+Shift+Alt+Mod4 + o

"woof maximize"
    m:0x4d + c:94
    Control+Shift+Alt+Mod4 + backslash
```

Would also recommend using shortcuts for navigating between windows. In Plasma, I use shortcuts to focus windows left, down, up and right