import enums


def join_and_sanitize(list_):
    """Join a list of items into a single string"""
    if isinstance(list_, str):
        return list_

    new_list = []
    for item in list_:
        if isinstance(item, str):
            new_list.append(item)
        elif isinstance(item, int):
            new_list.append(str(item))
        elif isinstance(item, float):
            new_list.append(str(item))
        else:
            raise Exception('Invalid type when attempting to join and sanitize')

    return ' '.join(new_list)


def element(list_, index, default):
    try:
        return list_[index]
    except:
        return default


def cut_off_rest(arg):
    """
    Cuts of the comment of the args
    """
    return arg.split(' : ')[0]


def string_to_integer(value):
    if value == '':
        return None
    else:
        return int(value)


def json_com(value):
    if type(value) is int:
        return str(value)
    elif type(value) is float:
        return str(value)
    elif type(value) is list:
        return str(value)
    elif type(value) is str:
        return '"' + value + '"'
    elif value is None:
        return 'null'
    else:
        return str(value)


def combine_lists(list_1, list_2):
    if (list_1, list_2) == (None, None):
        return []
    elif list_1 is None:
        return list_2
    elif list_2 is None:
        return list_1
    else:
        return list_1 + list_2
