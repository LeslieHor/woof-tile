import os
import json


CONFIG_PATH = "~/.woof/config.json"
CONFIG = {}


def expand_path(path):
    return os.path.expanduser(path)


def load_config():
    global CONFIG_PATH
    global CONFIG

    CONFIG_PATH = expand_path(CONFIG_PATH)
    with open(CONFIG_PATH) as json_file:
        CONFIG = json.load(json_file)

    CONFIG['data_path'] = expand_path(CONFIG.get('data_path'))
    CONFIG['log_path'] = expand_path(CONFIG.get('log_path'))
    CONFIG['statuses_dir'] = expand_path(CONFIG.get('statuses_dir'))
    CONFIG['layouts_dir'] = expand_path(CONFIG.get('layouts_dir'))


def get_config(key):
    global CONFIG

    if CONFIG == {}:
        load_config()

    return CONFIG.get(key)

def get_border_class_correction(window):
    window_class = window.get_window_class()
    border_class_corrections = get_config('border_class_corrections')

    if window_class in border_class_corrections:
        return border_class_corrections[window_class]
    else:
        return get_config('default_border_corrections')
