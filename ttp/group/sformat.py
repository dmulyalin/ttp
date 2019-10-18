def sformat(data, string, key):
    """Function to format string with group match results.
    
    **Arguments**
    
    * data - match results data
    * string - string to format
    * key - name of the key to assign formatting results to
    """
    try:
        data[key] = string.format(**data)
    except KeyError: # KeyError happens when not enough keys in **kwargs supplied to format method
        kwargs = _ttp_["global_vars"].copy()
        kwargs.update(_ttp_["parser_object"].vars)
        kwargs.update(data)
        try:
            data[key] = string.format(**kwargs)
        except:
            pass
    return data, True