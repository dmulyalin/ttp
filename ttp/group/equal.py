def equal(data, key, value):
    if data.get(key, None) == value:
        return data, True
    return data, False