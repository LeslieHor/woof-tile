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
    ('aux', [[0, 18], [1920, 1080 - 18]]),
    ('internet', [[1920, 18], [1920, 1080 - 18]]),
    ('video', [[3840, 18], [1920, 1080 - 18]]),
    ('ide', None)
]

LAYOUTS_POC = {
    'aux': {
        'type': 'split_node',
        'split_ratio': 0.70,
        'plane_type': 'v',
        'children': [{'type': 'empty_container',
                      'window_class': 'Spotify'},
                     {'type': 'empty_container',
                      'window_class': 'konsole',
                      'window_title': 'aux1'}]},

    'internet': {'type': 'empty_container',
                 'window_class': 'Firefox'},

    'video': {'type': 'split_node',
              'split_ratio': 0.45,
              'plane_type': 'v',
              'children': [{'type': 'empty_container',
                            'window_class': 'Firefox'},
                           {'type': 'split_node',
                            'split_ratio': 0.60,
                            'plane_type': 'h',
                            'children': [{'type': 'empty_container',
                                          'window_class': 'Google-chrome'},
                                         {'type': 'empty_container',
                                          'window_class': 'konsole',
                                          'window_title': 'video1'}]}]},

    'ide': {'type': 'split_node',
            'split_ratio': 0.75,
            'plane_type': 'v',
            'children': [{'type': 'empty_container',
                          'window_class': 'jetbrains-idea-ce'},
                         {'type': 'split_node',
                          'split_ratio': 0.50,
                          'plane_type': 'h',
                          'children': [{'type': 'empty_container',
                                        'window_class': 'konsole',
                                        'window_title': 'ide1'},
                                       {'type': 'empty_container',
                                        'window_class': 'konsole',
                                        'window_title': 'ide2'}]}]},

    'test': {'type': 'split_node',
             'split_ratio': 0.40,
             'plane_type': 'v',
             'children': [{'type': 'empty_container',
                           'window_class': 'konsole'},
                          {'type': 'group_node',
                           'children': [{'type': 'empty_container',
                                         'window_class': 'konsole'},
                                        {'type': 'empty_container',
                                         'window_class': 'konsole'},
                                        {'type': 'empty_container',
                                         'window_class': 'konsole'}]}]}
}

# Initialising Config
DATA_PATH = os.path.expanduser(DATA_PATH)  # Convert relative path to global path
LOG_PATH = os.path.expanduser(LOG_PATH)  # Convert relative path to global path
STATUSES_PATH = os.path.expanduser(STATUSES_PATH)  # Convert relative path to global path

