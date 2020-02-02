_name_map_ = {
"set_func": "set"
}

def set_func(data, source, target="_use_source_"):
    # source - name of source variable to retrieve value
    # target - name of variable to save into
    if source in _ttp_["results_object"].vars:
        source_var_value = _ttp_["results_object"].vars[source]
        # get target var name:
        if target == "_use_source_":
            target = source
        data.update({target: source_var_value})
        return data, None
    else:
        return data, False