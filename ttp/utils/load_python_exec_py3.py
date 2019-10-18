def load_python_exec(text_data, builtins=None):
    """
    Function to provide compatibility with python 3.7 for loading text formwatted in 
    python using exec buil-in method. Exec syntaxis in pyton 2.6 different
    comared to python3.x and python3 spits "Invlaid Syntaxis error" while trying to 
    run code below.
    """
    data = {}
    # below can run on python3.7 as exec is a function not satatement for python3.7:
    exec(compile(text_data, '<string>', 'exec'), {"__builtins__" : builtins}, data)
    # run eval in case if data still empty as we might have python dictionary or list
    # expressed as string
    if not data:
        data = eval(text_data, None, None)
    return data