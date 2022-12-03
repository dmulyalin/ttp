from copy import deepcopy

_name_map_ = {"copy_func": "copy"}


def copy_func(data, name):
    return data, {"new_field": {name: deepcopy(data)}}
