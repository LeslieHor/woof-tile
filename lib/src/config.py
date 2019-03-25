import os

# Paths
DATA_PATH = "~/.woof/windows.dat"
LOG_PATH = "~/.woof/log/log"
STATUSES_PATH = "~/.woof/status/"

# Config
GAP = 10
TOP_BORDER = 25
LEFT_BORDER = 0
RIGHT_BORDER = 0
BOTTOM_BORDER = 0
SHADED_SIZE = 25

DEFAULT_BORDER_CORRECTIONS = (0, -TOP_BORDER-BOTTOM_BORDER,
                              0, -LEFT_BORDER-RIGHT_BORDER)
BORDER_CLASS_CORRECTIONS = {
    'konsole': (LEFT_BORDER, -BOTTOM_BORDER, TOP_BORDER, -RIGHT_BORDER),
    'Spotify': (LEFT_BORDER, -BOTTOM_BORDER, TOP_BORDER, -RIGHT_BORDER),
    'libreoffice': (LEFT_BORDER, -BOTTOM_BORDER, TOP_BORDER, -RIGHT_BORDER),
    'dolphin': (LEFT_BORDER, -BOTTOM_BORDER, TOP_BORDER, -RIGHT_BORDER),
    'mpv': (LEFT_BORDER + 2, -BOTTOM_BORDER + 12, TOP_BORDER + 2, -RIGHT_BORDER + 12)
}

RESIZE_INCREMENT = 50
RAPID_INCREMENT = 50
RESIZE_RAPID_TIME = 200  # milliseconds

DEBUG = False
DEBUG_SPACER = ' '

START_SCREEN_COUNT = 10

SCREEN_CONFIG = [
    ((0, 18), (1920, 1080 - 18)),
    ((1920, 18), (1920, 1080 - 18)),
    ((3840, 18), (1920, 1080 - 18))
]

# Initialising Config
DATA_PATH = os.path.expanduser(DATA_PATH)  # Convert relative path to global path
LOG_PATH = os.path.expanduser(LOG_PATH)  # Convert relative path to global path
STATUSES_PATH = os.path.expanduser(STATUSES_PATH)  # Convert relative path to global path
