import logging
log = logging.getLogger(__name__)

def str_to_unicode(data):
    if _ttp_["python_major_version"] == 3:
        return data, None
    for key, value in data.items():
        if isinstance(value, str):
            data[key] = unicode(value)
    return data, None