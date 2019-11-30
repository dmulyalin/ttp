def lookup(data, name=None, template=None, group=None, add_field=False):
    found_value = None
    lookup_data = {}
    # try get lookup dictionary/data from lookup tags:
    if name:
        path = [i.strip() for i in name.split('.')]
        lookup_data = _ttp_["parser_object"].lookups
    elif template:
        path = [i.strip() for i in template.split('.')]
        for template in _ttp_['ttp_object']._templates:
            if template.name == path[0]:
                # use first input results in the template:
                lookup_data = template.results[0]     
                path = path[1:]
                break
    elif group:
        path = [i.strip() for i in group.split('.')]
        for result in _ttp_["template_obj"].results:
            if path[0] in result:
                lookup_data = result[path[0]]
                break
        path = path[1:]
    else:
        log.info("ttp.lookup no lookup data name provided, doing nothing.")
        return Data, None
    for i in path:
        lookup_data = lookup_data.get(i,{})
    # perform lookup:
    try:
        found_value = lookup_data[data]
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