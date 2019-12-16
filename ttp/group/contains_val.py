def contains_val(data, key, value):
    """
    check if certain key has certain value, return true if so and false otherwise
    """
    try:
        if data[key] == value:
            return data, True
        else:
            return data, False
    except KeyError:
        return data, True