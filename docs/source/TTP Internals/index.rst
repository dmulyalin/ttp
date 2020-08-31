TTP Internals
=============

This is to describe how TTP internals works, mainly to server as a reference for the Author and other developers.

Lazy loading system
-------------------

TTP uses lazy loading to load helper functions for all its components. That is to speed up TTP library loading time and to make sure that only dependencies required for functions in use need to be installed on the system, e.g. if you do not use excel output formatter, no need to install ``openpyxl`` library.

The way how lazy loader works is quite simple, work flow is:

1. Scan all files in all folders of TTP module using ``ast`` built in library to extract all functions names and assignments.
2. Save reference to function names and file where that function found in a lazy load class
3. Use directory and function name as a keys and store lazy load class in ``_ttp_`` dictionary
4. On first call to the function, lazy load class will perform import on the file where function in question located and will update references in ``_ttp_`` dictionary to all functions imported from that file

Implications of above process are:

1. To add new function to TTP, ones need to create .py file and place it in appropriate directory
2. The more files TTP need to scan the slower it will load, hence it make sense to combine functions of similar functionality in single file
3. All functions in single file will be imported on first call to any of the functions

Sometimes it is good to have name of TTP function to reference python reserved names, for instance ``set`` or ``del``, but, it is against best practices to name your functions with python
well reserved names. At the same time, TTP does not call function directly but rather reference to function stored in ``_ttp_`` dictionary and that reference got called upon request.

As a result ``_name_map_`` can be defined within .py file to map fuinction names within that file to ``_ttp_`` dictionary keys. 

Consider this example ::

    _name_map_ = {
        "set_func": "set"
    }
    
    def set_func():
        pass
	
Here, ``set_func`` is function defined within file, on load TTP will add reference to that function under ``set`` key in a ``_ttp_`` dictionary using ``_name_map_``
 

``_ttp_`` (not so) dunder dictionary
------------------------------------

The purpose of ``_ttp_`` is multi-fold:

1. TTP injects ``_ttp_`` dictionary into global name space of each file it imports, the same is true for macro functions. That way, functions or macro can reference one another through ``_ttp_`` dictionary without the need to explicitly define import statements.
2. Template global variables reference stored in ``_ttp_`` dictionary
3. Reference to various internal objects stored in ``_ttp_`` dictionary to work with them out of functions.

