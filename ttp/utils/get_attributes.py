import re
import logging
log = logging.getLogger(__name__)


def get_attributes(line):
    """Extract attributes from variable line string.
    Example:
        'peer | orphrase | exclude(-VM-)' -> [{'peer': []}, {'orphrase': []}, {'exclude': ['-VM-']}]
    Args:
        line (str): string that contains variable attributes i.e. "contains('vlan') | upper | split('.')"
  s  Returns:
        List of opts dictionaries containing extracted attributes
    """
    def get_args_kwargs(*args, **kwargs):
        return {'args': args, 'kwargs': kwargs}

    result=[]
    ATTRIBUTES=[i.strip() for i in line.split('|')]
    for item in ATTRIBUTES:
        opts = {'args': (), 'kwargs': {}, 'name': ''}
        if not item.strip(): # skip empty items like {{ bla | | bla2 }}
            continue
        # re search attributes like set(), upper, joinchar(',','-')
        itemDict = re.search('^(?P<name>\S+?)\s?(\((?P<options>.*)\))?$', item).groupdict()
        opts['name'] = itemDict['name']
        options = itemDict['options']
        # create options list from options string using eval:
        if options:
            try:
                args_kwargs = eval("get_args_kwargs({})".format(options))
            except NameError:
                log.critical("""ERROR: Failed to load arg/kwargs from line '{}' for options '{}' - possibly wrong syntaxes, 
make sure that all string arguments are within quotes, e.g. split(',') not split(,)""".format(line, options))
                raise SystemExit()
            opts.update(args_kwargs)
        else:
            options = []
        result.append(opts)
    return result