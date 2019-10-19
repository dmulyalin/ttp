PHRASE    = '(\S+ {1})+?\S+',
ROW       = '(\S+ +)+?\S+',
ORPHRASE  = '\S+|(\S+ {1})+?\S+',
DIGIT     = '\d+',
IP        = '(?:[0-9]{1,3}\.){3}[0-9]{1,3}',
PREFIX    = '(?:[0-9]{1,3}\.){3}[0-9]{1,3}/[0-9]{1,2}',
IPV6      = '(?:[a-fA-F0-9]{1,4}:|:){1,7}(?:[a-fA-F0-9]{1,4}|:?)',
PREFIXV6  = '(?:[a-fA-F0-9]{1,4}:|:){1,7}(?:[a-fA-F0-9]{1,4}|:?)/[0-9]{1,3}',
_line_    = '.+',
WORD      = '\S+',
MAC       = '(?:[0-9a-fA-F]{2}(:|\.)){5}([0-9a-fA-F]{2})|(?:[0-9a-fA-F]{4}(:|\.)){2}([0-9a-fA-F]{4})'

def get(name):
    try:
        re = globals()[name][0]
        return re
    except KeyError:
        return False