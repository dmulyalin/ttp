def to_str(data):
    return str(data), None
    
def to_list(data):
    return [data], None
    
def to_int(data):
    try:
        return int(data), None
    except ValueError:
        return data, None