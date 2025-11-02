import logging

log = logging.getLogger(__name__)


def str_to_unicode(data):
    return data, None


def to_int(data, *keys, intlist=False):
    if not keys:
        keys = list(data.keys())
    for k in keys:
        # check if given key exists
        try:
            v = data[k]
        except KeyError:
            continue

        # do best effort string to int conversion
        try:
            data[k] = int(v)
        except:
            try:
                data[k] = float(v)
            except:
                pass

        # convert list of integer strings to list of integers
        if intlist is True and isinstance(data[k], list):
            converted_list = []
            for i in data[k]:
                try:
                    converted_list.append(int(i))
                except:
                    try:
                        converted_list.append(float(i))
                    except:
                        converted_list.append(i)

            data[k] = converted_list

    return data, None
