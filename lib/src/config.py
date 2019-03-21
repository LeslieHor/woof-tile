import os

# Paths
DATA_PATH = "~/.woof/windows.dat"
LOG_PATH = "~/.woof/log/log"

# Config
GAP = 10
TOP_BORDER = 25
LEFT_BORDER = 2
RIGHT_BORDER = 2
BOTTOM_BORDER = 4
SHADED_SIZE = 25

BORDER_WHITELIST = [
    'konsole',
    'Spotify',
    'libreoffice',
    'dolphin'
]

SPECIAL_SHITS = {
    'mpv': [2, 12]
}

RESIZE_INCREMENT = 10
RAPID_INCREMENT = 80
RESIZE_RAPID_TIME = 200  # milliseconds

DEBUG = False
DEBUG_SPACER = ' '

WORKSPACES = 4
SCREENS = 3
HORIZONTAL_DIMENSION = 5760
VERTICAL_DIMENSION = 1080

SCREEN_CONFIG = [
    ((0, 0), (1920, 1080)),
    ((1920, 0), (1920, 1080)),
    ((3840, 0), (1920, 1080))
]

# Initialising Config
DATA_PATH = os.path.expanduser(DATA_PATH)  # Convert relative path to global path
LOG_PATH = os.path.expanduser(LOG_PATH)  # Convert relative path to global path
