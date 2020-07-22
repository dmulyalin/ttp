_name_map_ = {
"csv_formatter": "csv"
}

def csv_formatter(data):
    """Method to dump list of dictionaries into table
    using provided separator, default is comma - ','
    """
    result = ""
    # form table - list of lists
    table = _ttp_["formatters"]["table"](data)
    sep = _ttp_["output_object"].attributes.get('sep', ',')
    # from results:
    result = sep.join(table[0])
    for row in table[1:]:
        try:
            result += "\n" + sep.join(row)
        except TypeError: # might happen if not all values in row are strings
            result += "\n" + sep.join([str(i) for i in row])            
    return result