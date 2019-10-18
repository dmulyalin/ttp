def let(data, name_or_value, var_value="" ):
    if not var_value:
        data = name_or_value
        return data, None
    else:
        return data, {'new_field': {name_or_value: var_value}}