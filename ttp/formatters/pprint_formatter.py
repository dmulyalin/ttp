_name_map_ = {
"pprint_formatter": "pprint"
}

def pprint_formatter(data):
    """Method to pprint format results
    """
    from pprint import pformat
    return pformat(data, indent=4)