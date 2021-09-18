def macro(data, *macro):
    result = data
    # extract macro names
    macro_names_list = [i.strip() for item in macro for i in item.split(",")]
    # run macro
    for macro_item in macro_names_list:
        if macro_item in _ttp_["macro"]:
            res = _ttp_["macro"][macro_item](result)
            if res is False:
                return result, False
            elif res in [True, None]:
                continue
            else:
                result = res
    return result, True
