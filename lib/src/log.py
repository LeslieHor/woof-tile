import time
from helpers import join_and_sanitize
from config import *


def log_info(log_list):
    log(['[INFO]'] + log_list)


def log_debug(log_list):
    log(['[DEBUG]'] + log_list)


def log_warning(log_list):
    log(['[WARN]'] + log_list)


def log_error(log_list):
    log(['[ERROR]'] + log_list)


def log(log_list):
    string = join_and_sanitize(log_list) + '\n'
    timestamp = time.strftime('%Y-%m-%dT%H:%M:%S ', time.gmtime())
    string = timestamp + string
    with open(LOG_PATH, 'a') as log_file:
        log_file.write(string)
