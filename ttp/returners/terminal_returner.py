_name_map_ = {
"terminal_returner": "terminal"
}

def terminal_returner(D):
    """ Returner that prints results to terminal
    """
    # add colouring
    if "colour" in _ttp_["output_object"].attributes:
        from colorama import init
        init()
        R = "\033[0;31;40m" # RED
        G = "\033[0;32;40m" # GREEN
        Y = "\033[0;33;40m" # Yellow
        # B = "\033[0;34;40m" # Blue
        N = "\033[0m"       # Reset
        fttr = "{}{}{}"
        # get colour words from output
        red_words = _ttp_["output_object"].attributes.get("red", "False,No,Failed,Error,Failure,Fail,false,no,failed,error,failure,fail")
        green_words = _ttp_["output_object"].attributes.get("green","True,Yes,Success,Ok,true,yes,success,ok")
        yeallow_words = _ttp_["output_object"].attributes.get("yellow", "Warning,warning")
        # convert colour words to lists
        red_words = [i.strip() for i in red_words.split(",")]
        green_words = [i.strip() for i in green_words.split(",")]
        yeallow_words = [i.strip() for i in yeallow_words.split(",")]
        # add colouring to output
        for red_word in red_words:
            D = D.replace(red_word, fttr.format(R, red_word, N))
        for green_word in green_words:
            D = D.replace(green_word, fttr.format(G, green_word, N))
        for yeallow_word in yeallow_words:
            D = D.replace(yeallow_word, fttr.format(Y, yeallow_word, N))
    # print output
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