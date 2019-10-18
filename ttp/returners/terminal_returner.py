_name_map_ = {
"terminal_returner": "terminal"
}

def terminal_returner(D):
    if _ttp_["python_major_version"] is 2:
        if isinstance(D, str) or isinstance(D, unicode):
            print(D)
        else:
            print(str(D).replace('\\n', '\n'))
    elif _ttp_["python_major_version"] is 3:
        if isinstance(D, str):
            print(D)
        else:
            print(str(D).replace('\\n', '\n'))