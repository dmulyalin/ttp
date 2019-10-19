

def get(name):
    try:
        return globals()[name]
    except KeyError:
        return False