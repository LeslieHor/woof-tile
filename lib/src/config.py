import os

# Paths
DATA_PATH = "~/.woof/tree.dat"
LOG_PATH = "~/.woof/log/log"
STATUSES_PATH = "~/.woof/status/"

# Config
GAP = 10
TOP_BORDER = 25
LEFT_BORDER = 0
RIGHT_BORDER = 0
BOTTOM_BORDER = 0

DEFAULT_BORDER_CORRECTIONS = ((0, 0), (-LEFT_BORDER-RIGHT_BORDER, -TOP_BORDER-BOTTOM_BORDER))

CLASS_A = ((LEFT_BORDER, TOP_BORDER), (-LEFT_BORDER-RIGHT_BORDER, -TOP_BORDER-BOTTOM_BORDER))
BORDER_CLASS_CORRECTIONS = {
    'konsole': CLASS_A,
    'Spotify': CLASS_A,
    'libreoffice': CLASS_A,
    'dolphin': CLASS_A,
    'mpv': ((LEFT_BORDER + 2, TOP_BORDER + 12), (-LEFT_BORDER-RIGHT_BORDER, -TOP_BORDER-BOTTOM_BORDER))
}

RESIZE_INCREMENT = 50

BENCHMARK = True
COMMENT_SEP = ' : '

WORKSPACE_CONFIG = [
    ('aux', ((0, 18), (1920, 1080 - 18))),
    ('internet', ((1920, 18), (1920, 1080 - 18))),
    ('video', ((3840, 18), (1920, 1080 - 18))),
    ('ide', None)
]

SAVED_LAYOUTS_POC = {
    'aux': ('v', 0.75, ('w', 'Spotify'), ('w', 'konsole'))
}

# Initialising Config
DATA_PATH = os.path.expanduser(DATA_PATH)  # Convert relative path to global path
LOG_PATH = os.path.expanduser(LOG_PATH)  # Convert relative path to global path
STATUSES_PATH = os.path.expanduser(STATUSES_PATH)  # Convert relative path to global path