``_ttp_`` dictionary content is::

    {'formatters': {'csv': <ttp.ttp.CachedModule object at 0x03686370>,
                    'excel': <ttp.ttp.CachedModule object at 0x03669230>,
                    'jinja2': <ttp.ttp.CachedModule object at 0x036868B0>,
                    'json': <ttp.ttp.CachedModule object at 0x036C3330>,
                    'n2g': <ttp.ttp.CachedModule object at 0x03686930>,
                    'pprint': <ttp.ttp.CachedModule object at 0x03669A10>,
                    'raw': <ttp.ttp.CachedModule object at 0x03686610>,
                    'table': <ttp.ttp.CachedModule object at 0x03686130>,
                    'tabulate': <ttp.ttp.CachedModule object at 0x0367E690>,
                    'yaml': <ttp.ttp.CachedModule object at 0x036C3170>},
     'global_vars': {},
     'group': {'cerberus': <ttp.ttp.CachedModule object at 0x0367EF90>,
               'contains': <ttp.ttp.CachedModule object at 0x0367E8B0>,
               'contains_val': <ttp.ttp.CachedModule object at 0x0367E890>,
               'containsall': <ttp.ttp.CachedModule object at 0x036699F0>,
               'del': <ttp.ttp.CachedModule object at 0x0367E970>,
               'equal': <ttp.ttp.CachedModule object at 0x0367E910>,
               'exclude': <ttp.ttp.CachedModule object at 0x0367EFB0>,
               'exclude_val': <ttp.ttp.CachedModule object at 0x0367ED90>,
               'excludeall': <ttp.ttp.CachedModule object at 0x0367E5D0>,
               'expand': <ttp.ttp.CachedModule object at 0x0367EB10>,
               'itemize': <ttp.ttp.CachedModule object at 0x03686750>,
               'lookup': <ttp.ttp.CachedModule object at 0x036860B0>,
               'macro': <ttp.ttp.CachedModule object at 0x036860D0>,
               'record': <ttp.ttp.CachedModule object at 0x03686090>,
               'set': <ttp.ttp.CachedModule object at 0x03686170>,
               'sformat': <ttp.ttp.CachedModule object at 0x03686150>,
               'str_to_unicode': <ttp.ttp.CachedModule object at 0x03686DB0>,
               'to_int': <ttp.ttp.CachedModule object at 0x03686790>,
               'to_ip': <ttp.ttp.CachedModule object at 0x03686710>,
               'validate': <ttp.ttp.CachedModule object at 0x0367EB50>,
               'void': <ttp.ttp.CachedModule object at 0x0367EEF0>},
     'input': {'extract_commands': <ttp.ttp.CachedModule object at 0x0367ED30>,
               'macro': <ttp.ttp.CachedModule object at 0x0367E930>,
               'test': <ttp.ttp.CachedModule object at 0x0367EDD0>},
     'lookup': {'geoip2_db_loader': <ttp.ttp.CachedModule object at 0x0367EC70>},
     'macro': {},
     'match': {'append': <ttp.ttp.CachedModule object at 0x03690590>,
               'cidr_match': <ttp.ttp.CachedModule object at 0x0367E6D0>,
               'contains': <ttp.ttp.CachedModule object at 0x036901B0>,
               'contains_re': <ttp.ttp.CachedModule object at 0x03686BD0>,
               'count': <ttp.ttp.CachedModule object at 0x03686250>,
               'dns': <ttp.ttp.CachedModule object at 0x03686C10>,
               'endswith_re': <ttp.ttp.CachedModule object at 0x03686ED0>,
               'equal': <ttp.ttp.CachedModule object at 0x03690690>,
               'exclude': <ttp.ttp.CachedModule object at 0x03690670>,
               'exclude_re': <ttp.ttp.CachedModule object at 0x036864D0>,
               'geoip_lookup': <ttp.ttp.CachedModule object at 0x0367E990>,
               'gpvlookup': <ttp.ttp.CachedModule object at 0x036866D0>,
               'greaterthan': <ttp.ttp.CachedModule object at 0x036904B0>,
               'ip_info': <ttp.ttp.CachedModule object at 0x0367EE50>,
               'is_ip': <ttp.ttp.CachedModule object at 0x0367EFD0>,
               'isdigit': <ttp.ttp.CachedModule object at 0x036903B0>,
               'item': <ttp.ttp.CachedModule object at 0x0369D1D0>,
               'join': <ttp.ttp.CachedModule object at 0x03690570>,
               'joinmatches': <ttp.ttp.CachedModule object at 0x0369DFF0>,
               'lessthan': <ttp.ttp.CachedModule object at 0x036904D0>,
               'let': <ttp.ttp.CachedModule object at 0x0369D250>,
               'lookup': <ttp.ttp.CachedModule object at 0x036861F0>,
               'mac_eui': <ttp.ttp.CachedModule object at 0x036863F0>,
               'macro': <ttp.ttp.CachedModule object at 0x0367EEB0>,
               'notdigit': <ttp.ttp.CachedModule object at 0x03690490>,
               'notendswith_re': <ttp.ttp.CachedModule object at 0x03686E30>,
               'notequal': <ttp.ttp.CachedModule object at 0x036906B0>,
               'notstartswith_re': <ttp.ttp.CachedModule object at 0x036865D0>,
               'prepend': <ttp.ttp.CachedModule object at 0x036904F0>,
               'print': <ttp.ttp.CachedModule object at 0x03690530>,
               'rdns': <ttp.ttp.CachedModule object at 0x03686B50>,
               'record': <ttp.ttp.CachedModule object at 0x0367EBB0>,
               'replaceall': <ttp.ttp.CachedModule object at 0x03690550>,
               'resub': <ttp.ttp.CachedModule object at 0x03686A10>,
               'resuball': <ttp.ttp.CachedModule object at 0x03686E70>,
               'rlookup': <ttp.ttp.CachedModule object at 0x03686C90>,
               'set': <ttp.ttp.CachedModule object at 0x03686CD0>,
               'sformat': <ttp.ttp.CachedModule object at 0x03690250>,
               'startswith_re': <ttp.ttp.CachedModule object at 0x03686730>,
               'to_cidr': <ttp.ttp.CachedModule object at 0x0367EC50>,
               'to_float': <ttp.ttp.CachedModule object at 0x0367EF50>,
               'to_int': <ttp.ttp.CachedModule object at 0x0367E8F0>,
               'to_ip': <ttp.ttp.CachedModule object at 0x0367EB70>,
               'to_list': <ttp.ttp.CachedModule object at 0x0367EC90>,
               'to_net': <ttp.ttp.CachedModule object at 0x0367EBD0>,
               'to_str': <ttp.ttp.CachedModule object at 0x0367EE70>,
               'to_unicode': <ttp.ttp.CachedModule object at 0x0367E590>,
               'truncate': <ttp.ttp.CachedModule object at 0x03690510>,
               'unrange': <ttp.ttp.CachedModule object at 0x0369D8B0>,
               'uptimeparse': <ttp.ttp.CachedModule object at 0x036902D0>,
               'void': <ttp.ttp.CachedModule object at 0x03690450>},
     'output': {'deepdiff': <ttp.ttp.CachedModule object at 0x03686BB0>,
                'dict_to_list': <ttp.ttp.CachedModule object at 0x0369D9F0>,
                'is_equal': <ttp.ttp.CachedModule object at 0x03686F10>,
                'macro': <ttp.ttp.CachedModule object at 0x03686B10>,
                'traverse': <ttp.ttp.CachedModule object at 0x0369DBB0>,
                'validate': <ttp.ttp.CachedModule object at 0x0369D8F0>},
     'patterns': {'get': <ttp.ttp.CachedModule object at 0x0367E5B0>},
     'python_major_version': 3,
     'returners': {'file': <ttp.ttp.CachedModule object at 0x0369DD30>,
                   'self': <ttp.ttp.CachedModule object at 0x0367E730>,
                   'syslog': <ttp.ttp.CachedModule object at 0x0369DEF0>,
                   'terminal': <ttp.ttp.CachedModule object at 0x0367E6B0>},
     'sources': {'hopper': <ttp.ttp.CachedModule object at 0x0369D130>,
                 'netmiko': <ttp.ttp.CachedModule object at 0x0367EF30>,
                 'nornir': <ttp.ttp.CachedModule object at 0x0369DA30>},
     'template_obj': {},
     'ttp_object': <ttp.ttp.ttp object at 0x03160790>,
     'utils': {'get_attributes': <ttp.ttp.CachedModule object at 0x036907F0>,
               'guess': <ttp.ttp.CachedModule object at 0x036863D0>,
               'load_csv': <ttp.ttp.CachedModule object at 0x03690310>,
               'load_files': <ttp.ttp.CachedModule object at 0x03686410>,
               'load_ini': <ttp.ttp.CachedModule object at 0x03686FB0>,
               'load_json': <ttp.ttp.CachedModule object at 0x03690710>,
               'load_python': <ttp.ttp.CachedModule object at 0x03688230>,
               'load_python_exec': <ttp.ttp.CachedModule object at 0x03688D90>,
               'load_struct': <ttp.ttp.CachedModule object at 0x03686390>,
               'load_text': <ttp.ttp.CachedModule object at 0x036863B0>,
               'load_yaml': <ttp.ttp.CachedModule object at 0x036881D0>},
     'variable': {'get_date': <ttp.ttp.CachedModule object at 0x0367E9B0>,
                  'get_time': <ttp.ttp.CachedModule object at 0x0367EDB0>,
                  'get_time_ns': <ttp.ttp.CachedModule object at 0x0367E9F0>,
                  'get_timestamp': <ttp.ttp.CachedModule object at 0x0367E7D0>,
                  'get_timestamp_iso': <ttp.ttp.CachedModule object at 0x0367ED70>,
                  'get_timestamp_ms': <ttp.ttp.CachedModule object at 0x0367E790>,
                  'getfilename': <ttp.ttp.CachedModule object at 0x0367EB30>,
                  'gethostname': <ttp.ttp.CachedModule object at 0x03688F50>}}
				  
All above function contained within ``.py`` files and spread across respective directories of TTP module. Description of ``_ttp_`` dictionary keys:

* ``global_vars`` - dictionary to store variables produced by ``record`` function, this dictionary accessible between templates
* ``group`` - group function
* ``formatters`` - formatter function
* ``input`` - input functions
* ``lookup`` - lookup functions, such as database loaders
* ``macro`` - functions from template ``<macro>`` tag
* ``match`` - match variable functions
* ``output`` - output functions
* ``patterns`` - function to retrieve match variable regex patterns
* ``python_major_version`` - integer 2 or 3, representing python major version, used for py2/py3 interop
* ``returners`` - output returner functions
* ``sources`` - input source functions
* ``template_obj`` - references to template object
* ``ttp_object`` - reference to ttp parser object itself
* ``utils`` - various utilities
* ``variable`` - template variables getter function