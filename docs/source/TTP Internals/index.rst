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

    _ttp_: {
	
	
	}