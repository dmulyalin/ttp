def table(data, path=None, missing="", key="", strict=True, headers=None, **kwargs):
    """Method to form table there table is list of lists,
    first item - headers row. Method used by csv/tabulate/excel
    formatters.

    :param path: (list) path items list to result within data
    :param strict: (bool) strict attribute to use with traverse function, if True
        will raise KeyError in case of path not within data
    :param missing: (str) value to use for missing headers
    :param key: (str) name of key to use for transforming dictionary to list
    :param headers: (list) list of table headers
    """
    headers = headers or []
    path = path or []
    table = []
    data_to_table = []
    source_data = []
    # normalize source_data to list:
    if isinstance(data, list):  # handle the case for template/global output
        source_data += data
    elif isinstance(data, dict):  # handle the case for group specific output
        source_data.append(data)
    # form data_to_table:
    for datum in source_data:
        item = _ttp_["output"]["traverse"](datum, path, strict)
        if not item:  # skip empty results
            continue
        elif isinstance(item, list):
            data_to_table += item
        elif isinstance(item, dict):
            # flatten dictionary data if key was given
            if key:
                data_to_table += _ttp_["output"]["dict_to_list"](
                    data=item, key_name=key
                )
            else:
                data_to_table.append(item)
    # create headers:
    if not headers:
        headers = set()
        for item in data_to_table:
            headers.update(list(item.keys()))
        headers = sorted(list(headers))
    # save headers row in table:
    table.insert(0, headers)
    # fill in table with data:
    for item in data_to_table:
        row = [missing for _ in headers]
        for k, v in item.items():
            if k in headers:
                row[headers.index(k)] = v
        table.append(row)
    return table
