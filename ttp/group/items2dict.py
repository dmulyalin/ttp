def items2dict(data, key_name, value_name):
    """
    Function to combine values of key_name and value_name keys in
    a key-value pair.
    """
    # do sanity checks
    if key_name not in data or value_name not in data:
        return data, False
    # combine values
    data[data.pop(key_name)] = data.pop(value_name)

    return data, None
