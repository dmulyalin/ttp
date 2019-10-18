_name_map_ = {
"json_formatter": "json"
}

def json_formatter(data):
    """Method returns parsing result in json format.
    """
    from json import dumps
    return dumps(data, sort_keys=True, indent=4, separators=(',', ': '))