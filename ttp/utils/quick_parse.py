from ttp import ttp


def quick_parse(
    data=None, template=None, ttp_kwargs=None, parse_kwargs=None, result_kwargs=None
):
    """
    Function to parse data and return results.

    :param data: (str) data to parse
    :param template: (str) template string
    :param ttp_kwargs: (dict) kwargs to use while instantiating TTP object
    :param parse_kwargs: (dict ) kwargs to use with ``parse`` method call
    :param result_kwargs: (dict ) kwargs to use with ``result`` method call

    Sample usage::

        from ttp import quick_parse

        template = '''
        <group>
        interface {{ interface }}
        description {{ description | ORPHRASE }}
        ip address {{ ip }} {{ mask }}
        </group>
        '''

        data = '''
        interface Lo0
        ip address 124.171.238.50 32
        !
        interface Lo1
        description this interface has description
        ip address 1.1.1.1 32
        '''

        parsing_result = quick_parse(data, template)
    """
    ttp_kwargs = ttp_kwargs or {}
    parse_kwargs = parse_kwargs or {}
    result_kwargs = result_kwargs or {}
    # instantiate TTP parser object
    if data:
        parser = ttp(data=data, template=template, **ttp_kwargs)
    else:
        parser = ttp(template=template, **ttp_kwargs)

    # parse
    parser.parse(**parse_kwargs)

    # return results
    return parser.result(**result_kwargs)
