import json
import os

import config


def get_layout(key):
    with open(config.get_config('layouts_dir') + key) as json_file:
        return json.load(json_file)


def get_layout_names():
    return os.listdir(config.get_config('layouts_dir'))
