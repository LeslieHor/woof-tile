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
