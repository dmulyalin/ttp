def lookup(data, name, add_field=False):
    path = [i.strip() for i in name.split('.')]
    found_value = None
    # get lookup dictionary/data:
    try:
        lookup = _ttp_["parser_object"].lookups
        for i in path:
            lookup = lookup.get(i,{})
    except KeyError:
        return data, None
    # perfrom lookup:
    try:
        found_value = lookup[data]
    except KeyError:
        return data, None
    # decide to replace match result or add new field:
    if add_field is not False:
        return data, {'new_field': {add_field: found_value}}
    else:
        return found_value, None

def rlookup(data, name, add_field=False):
    path = [i.strip() for i in name.split('.')]
    found_value = None
    # get lookup dictionary/data:
    try:
        rlookup = _ttp_["parser_object"].lookups
        for i in path:
            rlookup = rlookup.get(i,{})
    except KeyError:
        return data, None
    # perfrom rlookup:
    if isinstance(rlookup, dict) is False:
        return data, None
    for key in rlookup.keys():
        if key in data:
            found_value = rlookup[key]
            break
    # decide to replace match result or add new field:
    if found_value is None:
        return data, None
    elif add_field is not False:
        return data, {'new_field': {add_field: found_value}}
    else:
        return found_value, None