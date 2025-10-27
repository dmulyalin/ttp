# -*- coding: utf-8 -*-

__version__ = "0.9.5"

import re
import os
import logging
import copy
import ast
import pickle
from xml.etree import cElementTree as ET
from multiprocessing import Process, cpu_count, JoinableQueue, Queue
from sys import version_info
from sys import getsizeof
from collections import OrderedDict


# Initiate global variables
log = logging.getLogger(__name__)


"""
==============================================================================
TTP LAZY IMPORT SYSTEM
==============================================================================
"""


class CachedModule:
    """Class that contains name of the function and path to module/file
    that contains that function, on first call to this class, function
    will be imported into _ttp_ dictionary, subsequent calls we call
    function directly
    """

    def __init__(self, import_path, parent_dir, function_name, functions, _ttp_):
        self.import_path = import_path
        self.parent_dir = parent_dir
        self.function_name = function_name
        self.parent_module_functions = functions
        self._ttp_ = _ttp_

    def load(self):
        # import cached function and insert it into _ttp_ dictionary
        abs_import = "ttp."
        if __name__ in ("__main__", "__mp_main__"):
            abs_import = ""
        path = "{abs}{imp}".format(abs=abs_import, imp=self.import_path)
        module = __import__(path, fromlist=[None])
        # add _ttp_ to module globals space
        setattr(module, "_ttp_", self._ttp_)
        try:
            _name_map_ = getattr(module, "_name_map_")
        except AttributeError:
            _name_map_ = {}
        for func_name in self.parent_module_functions:
            name = _name_map_.get(func_name, func_name)
            self._ttp_[self.parent_dir][name] = getattr(module, func_name)

    def __call__(self, *args, **kwargs):
        # this method invoked on CachedModule class call, triggering function import
        log.info(
            "calling CachedModule: module '{}', function '{}'".format(
                self.import_path, self.function_name
            )
        )
        self.load()
        # call original function
        return self._ttp_[self.parent_dir][self.function_name](*args, **kwargs)


def lazy_import_functions():
    """function to collect a list of all files/directories within ttp module,
    parse .py files using ast and extract information about all functions
    to cache them within _ttp_ dictionary
    """
    _ttp_ = {
        "macro": {},
        "python_major_version": version_info.major,
        "global_vars": {},
        "template_obj": {},
        "vars": {},
    }
    log.info("ttp.lazy_import_functions: starting functions lazy import")

    # try to load previously pickled/cached _ttp_ dictionary
    path_to_cache = os.getenv("TTPCACHEFOLDER", os.path.dirname(__file__))
    cache_file = os.path.join(path_to_cache, "ttp_dict_cache.pickle")
    try:
        if os.path.isfile(cache_file):
            with open(cache_file, "rb") as f:
                _ttp_ = pickle.load(f)
            # use unpickled _ttp_ dictionary if it of the same python version
            if (
                _ttp_["python_major_version"] == version_info.major
                and _ttp_.get("__version__") == __version__
            ):
                log.info(
                    "ttp.lazy_import_functions: loaded _ttp_ dictionary from ttp_dict_cache.pickle"
                )
                return _ttp_
            # rebuilt _ttp_ dictionary as it is of different version
            else:
                _ttp_ = {
                    "macro": {},
                    "python_major_version": version_info.major,
                    "global_vars": {},
                    "template_obj": {},
                    "vars": {},
                    "__version__": __version__,
                }
    except Exception as e:
        log.warning(
            "ttp.lazy_import_functions: failed load ttp_dict_cache.pickle, loading functions directly, error '{}'".format(
                e
            )
        )
    # load functions from files instead
    exclude = "_py3.py" if _ttp_["python_major_version"] == 2 else "_py2.py"
    exclude_modules = ["ttp.py"]
    # load and parse files
    log.info("ttp.lazy_import_functions: loading files for ast parsing")
    for item in os.walk(os.path.dirname(__file__)):
        root, dirs, files = item
        for f in files:
            if not (
                f.endswith(".py")
                and not f.startswith("_")
                and not f.endswith(exclude)
                and f not in exclude_modules
            ):
                continue
            try:
                module_file = open("{}/{}".format(root, f), mode="r", encoding="utf-8")
            except:
                # in some versions of python open() does not support encoding
                module_file = open("{}/{}".format(root, f), mode="r")
            node = ast.parse(module_file.read())
            assignments = [n for n in node.body if isinstance(n, ast.Assign)]
            functions = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
            functions = [f for f in functions if (not f.startswith("_"))]
            # get _name_map_
            _name_map_ = {}
            for assignment in assignments:
                # stop if _name_map_ already found
                if _name_map_:
                    break
                for target in assignment.targets:
                    if target.id == "_name_map_":
                        _name_map_.update(
                            {
                                key.value: assignment.value.values[index].value
                                for index, key in enumerate(assignment.value.keys)
                            }
                        )
            # fill in _ttp_ dictionary with CachedModule class
            parent_path, filename = os.path.split(module_file.name)
            _, parent_dir = os.path.split(parent_path)
            for func_name in functions:
                name = _name_map_.get(func_name, func_name)
                path = "{}.{}".format(parent_dir, filename.replace(".py", ""))
                _ttp_.setdefault(parent_dir, {})[name] = CachedModule(
                    path, parent_dir, name, functions, _ttp_
                )
            module_file.close()
    # try to cache/pickle _ttp_ to a file for future use
    try:
        with open(cache_file, "wb") as f:
            pickle.dump(_ttp_, f)
    except Exception as e:
        log.warning(
            "ttp.lazy_import_functions: failed to save cache at '{}', error '{}'".format(
                cache_file, e
            )
        )
    log.info("ttp.lazy_import_functions: finished functions lazy import")
    return _ttp_


"""
==============================================================================
MAIN TTP CLASS
==============================================================================
"""


class ttp:
    """Template Text Parser main class to load data, templates, lookups, variables
    and dispatch data to parser object to parse in single or multiple processes,
    construct final results and run outputs.

    :param data: (obj) file object or OS path to text file or directory with text files with data to parse
    :param template: (obj) one of: file object, OS path to template text file, OS path to directory with
        templates text files, template text string, TTP Templates path (ttp://x/y/z), OS path to template
        text file within ``TTP_TEMPLATES_DIR`` directory, where ``TTP_TEMPLATES_DIR`` is an environment variable.
    :param base_path: (str) base OS path prefix to load data from for template's inputs
    :param log_level: (str) level of logging "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
    :param log_file: (str) path where to save log file
    :param vars: (dict) dictionary of variables to make available to ttp parser
    :param dynamic_path_key_to_int: (bool) if True converts dynamic path keys to integers, False by default

    Example::

        from ttp import ttp
        parser = ttp(data="/os/path/to/data/dir/", template="/os/path/to/template.txt")
        parser.parse()
        result = parser.result(format="json")
        print(result[0])

    Or if ``TTP_TEMPLATES_DIR=/absolute/os/path/to/templates/dir/``::

        from ttp import ttp
        parser = ttp(data="/os/path/to/data/dir/", template="template.txt")
        parser.parse()
        result = parser.result(format="json")
        print(result[0])
    """

    def __init__(
        self,
        data="",
        template="",
        log_level="WARNING",
        log_file=None,
        base_path="",
        vars=None,
        dynamic_path_key_to_int=False,
    ):
        self.__data_size = 0
        self.__datums_count = 0
        self._templates = []
        self.base_path = base_path
        self.multiproc_threshold = 5242880  # in bytes, equal to 5MBytes
        self.vars = vars or {}  # dictionary of variables to add to each template vars
        self.lookups = {}
        # setup logging
        logging_config(log_level, log_file)
        # lazy import all functions - _ttp_ dictionary acts as a glue between
        # all TTP objects and plugins, it forms a basis for overall module operation
        self._ttp_ = lazy_import_functions()
        # add reference to TTP object in _ttp_ dunder
        self._ttp_["ttp_object"] = self
        self._ttp_["dynamic_path_key_to_int"] = dynamic_path_key_to_int
        # check if template given, if so - load it
        if template != "":
            self.add_template(template=template)
        # check if data given, if so - load it to all templates
        if data != "":
            self.add_input(data=data, template_name="_all_")

    def add_input(
        self,
        data,
        input_name="Default_Input",
        template_name="_root_template_",
        groups=None,
    ):
        """Method to load data to be parsed. Data associated with certain
        input of ``input_name`` and template of ``template_name``.

        .. warning:: ``add_input`` should be called only after templates added

        **Parameters**

        * ``data`` text data or OS path to text file or directory with text files with data to parse.
          Also can be structured data - list or dictionary - will be passed to input as is, so that
          it can be pre-processed using input macro function(s)
        * ``input_name`` (str) name of the input to put data in, default is *Default_Input*
        * ``groups`` (list) list of group names to use to parse this input data
        * ``template_name`` (str) name of the template to add input for
        """
        groups = groups or ["all"]
        if not self._templates:
            log.warning(
                "ttp.add_input: no TTP templates to associate input data with, load template(s) first."
            )
        # form a list of ((type, url|text,), input_name, groups,) tuples
        data_items = self._ttp_["utils"]["load_files"](path=data, read=False)
        if data_items:
            [
                template.update_input(
                    data=data_items, input_name=input_name, groups=groups
                )
                for template in self._templates
                if template.name == template_name or template_name == "_all_"
            ]

    def set_input(
        self,
        data,
        input_name="Default_Input",
        template_name="_root_template_",
        groups=None,
    ):
        """Method to replace existing templates inputs data with new set of data. This
        method is alias to ``clear_input`` and ``add_input`` methods.

        .. warning:: ``set_input`` should be called only after templates added

        **Parameters**

        * ``data`` text data or OS path to text file or directory with text files with data to parse
          Also can be structured data - list or dictionary - will be passed to input as is, so that
          it can be pre-processed using input macro function(s)
        * ``input_name`` (str) name of the input to put data in, default is *Default_Input*
        * ``groups`` (list) list of group names to use to parse this input data
        * ``template_name`` (str) name of the template to set input for
        """
        groups = groups or ["all"]
        if not self._templates:
            log.warning(
                "ttp.set_input: no TTP templates to associate input data with, load template(s) first."
            )
        self.clear_input(template_name=template_name)
        self.add_input(
            data=data, input_name=input_name, groups=groups, template_name=template_name
        )

    def clear_input(self, template_name="_all_"):
        """Method to delete all input data for all or some templates, can be used prior to adding new
        set of data to parse with same templates, instead of re-initializing ttp object.

        **Parameters**

        * ``template_name`` (str) name of the template to clear input for, clears for all templates
          by default
        """
        self.__data_size = 0
        self.__datums_count = 0
        for template in self._templates:
            if template.name == template_name or template_name == "_all_":
                template.inputs = {}

    def _calculate_overall_data_size(self):
        """Method to calculate overall data size and count"""
        self.__data_size = 0
        self.__datums_count = 0
        for template in self._templates:
            # get overall data size and count
            for input_name, input_obj in template.inputs.items():
                self.__datums_count += len(input_obj.data)
                # get data size
                for i in input_obj.data:
                    if i[0] == "file_name":
                        self.__data_size += os.path.getsize(i[1])
                    elif i[0] == "text_data":
                        self.__data_size += getsizeof(i[1])

    def add_template(self, template, template_name="_root_template_", filters=None):
        """Method to load TTP templates into the parser.

        **Parameters**

        * ``template`` file object or OS path to text file with template
        * ``template_name`` (str) name of the template
        * ``filters`` (list) list of templates' names to load,

        ``filters`` attribute allow to filter the list of template names that
        should be loaded. Checks done against child templates as well. For
        templates specified in filter list, groups/macro/inputs/etc. will not
        be loaded and no results produced.
        """
        filters = filters or []
        log.debug("ttp.add_template - loading template '{}'".format(template_name))
        # get a list of [(type, text,)] tuples or empty list []
        items = self._ttp_["utils"]["load_files"](path=template, read=True)
        for i in items:
            template_obj = _template_class(
                template_text=i[1],
                base_path=self.base_path,
                ttp_vars=self.vars,
                name=template_name,
                filters=filters,
                ttp_macro=self._ttp_.get("_custom_functions_", {}).get("macro", {}),
                _ttp_=self._ttp_,
            )
            # if not template_obj.templates - no 'template' tags in template
            self._templates += (
                template_obj.templates if template_obj.templates else [template_obj]
            )

    def add_lookup(self, name, text_data="", include=None, load="python", key=None):
        """Method to add lookup table data to all templates loaded so far. Lookup is a
        text representation of structure that can be loaded into python dictionary using one
        of the available loaders - python, csv, ini, yaml, json.

        **Parameters**

        * ``name`` (str) name to assign this lookup table for referencing
        * ``text_data`` (str) text to load lookup table/dictionary from
        * ``include`` (str) absolute or relative /os/path/to/lookup/table/file.txt
        * ``load`` (str) name of TTP loader to use to load table data
        * ``key`` (str) specify key column for csv loader to construct dictionary

        ``include`` can accept relative OS path - relative to the directory where TTP will be
        invoked either using CLI tool or as a module
        """
        lookup_data = self._ttp_["utils"]["load_struct"](
            text_data=text_data, include=include, load=load, key=key
        )
        self.lookups.update({name: lookup_data})
        [template.add_lookup({name: lookup_data}) for template in self._templates]

    def add_vars(self, vars):
        """Method to add variables to ttp and its templates to reference during parsing

        **Parameters**

        * ``vars`` dictionary of variables to make available to ttp parser
        """
        if isinstance(vars, dict):
            self.vars.update(vars)
            [template.add_vars(vars) for template in self._templates]

    def parse(self, one=False, multi=False):
        """Method to parse data with templates.

        **Parameters**

        * ``one`` (boolean) if set to True will run parsing in single process
        * ``multi`` (boolean) if set to True will run parsing in multiprocess

        By default one and multi set to False and  TTP will run parsing following below rules:

            1. if one or multi set to True run in one or multi process
            2. if overall data size is less then 5Mbyte, use single process
            3. if overall data size is more then 5Mbytes, use multiprocess

        In addition to 3 TTP will check if number of input data items more then 1, if so
        multiple processes will be used and one process otherwise.
        """
        # add self.__data to templates and get file count and size:
        self._calculate_overall_data_size()
        log.info(
            "ttp.parse: loaded datums - {}, overall size - {} bytes".format(
                self.__datums_count, self.__data_size
            )
        )
        if one is True and multi is True:
            log.critical("ttp.parse - choose one or multiprocess parsing")
            raise SystemExit()
        elif one is True:
            self.__parse_in_one_process()
        elif multi is True:
            self.__parse_in_multiprocess()
        elif self.__data_size > self.multiproc_threshold and self.__datums_count >= 2:
            self.__parse_in_multiprocess()
        else:
            self.__parse_in_one_process()
        # run outputters defined in templates:
        [template.run_outputs() for template in self._templates]

    def __parse_in_multiprocess(self):
        """Method to parse data in bulk by parsing each data item
        against each template and saving results in results list.
        """
        log.info("ttp.parse: parse using multiple processes")
        num_processes = cpu_count()

        for template in self._templates:
            num_jobs = 0
            tasks = JoinableQueue()
            results_queue = Queue()

            workers = [
                _worker(
                    tasks,
                    results_queue,
                    lookups=template.lookups,
                    vars=template.vars,
                    groups=template.groups,
                    macro_text=template.macro_text,
                    custom_functions=self._ttp_.get("_custom_functions_", {}),
                    dynamic_path_key_to_int=self._ttp_["dynamic_path_key_to_int"],
                )
                for i in range(num_processes)
            ]
            [w.start() for w in workers]

            for input_name, input_obj in template.inputs.items():
                for datum in input_obj.data:
                    task_dict = {
                        "data": datum,
                        "groups_indexes": input_obj.groups_indexes,
                        "input_functions": input_obj.functions,
                    }
                    tasks.put(task_dict)
                    num_jobs += 1
            [tasks.put(None) for i in range(num_processes)]

            # wait for all tasks to complete
            tasks.join()

            for i in range(num_jobs):
                result = results_queue.get()
                template.form_results(result)

    def __parse_in_one_process(self):
        """Method to parse data in single process, each data item parsed
        against each template and results saved in results list
        """
        log.info("ttp.parse: parse using single process")
        for template in self._templates:
            self._ttp_["macro"] = template.macro
            self._ttp_["template_obj"] = template
            parserObj = _parser_class(
                lookups=template.lookups,
                vars=template.vars,
                groups=template.groups,
                _ttp_=self._ttp_,
            )
            if template.results_method.lower() == "per_input":
                for input_name, input_obj in template.inputs.items():
                    for datum in input_obj.data:
                        parserObj.set_data(
                            datum, main_results={}, input_functions=input_obj.functions
                        )
                        parserObj.parse(groups_indexes=input_obj.groups_indexes)
                        result = parserObj.main_results
                        template.form_results(result)
            elif template.results_method.lower() == "per_template":
                results_data = {}
                for input_name, input_obj in template.inputs.items():
                    for datum in input_obj.data:
                        parserObj.set_data(
                            datum,
                            main_results=results_data,
                            input_functions=input_obj.functions,
                        )
                        parserObj.parse(groups_indexes=input_obj.groups_indexes)
                        results_data = parserObj.main_results
                template.form_results(results_data)

    def result(self, templates=None, structure="list", **kwargs):
        """Method to get parsing results, supports basic filtering based on
        templates' names, results can be formatted and returned to specified
        returner.

        **Parameters**

        * ``templates`` (list or str) names of the templates to return results for
        * ``structure`` (str) structure type, valid values - ``list``, ``dictionary`` or ``flat_list``

        **kwargs** - can contain any attributes supported by output tags, for instance:

        * ``format`` (str) output formatter name - yaml, json, raw, pprint, csv, table, tabulate
        * ``functions`` (str) reference output functions to run results through

        **Example**::

            from ttp import ttp
            parser = ttp(data="/os/path/to/data/dir/", template="/os/path/to/template.txt")
            parser.parse()
            json_result = parser.result(format="json")[0]
            yaml_result = parser.result(format="yaml")[0]
            print(json_result)
            print(yaml_result)

        **Returns**

        By default template results set to *per_input* and structure set to *list*, returns list such as::

            [
               [ template_1_input_1_results,
                 template_1_input_2_results,
                 ...
                 template_1_input_N_results ],
               [ template_2_input_1_results,
                 template_2_input_2_results,
                 ...
            ]

        If template results set to *per_template* and structure set to *list*, returns list such as::

            [
               [ template_1_input_1_2...N_joined_results ],
               [ template_2_input_1_2...N_joined_results ]
            ]

        If template results set to *per_input* and structure set to *dictionary*, returns dictionary such as::

            {
               template_1_name: [
                 input_1_results,
                 input_2_results,
                 ...
                 input_N_results
                ],
               template_2_name: [
                 input_1_results,
                 input_2_results
                ],
                 ...
            }

        If template results set to *per_template* and structure set to *dictionary*,
        returns dictionary such as::

            {
               template_1_name: input_1_2...N_joined_results,
               template_2_name: input_1_2...N_joined_results
            }

        If structure set to *flat_list*, results will be combined across
        all templates in a list of dictionaries. For instance, with structure
        set to *list* result might look like this::

            [[[{'interface': 'Lo0', 'ip': '192.168.0.1', 'mask': '32'},
               {'interface': 'Lo1', 'ip': '1.1.1.1', 'mask': '32'}],
              [{'interface': 'Lo2', 'ip': '2.2.2.2', 'mask': '32'},
               {'interface': 'Lo3', 'ip': '3.3.3.3', 'mask': '32'}]]]

        But with structure set to *flat_list* it will be flattened to this::

            [{'interface': 'Lo0', 'ip': '192.168.0.1', 'mask': '32'},
             {'interface': 'Lo1', 'ip': '1.1.1.1', 'mask': '32'},
             {'interface': 'Lo2', 'ip': '2.2.2.2', 'mask': '32'},
             {'interface': 'Lo3', 'ip': '3.3.3.3', 'mask': '32'}]
        """
        templates = templates or []
        # filter templates to run outputs for:
        templates = [templates] if isinstance(templates, str) else templates
        templates_obj = self._templates
        if templates:
            templates_obj = [
                template for template in self._templates if template.name in templates
            ]
        # check if kwargs provided, create outputter if so
        if kwargs:
            kwargs.setdefault("returner", "self")
            outputter = _outputter_class(_ttp_=self._ttp_, **kwargs)
        # form results structure
        if structure.lower() == "list":
            if kwargs:
                return [
                    outputter.run(template.results, macro=template.macro)
                    for template in templates_obj
                ]
            return [template.results for template in templates_obj]
        elif structure.lower() == "dictionary":
            if kwargs:
                return {
                    template.name: outputter.run(template.results, macro=template.macro)
                    for template in templates_obj
                    if template.name
                }
            return {
                template.name: template.results
                for template in templates_obj
                if template.name
            }
        elif structure.lower() == "flat_list":
            ret = []
            for template in templates_obj:
                rslt = (
                    outputter.run(template.results, macro=template.macro)
                    if kwargs
                    else template.results
                )
                if isinstance(rslt, list):
                    for item in rslt:
                        if isinstance(item, list):
                            ret += item
                        else:
                            ret.append(item)
                else:
                    ret.append(rslt)
            return ret

    def get_input_load(self):
        """Method to retrieve input tag text load. Using input ``load`` attribute,
        text data can be loaded into python structure using one of the supported
        loaders, for instance if text data structured using YAML, YAML
        loader can be used to produce python native structure, that structure will
        be returned by this method.

        Primary use case is to specify parameters within TTP input that can be
        used by other applications/scrips.

        **Returns**

        Dictionary of {"template_name": {"input_name": "input load data"}} across all templates,
        where input_name set to input name attribute value, by default it is "Default_Input",
        and template_name set to name of the template, by default it is "_root_template_"

        .. warning:: inputs load can override one another if combination of template_name
          and input_name is not unique.
        """
        ret = {}
        for template_obj in self._templates:
            ret[template_obj.name] = {}
            for input_name, input_obj in template_obj.inputs.items():
                ret[template_obj.name][input_name] = input_obj.parameters
        return ret

    def clear_result(self, templates=None):
        """Method to clear parsing results for templates.

        **Parameters**

        * ``templates`` (list or str) - name of template(s) to clear results for,
          if not provided will clear results for all templates.
        """
        templates = templates or []
        # filter templates objects to clear results for
        templates = [templates] if isinstance(templates, str) else templates
        # clear results
        if templates:
            [
                t_obj.results.clear()
                for t_obj in self._templates
                if t_obj.name in templates
            ]
        else:
            [t_obj.results.clear() for t_obj in self._templates]

    def add_function(self, fun, scope, name=None, add_ttp=False):
        """Method to add custom function in ``_ttp_`` dictionary.
        Function can be referenced in template depending on scope.

        **Parameters**

        * ``fun`` - function reference
        * ``scope`` - scope to add function to
        * ``name`` - optional, name to use within templates, by default equal to function ``__name__``
        * ``add_ttp`` - boolean, on True will add ``_ttp_`` dictionary in function's global scope

        **scope options**

        * ``match`` - used for match variables
        * ``group`` - used for groups
        * ``input`` - used for inputs
        * ``output`` - used for outputs
        * ``returners`` - used for output returners
        * ``formatters`` - used for output returners
        * ``variable`` - used as template variable getter
        * ``macro`` - used as macro function

        .. warning:: add_function should be called before template loaded in parser

        Custom functions should use first argument to hold data to process, additional
        args and kwargs will be supplied to function if provided in template.

        TTP passes output tag attributes to ``returner`` and ``formatter`` functions,
        attributes need to be unpacked using, for instance, ``**kwargs``.

        For ``template variable`` getters functions first argument supplied is an
        input text data, second argument is datum name, equal to filename if loaded
        from file

        Function return content differ depending on scope:

        * ``match`` - must return tuple of two items
        * ``group`` - must return tuple of two items
        * ``input`` - must return tuple of two items
        * ``output`` - must return single element containing processing results
        * ``returners`` - not returns expected
        * ``formatters`` - must return single element containing processing results
        * ``variable`` - must return single element to assign to variable
        * ``macro`` - can return processing results, True or False

        For ``match``, ``group`` and ``input`` functions TTP expects in return tuple
        of two elements where first element should contain processing results, second
        element can be True, False, None or dictionary. Second item can influence
        processing logic following these rules:

        * if second item is False - results invalidated and discarded
        * if second item is True or None - first item replaces originally supplied data, processing continues
        * if second item is dictionary - supported by ``match`` scope only, dictionary merged with results

        Example::

            def group_cust_fun(data, *args, **kwargs):
                if kwargs.get("upper") == True:
                    data["description"] = data["description"].upper()
                return data, None

            template = '''
            <input load="text">
            interface Lo1
             description this interface has description
             ip address 1.1.1.1 32
            </input>

            <group myFun="upper=True">
            interface {{ interface }}
             description {{ description | ORPHRASE }}
             ip address {{ ip }} {{ mask }}
            </group>
            '''

            parser = ttp()
            parser.add_function(group_cust_fun, scope="group", name="myFun")
            parser.add_template(template)
            parser.parse()
        """
        name = name if name else fun.__name__
        if add_ttp:
            fun.__globals__["_ttp_"] = self._ttp_
        self._ttp_[scope][name] = fun
        # save custom function separately to pass on to multiprocessing
        # for updating _ttp_ dictionary on reinitialization
        self._ttp_.setdefault("_custom_functions_", {}).setdefault(scope, {})[
            name
        ] = fun

    def get_template(self):
        """Method to return a string of fully constructed TTP templates. This is
        mainly to assist with troubleshooting ``extend`` tags processing.
        """
        return "\n".join(t.template for t in self._templates)


"""
==============================================================================
TTP PARSER MULTIPROCESSING WORKER
==============================================================================
"""


class _worker(Process):
    """Class used in multiprocessing to parse data"""

    def __init__(
        self,
        task_queue,
        results_queue,
        lookups,
        vars,
        groups,
        macro_text,
        custom_functions,
        dynamic_path_key_to_int,
    ):
        Process.__init__(self)
        self._ttp_ = lazy_import_functions()
        self._ttp_.update(custom_functions)
        self._ttp_["dynamic_path_key_to_int"] = dynamic_path_key_to_int
        self.task_queue = task_queue
        self.results_queue = results_queue
        self.macro_text = macro_text
        self.parserObj = _parser_class(lookups, vars, groups, _ttp_=self._ttp_)

    def load_functions(self):
        # load macro from text
        funcs = {}
        # extract macro with all the __builtins__ provided
        for macro_text in self.macro_text:
            try:
                funcs = self._ttp_["utils"]["load_python_exec"](
                    macro_text, builtins=__builtins__
                )
                self._ttp_["macro"].update(funcs)
            except SyntaxError as e:
                log.error(
                    "multiprocess_worker.load_functions: syntax error, failed to load macro: \n{},\nError: {}".format(
                        macro_text, e
                    )
                )

    def run(self):
        self.load_functions()
        # run tasks
        while True:
            next_task = self.task_queue.get()
            # check for dead pill to stop process
            if next_task is None:
                self.task_queue.task_done()
                break
            # set parser object parameters
            self.parserObj.set_data(
                next_task["data"],
                main_results={},
                input_functions=next_task["input_functions"],
            )
            # parse and get results
            self.parserObj.parse(groups_indexes=next_task["groups_indexes"])
            result = self.parserObj.main_results
            # put results in the queue and finish task
            self.task_queue.task_done()
            self.results_queue.put(result)
        return


"""
==============================================================================
TTP TEMPLATE CLASS
==============================================================================
"""


class _template_class:
    """Template class to hold template data"""

    def __init__(
        self,
        template_text,
        _ttp_,
        base_path="",
        ttp_vars=None,
        name="_root_template_",
        filters=None,
        ttp_macro=None,
    ):
        self._ttp_ = _ttp_
        ttp_vars = ttp_vars or {}
        filters = filters or []
        ttp_macro = ttp_macro or {}
        self.PATHCHAR = "."  # character to separate path items, like ntp.clock.time, '.' is pathChar here
        self.vars = {  # dictionary to store template variables
            "_vars_to_results_": {},  # to indicate variables and patch where they should be saved in results
            # _vars_to_results_ is a dict of {pathN:[var_key1, var_keyN]} data
            "_var_functions_": {},  # dictionary to keep variables with functions such as getters
        }
        self.ttp_vars = ttp_vars  # need to save it to pass to child templates
        self.vars.update(ttp_vars)
        self.outputs = []  # list that contains global outputs
        self.groups_outputs = []  # list that contains groups specific outputs
        self.groups = []
        self.inputs = OrderedDict()
        self.lookups = {}
        self.templates = []
        self.base_path = base_path
        self.results = []
        self.name = name
        self.macro = ttp_macro  # dictionary of macro name to function mapping
        self.results_method = "per_input"  # how to join results
        self.macro_text = (
            set()
        )  # set to contain macro functions text to transfer into other processes
        self.filters = filters  # list that contains names of child templates to extract
        self.__doc__ = ""  # string to contain template doc/description
        self.template = template_text  # attribute to store template text

        # dictionary to store template's top tags ET elements
        self.tags = {
            "vars": [],
            "groups": [],
            "inputs": [],
            "outputs": [],
            "lookups": [],
            "macro": [],
            "template": [],
            "extend": [],
        }

        # pre-process template to handle extend tags
        self.template = self.handle_extend(template_text)

        # load template from string:
        self.load_template_xml(self.template)

        # update inputs with the groups it has to be run against:
        self.update_inputs_with_groups()
        # update groups with output references:
        self.update_groups_with_outputs()
        # separate vars with functions from vars
        self.get_var_functions()

        if log.isEnabledFor(logging.DEBUG):
            self.debug()
            [template_obj.debug for template_obj in self.templates]
            [input.debug() for input in self.inputs.values()]
            [group.debug() for group in self.groups]
            [output_obj.debug() for output_obj in self.outputs]

    def debug(self):
        from pprint import pformat

        attributes = dict(vars(self))
        _ = attributes.pop("_ttp_")
        text = "Template Object {}, Template name '{}' content:\n{}".format(
            self, self.name, pformat(attributes, indent=4)
        )
        log.debug(text)

    def add_lookup(self, data):
        """Method to load lookup data"""
        self.lookups.update(data)
        [template.add_lookup(data) for template in self.templates]

    def add_vars(self, data):
        """Method to update vars with given data"""
        if isinstance(data, dict):
            self.vars.update(data)
            [template.add_vars(data) for template in self.templates]

    def run_outputs(self):
        """Method to run template outputs with template results"""
        for output in self.outputs:
            self.results = output.run(self.results, macro=self.macro)

    def form_results(self, result):
        """Method to add results to self.results"""
        datum = []
        # result is always a dictionary, but if have _anonymous_
        # group, need to merge it with the rest of results, at the
        # same time _anonymous_ group result is always a list
        if "_anonymous_" in result:
            datum = result.pop("_anonymous_")
            if result:
                if isinstance(result, list):
                    datum += result
                else:
                    datum.append(result)
        else:
            datum = result
        # for per_template mode, results already combined
        if self.results_method == "per_template":
            self.results = datum
        # append this input results to overall results
        elif self.results_method == "per_input":
            self.results.append(datum)

    def get_var_functions(self):
        """optimization method to move variable functions
        in separate dictionary
        """
        # form _var_functions_ dictionary
        for var_name, var_value in self.vars.items():
            if not isinstance(var_value, str):
                continue
            if var_value in self._ttp_["variable"]:
                self.vars["_var_functions_"][var_name] = var_value
        # remove _var_functions_ from self.vars
        [self.vars.pop(var_name) for var_name in self.vars["_var_functions_"].keys()]

    def update_input(
        self, element=None, data=None, input_name="Default_Input", groups=None
    ):
        """
        Method to set data for template input
        Args:
            data (list): list of (data_name, data_path,) tuples
            input_name (str): name of the input
            groups (list): list of groups to use for that input
        """
        groups = groups or ["all"]
        input_obj = _input_class(
            element=element,
            input_name=input_name,
            template_obj=self,
            groups=groups,
            data=data,
            _ttp_=self._ttp_,
        )
        if input_obj.name in self.inputs:
            self.inputs[input_obj.name].load_data(data=input_obj.data)
            self.inputs[input_obj.name].groups_indexes += input_obj.groups_indexes
            self.inputs[input_obj.name].groups_indexes = list(
                set(self.inputs[input_obj.name].groups_indexes)
            )
            del input_obj
        else:
            self.inputs[input_obj.name] = input_obj

    def update_inputs_with_groups(self):
        """
        Method to update self.inputs group_inputs with group indexes
        """
        for G in self.groups:
            for input_name in G.inputs:
                # add new input
                if input_name not in self.inputs:
                    url = self.base_path + input_name
                    data_items = self._ttp_["utils"]["load_files"](path=url, read=False)
                    # skip 'text_data' from data as if by the time this method runs
                    # no input with such name found it means that group input is os path
                    # string and text_data will be returned by self.utils.load_files
                    # only if no such path exists, hence text_data does not make sense here
                    data = [i for i in data_items if "text_data" not in i[0]]
                    self.update_input(data=data, input_name=input_name)

    def update_groups_with_outputs(self):
        """Method to replace output names in group with
        output index from self.groups_outputs, also move
        output from self.outputs to group specific
        self.groups_outputs
        """
        for G in self.groups:
            for output_index, grp_output in enumerate(G.outputs):
                group_output_found = False
                # search through global outputs:
                for glob_index, glob_output in enumerate(self.outputs):
                    if glob_output.name == grp_output:
                        self.groups_outputs.append(self.outputs.pop(glob_index))
                        G.outputs[output_index] = self.groups_outputs[-1]
                        group_output_found = True
                # go to next output if this output found:
                if group_output_found:
                    continue
                # try to find output in group specific outputs:
                for index, output in enumerate(self.groups_outputs):
                    if output.name == grp_output:
                        G.outputs[output_index] = output
                        group_output_found = True
                # print error message if no output found:
                if not group_output_found:
                    G.outputs.pop(output_index)
                    log.error(
                        "template.update_groups_with_outputs: group '{}' - output '{}' not found.".format(
                            G.name, grp_output
                        )
                    )

    def get_template_attributes(self, element):
        def extract_name(O):
            self.name = O

        def extract_base_path(O):
            self.base_path = O

        def extract_results_method(O):
            self.results_method = O

        def extract_pathchar(O):
            self.PATHCHAR = str(O)

        opt_funcs = {
            "name": extract_name,
            "base_path": extract_base_path,
            "results": extract_results_method,
            "pathchar": extract_pathchar,
        }

        for name, options in element.attrib.items():
            if name in opt_funcs:
                opt_funcs[name](options)

    def collect_tags(self, element):
        """
        Function to iterate over element tags and fill in self.tags
        dictionary.

        :param element: (obj) ET.XML object
        """
        # functions to append tag elements to tags dictionary:
        tags_funcs = {  # C - template child ET elements
            "v": lambda C: self.tags["vars"].append(C),
            "vars": lambda C: self.tags["vars"].append(C),
            "variables": lambda C: self.tags["vars"].append(C),
            "g": lambda C: self.tags["groups"].append(C),
            "grp": lambda C: self.tags["groups"].append(C),
            "group": lambda C: self.tags["groups"].append(C),
            "o": lambda C: self.tags["outputs"].append(C),
            "out": lambda C: self.tags["outputs"].append(C),
            "output": lambda C: self.tags["outputs"].append(C),
            "i": lambda C: self.tags["inputs"].append(C),
            "in": lambda C: self.tags["inputs"].append(C),
            "input": lambda C: self.tags["inputs"].append(C),
            "lookup": lambda C: self.tags["lookups"].append(C),
            "template": lambda C: self.tags["template"].append(C),
            "macro": self.parse_macro,
            "doc": self.parse_doc,
        }
        # fill in self.tags dictionary:
        for child in list(element):
            tags_funcs.get(child.tag.lower(), self.invalid)(child)

    def invalid(self, C):
        log.warning("template.parse: invalid tag '{}'".format(C.tag))

    def parse_macro(self, element):
        funcs = {}
        # extract macro with all the __builtins__ provided
        try:
            funcs = self._ttp_["utils"]["load_python_exec"](
                element.text, builtins=__builtins__
            )
            self.macro.update(funcs)
            # save macro text to be able to restore macro functions within another process
            self.macro_text.add(element.text)
        except SyntaxError as e:
            log.error(
                "template.parse_macro: syntax error, failed to load macro: \n{},\nError: {}".format(
                    element.text, e
                )
            )

    def parse_doc(self, element):
        self.__doc__ += element.text + "\n"

    def parse_template(self, element, template_index):
        # skip child templates that are not in requested children list
        if self.filters:
            if not element.attrib.get("name", None) in self.filters:
                return
        self.templates.append(
            _template_class(
                template_text=ET.tostring(element, encoding="UTF-8"),
                base_path=self.base_path,
                ttp_vars=self.ttp_vars,
                name=str(template_index),
                _ttp_=self._ttp_,
            )
        )

    def parse_vars(self, element):
        # method to parse vars data
        vars = self._ttp_["utils"]["load_struct"](element.text, **element.attrib)
        if vars:
            self.vars.update(vars)
        # check if var has name attribute:
        if "name" in element.attrib:
            path = element.attrib["name"]
            for key in vars.keys():
                self.vars["_vars_to_results_"].setdefault(path, []).append(key)

    def parse_lookup(self, element):
        if "name" not in element.attrib:
            log.warning("Lookup 'name' attribute not provided, skipping")
            return
        lookup_data = self._ttp_["utils"]["load_struct"](element.text, **element.attrib)
        if lookup_data is None:
            return
        if element.attrib.get("database", "").lower() == "geoip2":
            lookup_data = self._ttp_["lookup"]["geoip2_db_loader"](lookup_data)
        self.lookups[element.attrib["name"]] = lookup_data

    def parse_group(self, element, grp_index):
        self.groups.append(
            _group_class(
                element,
                top=True,
                pathchar=self.PATHCHAR,
                vars=self.vars,
                grp_index=grp_index,
                _ttp_=self._ttp_,
            )
        )

    def parse_hierarch_tmplt(self, element):
        # collect and sort all the top level tags
        self.collect_tags(element)

        # perform tags parsing/extraction
        for t_index, t in enumerate(self.tags["template"]):
            self.parse_template(t, t_index)
        for v in self.tags["vars"]:
            self.parse_vars(v)
        for o in self.tags["outputs"]:
            self.outputs.append(
                _outputter_class(o, _ttp_=self._ttp_, template_obj=self)
            )
        for L in self.tags["lookups"]:
            self.parse_lookup(L)
        for grp_index, g in enumerate(self.tags["groups"]):
            self.parse_group(g, grp_index)
        # need to parse inputs after groups to form group inputs correctly
        for i in self.tags["inputs"]:
            self.update_input(element=i)

    def filter_extend(self, extend_template, extend_tag, top):
        """
        Method to filter tags of extended template using name attribute

        :param extend_ET: (obj) ET.XML object of extended template
        :param child: (obj) ET.XML object of extend data
        :param top: (bool) indicator if extend tag is at the top or nested
        :return: list of EX.XML objects that passed filtering
        """
        # check if no filters given at all - return straight away
        if top and len(extend_tag.attrib) == 1:
            return extend_template
        ret = []
        grp_index = 0
        groups = [
            i.strip() for i in extend_tag.get("groups", "").split(",") if i.strip()
        ]
        # do filtering for top tag
        if top:
            inputs = [
                i.strip() for i in extend_tag.get("inputs", "").split(",") if i.strip()
            ]
            tvars = [
                i.strip() for i in extend_tag.get("vars", "").split(",") if i.strip()
            ]
            lookups = [
                i.strip() for i in extend_tag.get("lookups", "").split(",") if i.strip()
            ]
            outputs = [
                i.strip() for i in extend_tag.get("outputs", "").split(",") if i.strip()
            ]
            for t in extend_template:
                tag_name = t.attrib.get("name")
                if inputs and t.tag in ["i", "in", "input"]:
                    if tag_name in inputs:
                        ret.append(t)
                elif tvars and t.tag in ["v", "vars", "variables"]:
                    if tag_name in tvars:
                        ret.append(t)
                elif groups and t.tag in ["g", "grp", "group"]:
                    if tag_name in groups or str(grp_index) in groups:
                        ret.append(t)
                    grp_index += 1
                elif lookups and t.tag == "lookup":
                    if tag_name in lookups:
                        ret.append(t)
                elif outputs and t.tag in ["o", "out", "output"]:
                    if tag_name in outputs:
                        ret.append(t)
                else:
                    ret.append(t)
        # do filtering for nested tag allowing <group> and <extend> tags only
        else:
            for t in extend_template:
                tag_name = t.attrib.get("name")
                if t.tag in ["g", "grp", "group"]:
                    if groups:
                        if tag_name in groups or str(grp_index) in groups:
                            ret.append(t)
                        grp_index += 1
                    else:
                        ret.append(t)
                elif t.tag == "extend":
                    ret.append(t)
        return ret

    def handle_extend(self, template_text=None, template_ET=None, top=True):
        """
        Function to handle all extend tags including nested within groups.

        :param template_text: (str) template string
        :return: (str) final template string after extending it
        """
        # load template string to XML etree object
        if template_text:
            template_ET = self.construct_etree(template_text)
        # load macro functions from top template into self.macro dict
        if top == True:
            for child in template_ET:
                if child.tag == "macro":
                    self.parse_macro(child)
        # recursively iterate over etree handling extend tags
        for index, child in enumerate(template_ET):
            if child.tag == "extend":
                path_to_template = child.attrib.get("template", "")
                content = self._ttp_["utils"]["load_files"](path_to_template, read=True)
                if content[0][1] == path_to_template:
                    raise FileNotFoundError(
                        "template.extend: failed load extend tag content at path: {}".format(
                            path_to_template
                        )
                    )
                # run extend tag macro function if any
                template_content = content[0][1]
                if child.attrib.get("macro") in self.macro:
                    template_content = self.macro[child.attrib["macro"]](content[0][1])
                # construct etree out of template content
                extend_ET = self.construct_etree(template_content)
                # if extended template has _anonymous_ group as the only child, use only its text
                if (
                    len(extend_ET) == 1
                    and extend_ET[0].attrib.get("name") == "_anonymous_"
                ):
                    template_ET.text += extend_ET[0].text
                    template_ET.remove(child)
                # process extended template children to extend parent element
                else:
                    # run filtering for extended template tags
                    filtered_ET = self.filter_extend(
                        extend_template=extend_ET, extend_tag=child, top=top
                    )
                    # run recursion for newly extended groups to handle nested extend tags
                    self.handle_extend(template_ET=filtered_ET, top=False)
                    # save extended elements as parent children
                    template_ET[index : index + 1] = filtered_ET
            # run recursion for child groups looking for extend tags
            elif child.tag == "group":
                self.handle_extend(template_ET=child, top=False)

        if top:
            return ET.tostring(template_ET).decode()

    def construct_etree(self, template_text):
        """
        Method to construct XML etree out of template text reconstructing
        it if required

        :param template_text: (str) TTp Template string
        :return: ET.XML object with top tag set to <template>
        """
        try:
            template_ET = ET.XML(template_text)
            # check if top tag is not template:
            if template_ET.tag.lower() != "template":
                template_ET = ET.XML(
                    "<template>\n{}\n</template>".format(template_text)
                )
        except ET.ParseError as e:
            template_ET = ET.XML("<template>\n{}\n</template>".format(template_text))
        # check if template has children, if not, make it an _anonymous_  group
        if not list(template_ET):
            template_ET = ET.XML(
                '<template><group name="_anonymous_">\n{}\n</group></template>'.format(
                    template_text
                )
            )
        return template_ET

    def load_template_xml(self, template_text):
        """
        Main function to load template from text reconstructing it if required

        :param template_text: (str) TTP Template string
        """
        # load template and its attributes
        template_ET = self.construct_etree(template_text)
        self.get_template_attributes(template_ET)

        # filter - do not load template groups if template name not in filter
        if self.filters and self.name not in self.filters:
            return

        self.parse_hierarch_tmplt(template_ET)


"""
==============================================================================
TTP INPUT CLASS
==============================================================================
"""


class _input_class:
    """Template input class to hold inputs data"""

    def __init__(
        self,
        _ttp_,
        element=None,
        template_obj=None,
        data=None,
        input_name="Default_Input",
        groups="all",
    ):
        self._ttp_ = _ttp_
        self.attributes = {
            "load": "python",
            "extensions": [],
            "filters": [],
            "urls": [],
        }
        self.template_obj = template_obj
        self.parameters = {}
        self.data = []
        self.groups_indexes = []
        self.group_inputs = []
        self.input_groups = groups
        self.functions = []
        # extract attributes from input element
        if element is not None:
            # need to get name before getting any other attributes
            # as name used to extract groups and depending on python dict
            # hashing, groups can be attempted to extract before name attribute
            self.name = element.attrib.get("name", input_name).strip()
            # set default attribute values
            element.attrib.setdefault("groups", groups)
            element.attrib.setdefault("load", "python")
            # extract attributes
            self.get_attributes(data=element.attrib, element_text=element.text)
            self.load_data(element_text=element.text)
        # if no input element given, use input_name and groups with data
        # as well as default python loader
        else:
            self.name = input_name
            self.get_attributes(data={"groups": groups, "load": "python"})
            self.load_data(data=data)

    def get_attributes(self, data, element_text=""):
        def extract_name(O):
            self.name = O.strip()

        def extract_load(O):
            self.attributes["load"] = O.strip()
            if self.attributes["load"] != "text":
                attribs = self._ttp_["utils"]["load_struct"](element_text, **data)
                if attribs:
                    self.parameters = attribs
                    self.get_attributes(data=attribs)

        def extract_groups(O):
            if isinstance(O, list):
                groups_list = O
            else:
                groups_list = [i.strip() for i in O.split(",")]
            # create a list of groups with no input attribute matched by this input groups attribute
            if "all" in groups_list:
                self.input_groups = [
                    grp_obj.grp_index
                    for grp_obj in self.template_obj.groups
                    if not grp_obj.inputs
                ]
            else:
                self.input_groups = [
                    grp_obj.grp_index
                    for grp_obj in self.template_obj.groups
                    if (grp_obj.name in groups_list and not grp_obj.inputs)
                ]
            # iterate over all groups to get a list of groups that match this input in input attribute
            self.group_inputs = [
                grp_obj.grp_index
                for grp_obj in self.template_obj.groups
                if self.name in grp_obj.inputs
            ]
            # form input groups_indexes - group_inputs more preferred
            if self.group_inputs:
                self.groups_indexes = sorted(list(set(self.group_inputs)))
            else:
                self.groups_indexes = sorted(list(set(self.input_groups)))

        def extract_extensions(O):
            if isinstance(O, str):
                self.attributes["extensions"] = [O]
            else:
                self.attributes["extensions"] = O

        def extract_filters(O):
            if isinstance(O, str):
                self.attributes["filters"] = [O]
            else:
                self.attributes["filters"] = O

        def extract_urls(O):
            if isinstance(O, str):
                self.attributes["urls"] = [O]
            else:
                self.attributes["urls"] = O

        def extract_functions(O):
            funcs = self._ttp_["utils"]["get_attributes"](O)
            for i in funcs:
                func_name = i["name"]
                if func_name in functions:
                    functions[func_name](i)
                elif func_name in self._ttp_["input"]:
                    self.functions.append(i)
                else:
                    similar_funcs = self._ttp_["utils"]["guess"](
                        func_name, list(self._ttp_["input"].keys())
                    )
                    if similar_funcs:
                        log.error(
                            "input.get_attributes: unknown input function: '{}', most similar function(s) - {}".format(
                                func_name, ", ".join(similar_funcs)
                            )
                        )
                    else:
                        log.error(
                            'input.get_attributes: unknown input function: "{}"'.format(
                                func_name
                            )
                        )

        def extract_function(func_name, args_kwargs):
            attribs = self._ttp_["utils"]["get_attributes"](
                "{}({})".format(func_name, args_kwargs)
            )
            self.functions.append(attribs[0])

        def extract_commands(O):
            if isinstance(O, str):
                self.functions.append(
                    {
                        "name": "extract_commands",
                        "args": [i.strip() for i in O.split(",") if i.strip()],
                        "kwargs": {},
                    }
                )
            elif isinstance(O, dict):
                self.functions.append(O)

        # group attributes extract functions dictionary:
        options = {
            "name": extract_name,
            "load": extract_load,
            "groups": extract_groups,
            "extensions": extract_extensions,
            "filters": extract_filters,
            "url": extract_urls,
        }
        functions = {
            "functions": extract_functions,
            "extract_commands": extract_commands,
        }
        # extract attributes from element tag attributes
        for attr_name, attributes in data.items():
            if attr_name.lower() in options:
                options[attr_name.lower()](attributes)
            elif attr_name.lower() in functions:
                functions[attr_name.lower()](attributes)
            elif attr_name in self._ttp_["input"]:
                extract_function(attr_name, attributes)
            else:
                self.attributes[attr_name] = attributes

    def load_data(self, element_text=None, data=None):
        if self.attributes["load"] == "text" and element_text:
            self.data = [("text_data", element_text)]
            return
        elif data:
            for d_item in data:
                if not d_item in self.data:
                    self.data.append(d_item)
            return
        # load data:
        for url in self.attributes["urls"]:
            url = self.template_obj.base_path + url
            datums = self._ttp_["utils"]["load_files"](
                path=url,
                extensions=self.attributes["extensions"],
                filters=self.attributes["filters"],
                read=False,
            )
            self.data += datums

    def debug(self):
        from pprint import pformat

        text = "Template object {}, Template name '{}', Input name '{}' content:\n{}".format(
            self.template_obj,
            self.template_obj.name,
            self.name,
            pformat(vars(self), indent=4),
        )
        log.debug(text)


"""
==============================================================================
GROUP CLASS
==============================================================================
"""


class _group_class:
    """group class to store template group objects data"""

    def __init__(
        self,
        element,
        _ttp_,
        grp_index=0,
        top=False,
        path=None,
        pathchar=".",
        vars=None,
        parent_group_id=None,
    ):
        """Init method
        Attributes:
            element : xml ETree element to parse
            top (bool): to indicate that group is a top xml ETree group
            path (list): list containing results tree path, have to copy it otherwise
                it got overridden by recursion
            defaults (dict): contains group variables' default values
            runs (dict): to sotre modified defaults during parsing run
            default (str): group all variables' default value if no more specific default value given
            inputs (list): list of inputs names this group should be used for
            outputs (list): list of outputs to run for this group
            funcs (list): list of functions to run against group results
            method (str): indicate type of the group - [group | table]
            start_re (list): contains list of group start regular epressions
            end_re (list): contains list of group end regular expressions
            children (list): contains child group objects
            vars (dict): variables dictionary from template class
            grp_index (int): unique index of the group
            name (str): dot separate path string representing group result location within results tree
            group_id (tuple): unique ID of the group, tuple of (self.name, self.grp_index,)
        """
        self._ttp_ = _ttp_
        self.pathchar = pathchar
        self.top = top
        self.path = list(path or [])
        self.defaults = {}
        self.runs = {}
        self.default = "_Not_Given_"
        self.has_start_re_default = False
        self.outputs = []
        self.funcs = []
        self.method = "group"
        self.start_re = []
        self.end_re = []
        self.re = []
        self.children = []  # list to hold child groups
        self.name = ""
        self.group_id = ""
        self.parent_group_id = parent_group_id
        self.vars = vars or {}
        self.grp_index = grp_index
        self.inputs = []
        self.attributes = {}
        # extract data:
        self.get_attributes(element.attrib)
        self.set_anonymous_path()
        self.get_regexes(element.text)
        self.get_children(list(element))

    def set_anonymous_path(self):
        """Method to set anonymous path and name for groups with no name attribute."""
        if self.name == "":
            self.path = ["_anonymous_*"] if self.top else self.path
            self.name = ".".join(self.path)
            self.group_id = (self.name + "._anonymous_", self.grp_index)

    def get_attributes(self, data):
        def extract_default(O):
            self.default = self.vars.get(O, O)

        def extract_method(O):
            self.method = O.lower().strip()

        def extract_input(O):
            if self.top:
                self.inputs = [(i.strip()) for i in O.split(",")]

        def extract_output(O):
            if self.top:
                self.outputs = [(i.strip()) for i in O.split(",")]

        def extract_name(O):
            # check if absolute path given
            if O.startswith("/"):
                # check if parent group is _anonymous_
                if "_anonymous_" in self.path:
                    self.path = ["_anonymous_*"] + O.lstrip("/").split(self.pathchar)
                elif O == "/":
                    self.path = ["_anonymous_*"]
                else:
                    self.path = O.lstrip("/").split(self.pathchar)
            # threat relative path
            else:
                self.path = self.path + O.split(self.pathchar)
            self.name = ".".join(self.path)
            self.group_id = (self.name, self.grp_index)

        def extract_chain(var_name):
            """add items from chain to group functions"""
            variable_value = self.vars.get(var_name, var_name)
            if isinstance(variable_value, str):
                attributes = self._ttp_["utils"]["get_attributes"](variable_value)
            elif isinstance(variable_value, list):
                attributes = []
                for i in variable_value:
                    i_attribs = self._ttp_["utils"]["get_attributes"](i)
                    attributes += i_attribs
            for i in attributes:
                func_name = i["name"]
                if func_name in options:
                    options[func_name](i)
                elif func_name in self._ttp_["group"]:
                    self.funcs.append(i)
                else:
                    similar_funcs = self._ttp_["utils"]["guess"](
                        func_name, list(self._ttp_["group"].keys())
                    )
                    if similar_funcs:
                        log.error(
                            "group.extract_chain: unknown group function: '{}', most similar function(s) - {}".format(
                                func_name, ", ".join(similar_funcs)
                            )
                        )
                    else:
                        log.error(
                            'group.extract_chain: unknown group function: "{}"'.format(
                                func_name
                            )
                        )

        def extract_function(func_name, args_kwargs):
            attribs = self._ttp_["utils"]["get_attributes"](
                "{}({})".format(func_name, args_kwargs)
            )
            self.funcs.append(attribs[0])

        # group attributes extract functions dictionary:
        options = {
            "method": extract_method,
            "input": extract_input,
            "output": extract_output,
            "name": extract_name,
            "default": extract_default,
            "chain": extract_chain,
            "functions": extract_chain,
        }

        for attr_name, attributes in data.items():
            if attr_name.lower() in options:
                options[attr_name.lower()](attributes)
            else:
                extract_function(attr_name, attributes)

    def get_regexes(self, data, tail=False):
        varaibles_matches = []  # list of dictionaries
        regexes = []

        for line in data.splitlines():
            # skip empty lines and comments:
            if not line.strip():
                continue
            elif line.lstrip().startswith("##"):
                continue
            # strip leading spaces as they will be reconstructed in regex
            line = line.rstrip()
            # parse line against variable regexes
            match = re.findall(r"{{([\S\s]+?)}}", line)
            if not match:
                log.warning(
                    "group.get_regexes: variable not found in line: '{}'".format(line)
                )
                continue
            varaibles_matches.append({"variables": match, "line": line})
        for i in varaibles_matches:
            regex = ""
            variables = {}
            action = "add"
            is_line = False
            skip_regex = False
            for variable in i["variables"]:
                variableObj = _variable_class(
                    variable, i["line"], group=self, _ttp_=self._ttp_
                )

                # check if need to skip appending regex dict to regexes list
                # have to skip it for unconditional 'set' function
                if variableObj.skip_regex_dict == True:
                    skip_regex = True
                    continue
                # create variable dict:
                if variableObj.skip_variable_dict is False:
                    variables[variableObj.var_name] = variableObj
                    # add var_name_original for joinmatches function
                    variables[variableObj.var_name_original] = variableObj
                # form regex:
                regex = variableObj.form_regex(regex)

                # check if has sub variables:
                if variableObj.sub_variables:
                    variables.update(variableObj.sub_variables)
                # check if IS_LINE:
                if is_line == False:
                    is_line = variableObj.IS_LINE
                # modify save action only if it is not start or startempty already
                # and if it is not an ignore to not override other actions:
                if not "start" in action and not variableObj.var_name in ["ignore"]:
                    action = variableObj.SAVEACTION
            if skip_regex is True:
                continue
            regexes.append(
                {
                    "REGEX": re.compile(regex),  # re element
                    "VARIABLES": variables,  # Dict of variables objects
                    "ACTION": action,  # to indicate the save action
                    "GROUP": self,  # string contains current group object reference
                    "IS_LINE": is_line,  # boolean to indicate _line_ regex
                }
            )
        # form re, start re and end re lists:
        for index, re_dict in enumerate(regexes):
            if "end" in re_dict["ACTION"]:
                self.end_re.append(re_dict)
            elif tail == True:
                self.re.append(re_dict)
            elif index == 0:
                if not "start" in re_dict["ACTION"]:
                    re_dict["ACTION"] = "start"
                self.start_re.append(re_dict)
            elif self.method == "table":
                if not "start" in re_dict["ACTION"]:
                    re_dict["ACTION"] = "start"
                self.start_re.append(re_dict)
            elif "start" in re_dict["ACTION"]:
                self.start_re.append(re_dict)
            else:
                self.re.append(re_dict)
        # if no regexes in this top group, set it to start unconditionally
        if isinstance(self.default, dict):
            self.defaults.update(self.default)
            if self.start_re == []:
                self.has_start_re_default = True
        # check if has_start_re_default
        for start_re in self.start_re:
            if self.has_start_re_default:
                break
            for start_re_var_name in start_re["VARIABLES"].keys():
                if start_re_var_name in self.defaults:
                    self.has_start_re_default = True
                    break

    def get_children(self, child_groups):
        """Method to create child groups objects
        by iterating over all children.
        """
        for g_index, group in enumerate(child_groups):
            self.children.append(
                _group_class(
                    element=group,
                    top=False,
                    path=self.path,
                    pathchar=self.pathchar,
                    vars=self.vars,
                    grp_index=g_index,
                    parent_group_id=self.group_id,
                    _ttp_=self._ttp_,
                )
            )
            # get regexes from tail
            if group.tail.strip():
                self.get_regexes(data=group.tail, tail=True)

    def set_runs(self):
        """runs - default variable values during group
        parsing run, have to preserve original defaults
        as values in defaults dictionaries can change for 'set'
        function
        """
        self.runs = copy.deepcopy(self.defaults)
        # run recursion for children:
        for child in self.children:
            child.set_runs()

    def update_runs(self, data):
        # func to update runs of the groups using data dictionary
        for k, v in data.items():
            for dk, dv in self.runs.items():
                if dv == k:
                    self.runs[dk] = v
        # run recursion for children:
        for child in self.children:
            child.update_runs(data)

    def debug(self):
        from pprint import pformat

        attributes = dict(vars(self))
        _ = attributes.pop("_ttp_")
        text = "Group object {}, Group name '{}' content:\n{}".format(
            self, self.name, pformat(attributes, indent=4)
        )
        log.debug(text)
        for re_dict in self.start_re:
            for var_name, var_obj in re_dict["VARIABLES"].items():
                var_obj.debug()
        for re_dict in self.re:
            for var_name, var_obj in re_dict["VARIABLES"].items():
                var_obj.debug()
        for re_dict in self.end_re:
            for var_name, var_obj in re_dict["VARIABLES"].items():
                var_obj.debug()
        for group in self.children:
            group.debug()


"""
==============================================================================
TTP MATCH VARIABLE CLASS
==============================================================================
"""


class _variable_class:
    """
    variable class - to define variables and associated actions, conditions, regexes.
    """

    def __init__(self, variable, line, _ttp_, group=""):
        """
        Args:
            variable (str): contains variable content
            line(str): original line, need it here to form "set" actions
        """
        self._ttp_ = _ttp_
        # initiate variableClass object variables:
        self.variable = variable
        self.LINE = line  # original line from template
        self.functions = []  # actions and conditions list

        self.SAVEACTION = "add"  # to store action to do with results during saving
        self.group = group  # template object current group to save some vars
        self.IS_LINE = False  # to indicate that variable is _line_ regex
        self.skip_variable_dict = False  # will be set to true for 'ignore'
        self.skip_regex_dict = False  # will be set to true for 'set'
        self.var_res = []  # list of variable regexes
        self.sub_variables = {}  # dictionary to store child/sub variables
        self.regex = ""  # Regular expression sstring

        # form attributes - list of dictionaries:
        self.attributes = self._ttp_["utils"]["get_attributes"](variable)
        self.var_dict = self.attributes.pop(0)
        self.var_name = self.var_dict["name"]
        self.var_name_original = str(self.var_name)  # store original variable name

        # sanitize variable name to make it valid python identifier
        # by replacing all non alpha-characters with underscore
        # and prepending underscore if var name starts with digit
        self.var_name = re.sub(r"\W+|^(?=\d)", "_", self.var_name)

        # list of variables names that should not have defaults:
        self.skip_defaults = ["_end_", "_line_", "ignore", "_start_"]
        # add defaults
        if self.group.default != "_Not_Given_" and isinstance(self.group.default, str):
            if self.var_name_original not in self.group.defaults:
                if self.var_name_original not in self.skip_defaults:
                    self.group.defaults.update(
                        {self.var_name_original: self.group.default}
                    )
        # perform extractions:
        self.extract_functions()

    def extract_functions(self):
        """Method to extract variable actions and conditions."""

        def extract__start_(data):
            self.SAVEACTION = "start"
            if self.var_name == "_start_":
                self.SAVEACTION = "startempty"

        def extract__end_(data):
            self.SAVEACTION = "end"

        def extract_set(data):
            match_line = re.sub(r"{{([\S\s]+?)}}", "", self.LINE).rstrip()
            # handle conditional set when we have line to match
            if match_line:
                data["kwargs"]["match_line"] = (
                    "\n" + match_line
                )  # need to treat it as newline here
                self.functions.append(data)
            # handle unconditional set without line to match
            else:
                self.group.defaults.update({self.var_name_original: data["args"][0]})
                self.skip_regex_dict = True

        def extract_default(data):
            if self.var_name_original in self.skip_defaults:
                return
            if len(data["args"]) == 1:
                self.group.defaults.update({self.var_name_original: data["args"][0]})
            else:
                self.group.defaults.update({self.var_name_original: "None"})

        def extract_joinmatches(data):
            self.functions.append(data)
            self.SAVEACTION = "join"

        def extract__line_(data):
            # self.functions.append(data)
            self.SAVEACTION = "join"
            self.IS_LINE = True
            # extract _line_ regex as well
            extract_re(data)

        def extract_ignore(data):
            self.skip_variable_dict = True

        def extract_chain(data):
            """add items from chain to variable attributes and functions"""
            variable_value = self.group.vars.get(data["args"][0], None)
            if variable_value is None:
                log.error(
                    "match_variable.extract_chain: match variable - '{}', chain var '{}' not found".format(
                        self.var_name, data["args"][0]
                    )
                )
                return
            if isinstance(variable_value, str):
                attributes = self._ttp_["utils"]["get_attributes"](variable_value)
            elif isinstance(variable_value, list):
                attributes = []
                for i in variable_value:
                    i_attribs = self._ttp_["utils"]["get_attributes"](i)
                    attributes += i_attribs
            for i in attributes:
                name = i["name"]
                if name in extract_funcs:
                    extract_funcs[name](i)
                elif self._ttp_["patterns"]["get"](name=name):
                    extract_re(i)
                else:
                    self.functions.append(i)

        def extract_re(data):
            try:
                # if re('my_regex') was used
                regex = data["args"][0]
            except IndexError:
                # if {{ var_name | PHRASE }} used
                regex = data["name"]
            re_from_var = self.group.vars.get(regex, None)
            re_from_patterns = self._ttp_["patterns"]["get"](name=regex)
            # check template variables
            if re_from_var:
                self.var_res.append(re_from_var)
            # check ttp patterns
            elif re_from_patterns:
                self.var_res.append(re_from_patterns)
            # use regex as is
            else:
                self.var_res.append(regex)

        def get_arg_from_vars(data):
            """
            Helper function to get values of args from vars
            """
            if len(data["args"]) == 1:
                value = data["args"][0]
                data["args"] = (self.group.vars.get(value, value),)
            elif len(data["args"]) > 1:
                data["args"] = tuple([self.group.vars.get(i, i) for i in data["args"]])
            self.functions.append(data)

        def extract__headers_(data):
            self.SAVEACTION = "start"

        def skip(data):
            pass

        extract_funcs = {
            "ignore": extract_ignore,
            "_start_": extract__start_,
            "_end_": extract__end_,
            "_line_": extract__line_,
            "_exact_": skip,
            "_exact_space_": skip,
            "_headers_": extract__headers_,
            "columns": skip,
            "chain": extract_chain,
            "set": extract_set,
            "default": extract_default,
            "joinmatches": extract_joinmatches,
            "re": extract_re,
            "contains_re": get_arg_from_vars,
            "startswith_re": get_arg_from_vars,
            "endswith_re": get_arg_from_vars,
            "notstartswith_re": get_arg_from_vars,
            "notendswith_re": get_arg_from_vars,
            "exclude_re": get_arg_from_vars,
            "exclude": get_arg_from_vars,
            "contains": get_arg_from_vars,
            "equal": get_arg_from_vars,
            "notequal": get_arg_from_vars,
            "sformat": get_arg_from_vars,
        }
        # handle _start_, _line_ etc.
        if self.var_name in extract_funcs:
            extract_funcs[self.var_name](self.var_dict)
        # go over attribute extract function:
        for i in self.attributes:
            name = i["name"]
            if name in extract_funcs:
                extract_funcs[name](i)
            elif self._ttp_["patterns"]["get"](name=name):
                extract_re(i)
            else:
                self.functions.append(i)

    def form_regex(self, regex):
        """Method to form regular expression for template line."""
        # form escaped line by finding all spans of match variables in line,
        # after that split line in chunks and escape special chars, replace spaces and digits
        # for chunks that are not match variable, join chunks in esc_line string after that
        line_chunks = []
        no_indent_line = self.LINE.lstrip()
        llen = len(self.LINE)
        vars_spans = (
            [(0, 0)]
            + [i.span() for i in re.finditer(r"{{([\S\s]+?)}}", no_indent_line)]
            + [(llen, llen)]
        )
        for index, var_span in enumerate(vars_spans[1:]):
            previous_var_span = vars_spans[index]
            string_before_var = no_indent_line[previous_var_span[1] : var_span[0]]
            if string_before_var:
                string_before_var = re.escape(string_before_var)
                if not "_exact_space_" in self.LINE:
                    string_before_var = re.sub(
                        r"(\\ |\\\t)+", r"[ \\t]+", string_before_var
                    )
                    # prior to 0.8.0 variant that only accounts for spaces
                    # string_before_var = re.sub(r"(\\ )+", r"\\ +", string_before_var)
                if not "_exact_" in self.LINE:
                    string_before_var = re.sub(r"\d+", r"\\d+", string_before_var)
                line_chunks.append(string_before_var)
            # append current match variable to chunks
            line_chunks.append(no_indent_line[var_span[0] : var_span[1]])
        esc_line = "".join(line_chunks)
        esc_var = "{{" + self.variable + "}}"

        # check if regex empty, if so, make self.regex equal to escaped line, reconstruct indent and add start/end of line:
        if regex == "":
            # form indent to honor leading space characters like \t or \s:
            first_non_space_char_index = len(self.LINE) - len(self.LINE.lstrip())
            indent = self.LINE[:first_non_space_char_index]
            # form regex:
            self.regex = esc_line
            self.regex = indent + self.regex  # reconstruct indent
            self.regex = (
                r"\n" + self.regex + r"[\t ]*(?=\n|\r\n)"
            )  # use lookahead assertion for end of line and match any number of trailing spaces/tabs
        else:
            self.regex = regex

        def regex_ignore(data):
            if len(data["args"]) == 0:
                self.regex = self.regex.replace(esc_var, r"\S+", 1)
            elif len(data["args"]) == 1:
                pattern = data["args"][0]
                re_from_patterns = self._ttp_["patterns"]["get"](name=pattern)
                re_from_var = self.group.vars.get(pattern, None)
                if re_from_var:
                    self.regex = self.regex.replace(
                        esc_var, r"(?:{})".format(re_from_var), 1
                    )
                elif re_from_patterns:
                    self.regex = self.regex.replace(
                        esc_var, r"(?:{})".format(re_from_patterns), 1
                    )
                else:
                    self.regex = self.regex.replace(
                        esc_var, r"(?:{})".format(pattern), 1
                    )

        def regex_deleteVar(data):
            result = None
            if esc_var in self.regex:
                index = self.regex.find(esc_var)
                # slice regex string before esc_var start:
                result = self.regex[:index]
                # delete "[ \\t]+$" from end of line and add "[\t ]*(?=\n|\r\n)"
                result = re.sub(r"(\[ \\t\]\+)$", "", result) + r"[\t ]*(?=\n|\r\n)"
                # prior to 0.8.0 variant that only accounts for spaces
                # result = re.sub(r"(\\ \+)$", "", result) + r"[\t ]*(?=\n|\r\n)"
            if result:
                self.regex = result

        def regex_headers(data):
            """
            Goal is to create this regex::
                \\n(?P<Port>.{10})(?P<Name>.{1,19})(?P<Status>.*)(?=\\n)

            Out of this string::
              Port      Name  Status  {{ _headers_ }}

            :param data: (dict) variable dictionary, but not used here
            """
            # remove {{ _headers_ }} variable from end of string
            index = self.LINE.find(esc_var)
            self.regex = self.LINE[:index].rstrip()
            # find all headers
            headers = re.findall(r"(\S+\s+|\S+)", self.regex)
            # form columns count
            columns = len(headers) - 2
            for attribute in self.attributes:
                if attribute["name"] == "columns":
                    columns = max(1, int(attribute["args"][0]))
                    columns = min(columns, len(headers))
            # reconstruct headers line indentation
            self.regex = re.sub(
                r"\t", " " * 4, self.regex
            )  # replace tabs with 4 spaces
            headers[0] = " " * (len(self.regex) - len(self.regex.lstrip())) + headers[0]
            # form regex for mandatory columns of exact length
            row_re = [
                "(?P<{}>.{{{}}})".format(header.strip(), len(header))
                for header in headers[: columns - 1]
            ]
            # form regex for mandatory last column of variable length from 1 to header length
            row_re.append(
                "(?P<{}>.{{1,{}}})".format(
                    headers[columns - 1].strip(), len(headers[columns - 1])
                )
            )
            # form regexes for remaining optional columns
            row_re.extend(
                [
                    "(?P<{}>.{{0,{}}})".format(header.strip(), len(header))
                    for header in headers[columns:]
                ]
            )
            # form regex for last column
            if columns >= len(headers):
                row_re[-1] = "(?P<{}>.{{1,}})".format(headers[-1].strip())
            else:
                row_re[-1] = "(?P<{}>.*)".format(headers[-1].strip())
            # form final regex
            self.regex = r"\n" + "".join(row_re) + r"(?=\n|\r\n)"
            # form sub variables dictionary out of headers
            self.sub_variables = {
                var.strip(): _variable_class(
                    "{var} | strip | exclude({var})".format(var=var.strip()),
                    line="",
                    _ttp_=self._ttp_,
                    group=self.group,
                )
                for var in headers
            }

        # for variables like {{ ignore }} or {{ _headers_ }}
        regexFuncsVar = {
            "ignore": regex_ignore,
            "_start_": regex_deleteVar,
            "_end_": regex_deleteVar,
            "_headers_": regex_headers,
        }
        if self.var_name in regexFuncsVar:
            regexFuncsVar[self.var_name](self.var_dict)
        # for the rest of functions:
        regexFuncs = {"set": regex_deleteVar}
        # go over all keywords to form regex:
        for i in self.functions:
            if i["name"] in regexFuncs:
                regexFuncs[i["name"]](i)
        # assign default re if variable without regex formatters:
        if self.var_res == []:
            self.var_res.append(self._ttp_["patterns"]["get"](name="WORD"))
        # form variable regex by replacing escaped variable, if it is in regex,
        # except for the case if variable is "ignore" as it already was replaced
        # in regex_ignore function:
        if self.var_name != "ignore":
            self.regex = self.regex.replace(
                esc_var,
                r"(?P<{}>(?:{}))".format(self.var_name, r")|(?:".join(self.var_res)),
                1,
            )
        # after regexes formed we can delete unnecessary variables:
        if log.isEnabledFor(logging.DEBUG) == False:
            del self.attributes, esc_line
            del self.LINE, self.skip_defaults
            del self.var_dict, self.var_res
        return self.regex

    def debug(self):
        from pprint import pformat

        attributes = dict(vars(self))
        _ = attributes.pop("_ttp_")  # remove _ttp_ dictionary to not clutter the output
        text = "Variable object {}, Variable name '{}' content:\n{}".format(
            self, self.var_name, pformat(attributes, indent=4)
        )
        log.debug(text)


"""
==============================================================================
TTP PARSER OBJECT
==============================================================================
"""


class _parser_class:
    """Parser Object to run parsing of data and constructing resulted dictionary/list"""

    def __init__(self, lookups, vars, groups, _ttp_):
        self.lookups = lookups
        self.original_vars = vars
        self.groups = groups
        self.main_results = {}
        self.DATATEXT = ""
        self.DATANAME = ""
        self._ttp_ = _ttp_

    def set_data(self, D, main_results=None, input_functions=None):
        """Method to load data:
        Args:
            D (tuple): items are dict of (data_type, data_path,)
        """
        main_results = main_results or {}
        input_functions = input_functions or []
        self.main_results = main_results
        if D[0] == "text_data":
            self.DATATEXT = "\n" + D[1] + "\n\n"
            self.DATANAME = "text_data"
        elif D[0] == "structured_data":
            self.DATATEXT = D[1]
            self.DATANAME = "structured_data"
        else:
            data = self._ttp_["utils"]["load_files"](path=D[1], read=True)
            # data is a list of one tuple - [(data_type, data_text,)]
            self.DATATEXT = "\n" + data[0][1] + "\n\n"
            self.DATANAME = D[1]
        # set vars to original vars copy and run vars functions against DATATEXT
        self.vars = self.original_vars.copy()
        self._ttp_["vars"] = self.vars
        self.run_var_functions()
        # create groups' runs dicts to hold copy of defaults to updated them with var values
        for G in self.groups:
            G.set_runs()
        # re-initiate _ttp_ dictionary parser object
        self._ttp_["parser_object"] = self
        # run input functions
        for item in input_functions:
            func_name, args, kwargs = (
                item["name"],
                item.get("args", []),
                item.get("kwargs", {}),
            )
            self.DATATEXT, flags = self._ttp_["input"][func_name](
                self.DATATEXT, *args, **kwargs
            )
            if flags == False:
                break

    def update_groups_runs(self, D):
        """Method to update groups runs dictionaries with new values deirved
        during parsing, can be called from 'record' variable functions
        """
        for G in self.groups:
            G.update_runs(D)

    def run_var_functions(self):
        """Method to run variables functions before parsing data"""
        for VARname, VARvalue in self.vars["_var_functions_"].items():
            try:
                result = self._ttp_["variable"][VARvalue](self.DATATEXT, self.DATANAME)
                if result:
                    self.vars.update({VARname: result})
            except:
                log.error(
                    "ttp_parser.run_var_functions: '{}' variable function failed".format(
                        VARvalue
                    )
                )

    def parse(self, groups_indexes):
        """Main parser_call parsing method.
        Args::
            groups_indexes(list) : list of group indexes to run
        """
        unsort_rslts = (
            []
        )  # list of dictionaries - one item per top group, each dictionary
        # contains unsorted match results for REs within group
        raw_results = []  # list to store sorted results for groups with global outputs
        grps_unsort_rslts = []  # match results for groups with group specific outputs
        # each item is a tuple of (results, group.outputs,)
        grps_raw_results = []  # group specific sorted results

        def check_matches(regex, matches, results, start):
            for match in matches:
                result = {}  # dict to store result
                temp = {}
                # check if groupdict present - means regex with no set variables been matchesd
                if match.groupdict():
                    temp = match.groupdict()
                # we have match but no variables - set regex, need to check it as well:
                else:
                    temp = {key: match.group() for key in regex["VARIABLES"].keys()}
                # process matched values
                for var_name, data in temp.items():
                    flags = {}
                    for item in regex["VARIABLES"][var_name].functions:
                        func_name = item["name"]
                        args = item["args"]
                        kwargs = item["kwargs"]
                        try:  # try variable function
                            data, flag = self._ttp_["match"][func_name](
                                data, *args, **kwargs
                            )
                        except KeyError:
                            try:  # try data built-in function. e.g. if data is string, can run data.upper()
                                attrib = getattr(data, func_name)
                                if callable(attrib):
                                    run_result = attrib(*args, **kwargs)
                                else:
                                    run_result = attrib
                                if run_result is False:
                                    flag = False
                                elif run_result is True:
                                    flag = True
                                else:
                                    data = run_result
                                    flag = None
                            except AttributeError as e:
                                flag = None
                                log.error(
                                    "ttp_parser.check_matches: match variable function '{}' failed, data '{}', error '{}'".format(
                                        func_name, data, e
                                    )
                                )
                                similar_funcs = self._ttp_["utils"]["guess"](
                                    func_name, list(self._ttp_["match"].keys())
                                )
                                if similar_funcs:
                                    log.error(
                                        "ttp_parser.check_matches: the most similar match variable function(s) - {}".format(
                                            ", ".join(similar_funcs)
                                        )
                                    )
                        if flag is False:
                            result = (
                                False  # if flag False - checks produced negative result
                            )
                            break
                        elif isinstance(flag, dict):
                            # update new_field data preserving previously got new_field
                            if "new_field" in flags and "new_field" in flag:
                                flags["new_field"].update(flag["new_field"])
                            else:
                                flags.update(flag)
                    if result is False:
                        break
                    # add match result to results using original match variable name
                    result.update(
                        {regex["VARIABLES"][var_name].var_name_original: data}
                    )

                    # run flags
                    if "new_field" in flags:
                        result.update(flags["new_field"])
                # skip not start regexes that evaluated to False
                if result is False and not regex["ACTION"].startswith("start"):
                    continue
                # form result dictionary of dictionaries:
                span_start = start + match.span()[0]
                if span_start not in results:
                    results[span_start] = [(regex, result)]
                else:
                    results[span_start].append((regex, result))

        def run_re(group, results, start=0, end=-1):
            """Recursive function to run REs"""
            # results - dict of {span_start: [(re1, match1), (re2, match2)]}
            s = 0  # int to store the lowest start re span value
            se = 0  # int to store the highest/last start re span value - start end
            e = -1  # int to store the biggest end re span value
            group_start_found = False

            # run start REs:
            for R in group.start_re:
                start_matches = list(R["REGEX"].finditer(self.DATATEXT[start:end]))
                if not start_matches:
                    continue
                check_matches(R, start_matches, results, start)
                # if s is bigger, make it smaller:
                if s > start_matches[0].span()[0] or group_start_found is False:
                    group_start_found = True
                    s = start_matches[0].span()[0]
                # if se is smaller make it bigger except for when start re is _line_,
                # if start re is _line_ end matches have bigger priority
                if se < start_matches[-1].span()[0] and not R["IS_LINE"]:
                    se = start_matches[-1].span()[1] + start
            start = start + s
            # if no matches found for any start REs of this group - skip the rest of REs
            if not group_start_found:
                # handle group with no matches but with start re default values
                if group.has_start_re_default:
                    key = 10000000
                    # group.start_re == [] only for tag with no regexes
                    start_re = (
                        {"ACTION": "start", "VARIABLES": group.runs, "GROUP": group}
                        if group.start_re == []
                        else group.start_re[0]
                    )
                    # find free index to place results in
                    while key in results:
                        key += 1
                    else:
                        results[key] = [(start_re, {})]

                # run recursion to fill in results for children
                for child_group in group.children:
                    if group.start_re == [] or child_group.has_start_re_default:
                        run_re(child_group, results, start, end)
                return results
            # run end REs:
            for R in group.end_re:
                end_matches = list(R["REGEX"].finditer(self.DATATEXT[start:end]))
                if not end_matches:
                    continue
                check_matches(R, end_matches, results, start)
                # make e bigger if e is smaller than last end match
                # and last end match is bigger than last start match
                if e < end_matches[-1].span()[1] and end_matches[-1].span()[1] > se:
                    e = end_matches[-1].span()[1]
            if e != -1:
                end = start + e
                # clean up results beyond last _end_ match
                # can happen if stat re is _line_
                empty_matches_keys = []
                for span_start, mathches in results.items():
                    for item in mathches:
                        if item[0]["GROUP"] is group and span_start > end:
                            mathches.remove(item)
                    # if no matches left
                    if mathches == []:
                        empty_matches_keys.append(span_start)
                for key in empty_matches_keys:
                    results.pop(key)
            # run normal REs:
            for R in group.re:
                check_matches(
                    R,
                    list(R["REGEX"].finditer(self.DATATEXT[start:end])),
                    results,
                    start,
                )
            # run recursion:
            for child_group in group.children:
                run_re(child_group, results, start, end)
            return results

        # run parsing to produce unsorted results:
        for group_index in groups_indexes:
            group = self.groups[group_index]
            # get results for groups with global only outputs:
            if group.outputs == []:
                unsort_rslts.append(run_re(group, results={}))
            # get results for groups with group specific results:
            else:
                # form a tuple of ({results}, [group.outputs],)
                grps_unsort_rslts.append((run_re(group, results={}), group.outputs))
        # update groups runs (group default values) with global variables
        self.update_groups_runs(self._ttp_["global_vars"])
        # update groups runs (group default values) with group specific/local variables
        self.update_groups_runs(self.vars)

        # sort results for groups with global outputs
        for group_result in unsort_rslts:
            if group_result:
                raw_results.append(
                    [group_result[key] for key in sorted(list(group_result.keys()))]
                )

        # import pprint; pprint.pprint(raw_results)

        # form results for global groups:
        RSLTSOBJ = _results_class(self._ttp_)
        RSLTSOBJ.make_results(self.vars, raw_results, main_results=self.main_results)
        self.main_results = RSLTSOBJ.results

        # sort results for groups with group specific outputs
        for group_result in grps_unsort_rslts:
            if group_result[0]:
                grps_raw_results.append(
                    # tuple item that contains group.outputs:
                    (
                        [
                            group_result[0][key]
                            for key in sorted(list(group_result[0].keys()))
                        ],
                        group_result[1],
                    )
                )
        # form results for groups specific results with running groups through outputs:
        for grp_raw_result in grps_raw_results:
            RSLTSOBJ = _results_class(self._ttp_)
            RSLTSOBJ.make_results(self.vars, [grp_raw_result[0]], main_results={})
            grp_result = RSLTSOBJ.results
            for output in grp_raw_result[1]:
                grp_result = output.run(data=grp_result)
            # transform results into list:
            if isinstance(self.main_results, dict):
                if self.main_results:
                    self.main_results = [self.main_results]
                else:
                    self.main_results = []
            # save results into global results list:
            self.main_results.append(grp_result)


"""
==============================================================================
TTP results FORMATTER OBJECT
==============================================================================
"""


class _results_class:
    """
    Class to save results and do actions with them.
    Args:
        self.dyn_path_cache (dict): used to store dynamic path variables
    """

    def __init__(self, _ttp_):
        self._ttp_ = _ttp_
        self.results = {}
        self.started_groups = (
            []
        )  # keeps track of started groups to not add false matches
        self.ended_groups = (
            set()
        )  # keeps track of ended groups to not add false matches or filtered results
        self.record = {
            "result": {},
            "PATH": [],
            "FUNCTIONS": [],
            "DEFAULTS": {},
            "GRP_ID": None,
        }
        self.dyn_path_cache = {}
        self._ttp_["results_object"] = self

    def make_results(self, variables, raw_results, main_results):
        self.results = main_results
        self.variables = variables
        saveFuncs = {
            "start": self.start,  # start - to start new group;
            "add": self.add,  # add - to add data to group, default action;
            "startempty": self.startempty,  # startempty - to start new empty group in case if _start_ found;
            "end": self.end,  # end - to explicitly signal the end of group to LOCK it;
            "join": self.join,  # join - to join results for given variable, e.g. joinmatches;
        }
        # save _vars_to_results_ to results if any:
        if raw_results:
            self.save_vars(variables)
        # iterate over group results and form results structure:
        for group_results in raw_results:
            # iterate over each match result for the group
            for result in group_results:
                # if result been matched by one regex only
                if len(result) == 1:
                    re_ = result[0][0]
                    result_data = result[0][1]
                # if same results captured by multiple regexes, need to do further decision making
                else:
                    re_ = None
                    startempty_re, start_re, normal_re, line_re = [], [], [], []
                    # sort matches across startempty (_start_), start, normal and line REs
                    for index, item in enumerate(result):
                        if item[0]["IS_LINE"] == True:
                            line_re.append(index)
                        elif item[0]["ACTION"] == "start":
                            start_re.append(index)
                        elif item[0]["ACTION"] == "startempty":
                            startempty_re.append(index)
                        else:
                            normal_re.append(index)
                    # startempty RE always more preferred
                    if startempty_re:
                        # first run - look for results with same path as current record
                        for index in startempty_re:
                            re_ = result[index][0]
                            result_data = result[index][1]
                            # skip results that did not pass validation check
                            if result_data == False:
                                continue
                            # prefer result with same path as current record
                            elif re_["GROUP"].group_id == self.record["GRP_ID"]:
                                break
                        else:
                            # if second run - check other preferred conditions
                            for index in startempty_re:
                                re_ = result[index][0]
                                result_data = result[index][1]
                                # skip results that did not pass validation check
                                if result_data == False:
                                    continue
                                # prefer children of current record group
                                elif self.record["GRP_ID"] and re_["GROUP"].group_id[
                                    0
                                ].startswith(self.record["GRP_ID"][0]):
                                    break
                                # prefer results for group that has parent started
                                elif (
                                    re_["GROUP"].parent_group_id in self.started_groups
                                ):
                                    break
                    # start RE preferred next
                    elif start_re:
                        # first run - look for results with same path as current record
                        for index in start_re:
                            re_ = result[index][0]
                            result_data = result[index][1]
                            # skip results that did not pass validation check
                            if result_data == False:
                                continue
                            # prefer result with same path as current record
                            elif re_["GROUP"].group_id == self.record["GRP_ID"]:
                                break
                        else:
                            # if second run - check other preferred conditions
                            for index in start_re:
                                re_ = result[index][0]
                                result_data = result[index][1]
                                # skip results that did not pass validation check
                                if result_data == False:
                                    continue
                                # prefer children of current record group
                                elif self.record["GRP_ID"] and re_["GROUP"].group_id[
                                    0
                                ].startswith(self.record["GRP_ID"][0]):
                                    break
                                # prefer results for group that has parent started
                                elif (
                                    re_["GROUP"].parent_group_id in self.started_groups
                                ):
                                    break
                    # normal and end REs preferred next
                    elif normal_re:
                        for index in normal_re:
                            re_ = result[index][0]
                            result_data = result[index][1]
                            # prefer result with same path as current record
                            if re_["GROUP"].group_id == self.record["GRP_ID"]:
                                break
                        # iterate again and prefer results for group that already started
                        else:
                            for index in normal_re:
                                re_ = result[index][0]
                                result_data = result[index][1]
                                if re_["GROUP"].group_id in self.started_groups:
                                    break
                    # line REs have least preference
                    elif line_re:
                        for index in line_re:
                            re_ = result[index][0]
                            result_data = result[index][1]
                            # prefer result with same path as current record
                            if re_["GROUP"].group_id == self.record["GRP_ID"]:
                                break

                group = re_["GROUP"]

                # check if result is false, add group to ended groups if so
                if result_data == False:
                    self.ended_groups.add(re_["GROUP"].group_id)
                    continue
                # if parent is ended skip this child group results
                elif re_["GROUP"].parent_group_id in self.ended_groups:
                    continue
                # evaluate results to check if need to un-end ended group
                elif re_["GROUP"].group_id in self.ended_groups:
                    if re_["ACTION"].startswith("start"):
                        self.ended_groups.remove(re_["GROUP"].group_id)
                    else:
                        continue

                # Save results:
                saveFuncs[re_["ACTION"]](
                    result=result_data,
                    PATH=list(group.path),
                    DEFAULTS=group.runs,
                    FUNCTIONS=group.funcs,
                    REDICT=re_,
                )
        # check the last group:
        if self.processgrp() is not False:
            self.save_curelements(
                result_data=self.record["result"], result_path=self.record["PATH"]
            )

    def save_vars(self, variables):
        # need to sort keys first to introduce deterministic behavior
        sorted_pathes = sorted(list(variables["_vars_to_results_"].keys()))
        for path_item in sorted_pathes:
            # skip empty path items:
            if not path_item:
                continue
            vars_names = variables["_vars_to_results_"][path_item]
            result = {}
            for var_name in vars_names:
                if var_name in variables:
                    result[var_name] = variables[var_name]
            self.record = {
                "result": result,
                "PATH": [i.strip() for i in path_item.split(".")],
                "DEFAULTS": {},
            }
            processed_path = self.form_path(self.record["PATH"])
            if processed_path:
                self.record["PATH"] = processed_path
            else:
                continue
            self.save_curelements(
                result_data=self.record["result"], result_path=self.record["PATH"]
            )
        # set record to default value:
        self.record = {
            "result": {},
            "PATH": [],
            "FUNCTIONS": [],
            "DEFAULTS": {},
            "GRP_ID": None,
        }

    def value_to_list(self, DATA, PATH, result):
        """recursive function to get value at given PATH and transform it into the list
        Example:
            DATA={1:{2:{3:{4:5, 6:7}}}} and PATH=(1,2,3)
            running this function will transform DATA to {1:{2:{3:[{4:5, 6:7}]}}}
        Args:
            DATA (dict): data to add to the DATA
            PATH (list): list of path keys
            result : dict or list that contains results
        Returns:
            transformed DATA with list at given PATH and appended results to it
        """
        if PATH:
            name = PATH[0][0]
            # add support for null path
            if name == "_":
                if len(PATH) == 1:  # reached end of PATH, process DATA and return it
                    if isinstance(DATA, dict):
                        DATA.update(result)
                    elif isinstance(DATA, list):
                        DATA[-1].update(result)
                    return DATA
                else:  # have more path items, need to skip null path,
                    _ = PATH.pop(0)  # remove null path item to skip it
                    name = PATH[0][0]
            if isinstance(DATA, dict):
                if name in DATA:
                    DATA[name] = self.value_to_list(DATA[name], PATH[1:], result)
                    return DATA
            elif isinstance(DATA, list):
                if name in DATA[-1]:
                    DATA[-1][name] = self.value_to_list(
                        DATA[-1][name], PATH[1:], result
                    )
                    return DATA
        else:
            return [
                DATA,
                result,
            ]  # for resulting list - value at given PATH transformed into list with result appended to it

    def list_to_dict_fwd(self, KEYS):
        """recursive function to build nested dict starting from first element in list - forward order
        Args:
            KEYS (list): list that contains keys
        Returns:
            Nested dictionary
        Example:
            if KEYS=[1,2,3,4], returns {1:{2:{3:{4:{}}}}}, or
            if KEYS=[1,2,3,4*], returns {1:{2:{3:{4:[]}}}}, or
            if KEYS=[1,2,3*,4], returns {1:{2:{3:[{4:{}}]}}}
        """
        if KEYS:  # check if list is not empty:
            # add support for null path
            if KEYS[0] == "_":
                if len(KEYS) == 1:
                    return {}
                else:
                    _ = KEYS.pop(0)
            name = KEYS[0][0]
            asterisk_count = KEYS[0][1]
            if self._ttp_["dynamic_path_key_to_int"]:
                # convert key to integer if it is integer
                name = int(name) if name.isdigit() else name
            if asterisk_count == "*":  # if one * at the end - make a list
                if len(KEYS) == 1:  # if KEYS=[1,2,3,4*], returns {1:{2:{3:{4:[{}]}}}}
                    return {name: []}  # if last item in PATH - return emplty list
                else:  # if KEYS=[1,2,3*,4], returns {1:{2:{3:[{4:{}}]}}}
                    return {
                        name: [self.list_to_dict_fwd(KEYS[1:])]
                    }  # run recursion if PATH has more than one element
            else:  # if KEYS=[1,2,3,4], returns {1:{2:{3:{4:{}}}}}
                return {name: self.list_to_dict_fwd(KEYS[1:])}
        return {}  # return empty dict if KEYS list empty

    def dict_by_path(self, PATH, ELEMENT):
        """recursive function to iterate over PATH list and merge it into ELEMENT dict as new keys
        Args:
            PATH (list): list of keys in absolute path format
            ELEMENT: nested list, list of dictionaries or dictionary to get element from
        Returns:
            last element at given PATH of transformed ELEMENT dictionary
        """
        if PATH == []:
            return ELEMENT  # check if PATH is empty, if so - stop and return ELEMENT
        elif isinstance(ELEMENT, dict):
            name = PATH[0][0]
            if self._ttp_["dynamic_path_key_to_int"]:
                # convert key to integer if it is integer
                name = int(name) if name.isdigit() else name
            # add support for null path
            if name == "_":
                if len(PATH) == 1:  # reached end of PATH, need to return ELEMENT
                    return ELEMENT
                else:  # have more path items, need to skip null path,
                    _ = PATH.pop(0)  # remove null path item to skip it
                    name = PATH[0][0]
            if name in ELEMENT:  # check if first element of the list is in ELEMENT
                return self.dict_by_path(
                    PATH[1:], ELEMENT[name]
                )  # run recursion with moving forward in both - PATH and ELEMENT
            else:  # if first element not in dict - we found new key, update it into the dict
                ELEMENT.update(
                    self.list_to_dict_fwd(PATH)
                )  # update new key into the nested dict with value equal to new nested dict branch
                return self.dict_by_path(
                    PATH[1:], ELEMENT[name]
                )  # run recursion to reach element in the PATH
        elif isinstance(ELEMENT, list):
            if ELEMENT == []:
                ELEMENT.append(
                    self.list_to_dict_fwd(PATH)
                )  # check if element list is empty, if so - append empty dict to it
            return self.dict_by_path(
                PATH, ELEMENT[-1]
            )  # run recursion with last item in the list

    def _merge_recursively(self, element, result_data):
        """
        Function to recursively merge result_data dictionary into element dictionary

        :param element: (dict) current results element dictionary
        :param result_data: (dict) new results data to merge into existing one
        """
        for nk, nd in result_data.items():
            # check if need to run recursion
            if element.get(nk) and isinstance(nd, dict):
                self._merge_recursively(element[nk], nd)
            # nd is not a dict, simply save it in existing results
            else:
                element[nk] = nd

    def save_curelements(self, result_data, result_path):
        """Method to save current group results in self.results"""
        # get ELEMENT from self.results by result_path
        E = self.dict_by_path(PATH=result_path, ELEMENT=self.results)
        if isinstance(E, list) and result_data:
            if self.record.get("merge_with_last"):
                self._merge_recursively(E[-1], result_data)
            else:
                E.append(result_data)
        elif isinstance(E, dict):
            if self.record.get("merge_with_last"):
                self._merge_recursively(E, result_data)
            # check if result_path endswith "**" - update result's ELEMENET without converting it into list:
            elif result_path[-1][1] == "**":
                result_data.update(E)
                E.update(result_data)
            # to match all the other cases, like templates without "**" in path:
            elif E != {}:
                # transform ELEMENT dict to list and append data to it:
                self.results = self.value_to_list(
                    DATA=self.results, PATH=result_path, result=result_data
                )
            else:
                E.update(result_data)

    def reconstruct_last_element(self, result_data, result_path):
        """
        Method to retrieve last element value, make a copy of it and nerge with
        current results. This is to reconstruct group results for processing in
        a case where we have tail matches.
        """
        # get ELEMENT from self.results by result_path
        E = self.dict_by_path(PATH=result_path, ELEMENT=self.results)
        if isinstance(E, list):
            copied = E[-1].copy()
        elif isinstance(E, dict):
            copied = E.copy()
        copied.update(result_data)
        return copied

    def start(self, result, PATH, DEFAULTS=None, FUNCTIONS=None, REDICT=""):
        DEFAULTS = DEFAULTS or {}
        FUNCTIONS = FUNCTIONS or []
        # perform group path tracing
        while self.started_groups:
            # check if child group started
            if REDICT["GROUP"].parent_group_id == self.started_groups[-1]:
                self.started_groups.append(REDICT["GROUP"].group_id)
                break
            # check if _line_ group started, don't remove previous started
            # groups to allow collection of non matched lines - #94
            if REDICT.get("IS_LINE"):
                self.started_groups.append(REDICT["GROUP"].group_id)
                break
            _ = self.started_groups.pop()
        # meaning top group started
        else:
            if REDICT["GROUP"].group_id not in self.started_groups:
                self.started_groups.append(REDICT["GROUP"].group_id)

        # process recorded group results and save them
        if self.processgrp() != False:
            self.save_curelements(
                result_data=self.record["result"], result_path=self.record["PATH"]
            )
        self.record = {
            "result": result,
            "DEFAULTS": DEFAULTS.copy(),
            "PATH": PATH,
            "FUNCTIONS": FUNCTIONS,
            "GRP_ID": REDICT["GROUP"].group_id,
        }

    def startempty(self, result, PATH, DEFAULTS=None, FUNCTIONS=None, REDICT=""):
        DEFAULTS = DEFAULTS or {}
        FUNCTIONS = FUNCTIONS or []
        # perform group path tracing
        while self.started_groups:
            # check if child group started
            if REDICT["GROUP"].parent_group_id == self.started_groups[-1]:
                self.started_groups.append(REDICT["GROUP"].group_id)
                break
            # check if _line_ group started, don't remove previous started
            # groups to allow collection of non matched lines - #94
            if REDICT.get("IS_LINE"):
                self.started_groups.append(REDICT["GROUP"].group_id)
                break
            _ = self.started_groups.pop()
        # meaning top group started
        else:
            if REDICT["GROUP"].group_id not in self.started_groups:
                self.started_groups.append(REDICT["GROUP"].group_id)

        # process recorded group results and save them
        if self.processgrp() != False:
            self.save_curelements(
                result_data=self.record["result"], result_path=self.record["PATH"]
            )
        self.record = {
            "result": {},
            "DEFAULTS": DEFAULTS.copy(),
            "PATH": PATH,
            "FUNCTIONS": FUNCTIONS,
            "GRP_ID": REDICT["GROUP"].group_id,
        }

    def add(self, result, PATH, DEFAULTS=None, FUNCTIONS=None, REDICT=""):
        DEFAULTS = DEFAULTS or {}
        FUNCTIONS = FUNCTIONS or []
        if self.record["PATH"] == PATH:  # if same path - save into self.record
            # update without overriding already existing values:
            result.update(self.record["result"])
            self.record["result"] = result
        # if different path - that can happen if we have group ended and result
        # actually belongs to another already started group, hence need to save
        # directly into results
        elif REDICT["GROUP"].group_id in self.started_groups:
            # save current results to results structure and start new record
            self.start(
                result=result,
                PATH=PATH,
                DEFAULTS=DEFAULTS,
                FUNCTIONS=FUNCTIONS,
                REDICT=REDICT,
            )
            # mark new record as needed to be merged with last item in results
            self.record["merge_with_last"] = True
            # no need to add DEFAULTS for this record, DEFAULTS added by previous group
            self.record["DEFAULTS"] = {}

    def join(self, result, PATH, DEFAULTS=None, FUNCTIONS=None, REDICT=""):
        DEFAULTS = DEFAULTS or {}
        FUNCTIONS = FUNCTIONS or []
        # if same path - save into self.record
        if self.record["PATH"] == PATH:
            # retrieve joinchar to use
            joinchar = "\n"
            for varname, varvalue in result.items():
                # check if need to skip vars that were added to results on the go
                if not varname in REDICT["VARIABLES"]:
                    continue
                for item in REDICT["VARIABLES"][varname].functions:
                    if item["name"] == "joinmatches":
                        joinchar = item["args"][0] if item["args"] else joinchar
                        break
            # join results:
            for k in result.keys():
                if k in self.record["result"]:  # if we already have results
                    if isinstance(self.record["result"][k], str):
                        self.record["result"][k] += joinchar + result[k]  # join strings
                    elif isinstance(self.record["result"][k], list):
                        if isinstance(result[k], list):
                            self.record["result"][k] += result[k]  # join lists
                        else:
                            self.record["result"][k].append(result[k])  # append to list
                    else:  # transform result to list and append new result to it
                        self.record["result"][k] = [self.record["result"][k], result[k]]
                else:
                    self.record["result"][k] = result[k]  # if first result
        # if different path - that can happen if we have group ended and result
        # actually belongs to another already started group, hence need to save
        # directly into results
        elif REDICT["GROUP"].group_id in self.started_groups:
            # save current results to results structure and start new record by calling self.start
            self.start(
                result=result,
                PATH=PATH,
                DEFAULTS=DEFAULTS,
                FUNCTIONS=FUNCTIONS,
                REDICT=REDICT,
            )
            # mark new record as needed to be merged with last item in results
            self.record["merge_with_last"] = True
            # no need to add DEFAULTS for this record as DEFAULTS processed already by previous group record
            self.record["DEFAULTS"] = {}

    def end(self, result, PATH, DEFAULTS=None, FUNCTIONS=None, REDICT=""):
        DEFAULTS = DEFAULTS or {}
        FUNCTIONS = FUNCTIONS or []
        # if path not the same and this is not child it means that
        # results belong to different group - do not end current group
        if (
            self.record["PATH"] != PATH
            and
            # if below is true, this is child group:
            REDICT["GROUP"].group_id == self.started_groups[-1]
        ):
            return
        # action to end current group by adding it to ended groups
        self.ended_groups.add(REDICT["GROUP"].group_id)

    def form_path(self, path):
        """
        Method to form dynamic path transforming it into a list of tuples,
        where each tuple first element is a path item value and second
        element is a number of asterisks, need to keep asterisks count
        separatefrom path item value becasue match result value can end
        with asterisk - issue #97
        """
        for index, path_item in enumerate(path):
            asterisk_count = len(path_item) - len(path_item.rstrip("*"))
            path_item = path_item.rstrip("*")
            match = re.findall(r"{{\s*(\S+)\s*}}", path_item)
            if match:
                for m in match:
                    pattern = r"{{\s*" + m + r"\s*}}"
                    if m in self.record["result"]:
                        self.dyn_path_cache[m] = self.record["result"][m]
                        repl = str(self.record["result"].pop(m))
                        # try re replacement first
                        try:
                            path_item = re.sub(pattern, repl, path_item)
                        # might fail if match contains '\', try string replace
                        except re.error:
                            path_item = re.sub(pattern, "__replace_me__", path_item)
                            path_item = path_item.replace("__replace_me__", repl)
                    elif m in self.dyn_path_cache:
                        path_item = re.sub(pattern, self.dyn_path_cache[m], path_item)
                    elif m in self.variables:
                        path_item = re.sub(pattern, str(self.variables[m]), path_item)
                    else:
                        return False
            path[index] = (
                path_item,
                asterisk_count * "*",
            )
        return path

    def processgrp(self):
        """Method to process group results"""
        # add default values to group results
        for k, v in self.record["DEFAULTS"].items():
            self.record["result"].setdefault(k, v)
        # if merge_with_last - tail match, attempt to reconstruct group result
        # this only will work if self.record["result"] contains enough info to form PATH
        if self.record.get("merge_with_last") is True:
            processed_path = self.form_path(list(self.record["PATH"]))
            if processed_path:
                self.record["result"] = self.reconstruct_last_element(
                    self.record["result"], processed_path
                )
        # process group functions
        for item in self.record["FUNCTIONS"]:
            func_name = item["name"]
            args = item.get("args", [])
            kwargs = item.get("kwargs", {})
            # run group functions
            self.record["result"], flags = self._ttp_["group"][func_name](
                self.record["result"], *args, **kwargs
            )
            if flags == False:
                return False
        processed_path = self.form_path(self.record["PATH"])
        if processed_path:
            self.record["PATH"] = processed_path
        else:
            return False


"""
==============================================================================
TTP OUTPUTTER CLASS
==============================================================================
"""


class _outputter_class:
    """Class to serve run output functions, returners and formatters"""

    def __init__(self, element=None, template_obj=None, _ttp_=None, **kwargs):
        # set attributes default values
        self._ttp_ = _ttp_
        self.attributes = {"returner": "self", "format": "raw", "load": "python"}
        self.tag_load = {}
        self.template_obj = template_obj
        self.name = None
        self.return_to_self = False
        self.funcs = []
        # get output attributes:
        if element is not None:
            self.element = element
            self.attributes.update(element.attrib)
            self.extract_load(element)
        elif kwargs:
            self.attributes.update(kwargs)
        self.get_attributes(self.attributes.copy())

    def extract_load(self, element):
        # if formatter is jinja2, use text loader to load template
        if self.attributes.get("format") == "jinja2":
            self.attributes["load"] = "text"
        # run attributes extraction
        attribs = self._ttp_["utils"]["load_struct"](element.text, **self.attributes)
        self.tag_load = attribs if attribs else element.text
        if isinstance(attribs, dict):
            self.attributes.update(attribs)

    def get_attributes(self, data):
        def extract_name(O):
            self.name = O

        def extract_returner(O):
            self.attributes["returner"] = [i.strip() for i in O.split(",")]

        def extract_filename(O):
            """File name can contain time formatters supported by strftime"""
            from time import strftime

            self.attributes["filename"] = strftime(O)

        def extract_format_attributes(O):
            """Extract formatter attributes"""
            format_attributes = self._ttp_["utils"]["get_attributes"](
                "format_attributes({})".format(O)
            )
            self.attributes["format_attributes"] = {
                "args": format_attributes[0]["args"],
                "kwargs": format_attributes[0]["kwargs"],
            }

        def extract_path(O):
            self.attributes["path"] = [i.strip() for i in O.split(".")]

        def extract_headers(O):
            if isinstance(O, str):
                self.attributes["headers"] = [i.strip() for i in O.split(",")]
            else:
                self.attributes["headers"] = O

        def extract_condition(O):
            condition_attributes = self._ttp_["utils"]["get_attributes"](
                "condition({})".format(O)
            )
            self.attributes["condition"] = condition_attributes[0]["args"]

        def extract_functions(O):
            funcs = self._ttp_["utils"]["get_attributes"](O)
            for i in funcs:
                name = i["name"]
                if name in functions:
                    functions[name](i)
                elif name in self._ttp_["output"]:
                    self.funcs.append(i)
                else:
                    similar_funcs = self._ttp_["utils"]["guess"](
                        name, list(self._ttp_["output"].keys())
                    )
                    if similar_funcs:
                        log.error(
                            "output.extract_functions: unknown output function: '{}', most similar function(s) - {}".format(
                                name, ", ".join(similar_funcs)
                            )
                        )
                    else:
                        log.error(
                            'output.extract_functions: unknown output function: "{}"'.format(
                                name
                            )
                        )

        def extract_function(func_name, args_kwargs):
            attribs = self._ttp_["utils"]["get_attributes"](
                "{}({})".format(func_name, args_kwargs)
            )
            self.funcs.append(attribs[0])

        options = {
            "name": extract_name,
            "returner": extract_returner,
            "filename": extract_filename,
            "format_attributes": extract_format_attributes,
            "path": extract_path,
            "headers": extract_headers,
            "condition": extract_condition,
        }
        functions = {"functions": extract_functions}
        for attr_name, attributes in data.items():
            if attr_name.lower() in options:
                options[attr_name.lower()](attributes)
            elif attr_name.lower() in functions:
                functions[attr_name.lower()](attributes)
            elif attr_name in self._ttp_["output"]:
                extract_function(attr_name, attributes)
            else:
                self.attributes[attr_name] = attributes

    def run(self, data, macro=None):
        """
        Function to run outputter.

        :param data: (dict or list) data to run outputter for
        :param macro: (dict) dictionary of macro functions
        """
        marco = macro or {}
        self._ttp_["output_object"] = self
        if macro:
            self._ttp_["macro"] = macro
        format_type = self.attributes["format"]
        results = data
        # check condition to see if need to run this output
        if self.attributes.get("condition"):
            condition_var_name, condition_var_value = self.attributes["condition"]
            var_value = self.template_obj.vars.get(condition_var_name, "_undef_")
            if not var_value == condition_var_value:
                return data
        # run functions
        for item in self.funcs:
            func_name = item["name"]
            args = item.get("args", [])
            kwargs = item.get("kwargs", {})
            results = self._ttp_["output"][func_name](results, *args, **kwargs)
        # run formatters
        if format_type in self._ttp_["formatters"]:
            results = self._ttp_["formatters"][format_type](results, **self.attributes)
        else:
            log.warning(
                "output.run: unsupported formatter '{}', use one of: {}".format(
                    format_type, list(self._ttp_["formatters"].keys())
                )
            )
        # run returners
        for returner in self.attributes["returner"]:
            if returner in self._ttp_["returners"]:
                _ = self._ttp_["returners"][returner](results, **self.attributes)
            else:
                log.warning(
                    "output.run: unsupported returner '{}', use one of: {}".format(
                        returner, list(self._ttp_["returners"].keys())
                    )
                )
        # check if need to return processed data:
        if self.return_to_self is True:
            return results
        # return unmodified data otherwise
        return data

    def debug(self):
        from pprint import pformat

        text = "Output Object {}, Output name '{}' content:\n{}".format(
            self, self.name, pformat(vars(self), indent=4)
        )
        log.debug(text)


"""
==============================================================================
TTP LOGGING SETUP
==============================================================================
"""


def logging_config(LOG_LEVEL, LOG_FILE, _ttp_=None):
    _ttp_ = _ttp_ or {}
    valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if not LOG_LEVEL.upper() in valid_log_levels:
        return
    # if used as a CLI tool or sas a script - setup logging config using custom formatter
    if __name__ == "__main__" or _ttp_.get("_used_as_cli_tool_") == True:
        logging.basicConfig(
            format="%(asctime)s.%(msecs)d [TTP %(levelname)s] %(lineno)d; %(message)s",
            datefmt="%m/%d/%Y %I:%M:%S",
            level=LOG_LEVEL.upper(),
            filename=LOG_FILE,
            filemode="w",
        )
    # if used as a module - only set logs to requested level
    else:
        log.setLevel(LOG_LEVEL.upper())


"""
==============================================================================
TTP CLI PROGRAMM
==============================================================================
"""


def cli_tool():
    import argparse
    import time

    # form _ttp_ dictionary and pre-load it with all functions
    _ttp_ = lazy_import_functions()

    # use this to fix logging when used as a cli tool
    _ttp_["_used_as_cli_tool_"] = True

    # form argparser menu:
    description_text = """-d,  --data            Data files location
-dp, --data-prefix     Prefix to add to template inputs' urls
-t,  --template        OS path to templates file
-tn, --template-name   Name of the template in templates file
-o,  --outputter       Specify output format - yaml, json, raw, pprint
-ot, --out-template    Name of template to output results for
-l,  --logging         Set logging level - "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
-lf, --log-file        Path to save log file
-T,  --Timing          Print simple timing info
-s,  --structure       Final results structure - 'list' or 'dictionary'
-v,  --vars            Json string containing variables to add to TTP object
--one                  Parse using single process
--multi                Parse using multiple processes"""
    argparser = argparse.ArgumentParser(
        description="Template Text Parser, version {}".format(__version__),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    run_options = argparser.add_argument_group(description=description_text)
    run_options.add_argument(
        "--one", action="store_true", dest="ONE", default=False, help=argparse.SUPPRESS
    )
    run_options.add_argument(
        "--multi",
        action="store_true",
        dest="MULTI",
        default=False,
        help=argparse.SUPPRESS,
    )
    run_options.add_argument(
        "-T",
        "--Timing",
        action="store_true",
        dest="TIMING",
        default=False,
        help=argparse.SUPPRESS,
    )
    run_options.add_argument(
        "-d",
        "--data",
        action="store",
        dest="DATA",
        default="",
        type=str,
        help=argparse.SUPPRESS,
    )
    run_options.add_argument(
        "-dp",
        "--data-prefix",
        action="store",
        dest="data_prefix",
        default="",
        type=str,
        help=argparse.SUPPRESS,
    )
    run_options.add_argument(
        "-t",
        "--template",
        action="store",
        dest="TEMPLATE_FILE",
        default="",
        type=str,
        help=argparse.SUPPRESS,
    )
    run_options.add_argument(
        "-tn",
        "--template-name",
        action="store",
        dest="TEMPLATE_NAME",
        default="",
        type=str,
        help=argparse.SUPPRESS,
    )
    run_options.add_argument(
        "-o",
        "--outputter",
        action="store",
        dest="OUTPUTTER",
        default="",
        type=str,
        help=argparse.SUPPRESS,
    )
    run_options.add_argument(
        "-ot",
        "--out-template",
        action="store",
        dest="OUT_TEMPLATE",
        default="",
        type=str,
        help=argparse.SUPPRESS,
    )
    run_options.add_argument(
        "-l",
        "--logging",
        action="store",
        dest="LOG_LEVEL",
        default="WARNING",
        type=str,
        help=argparse.SUPPRESS,
    )
    run_options.add_argument(
        "-lf",
        "--log-file",
        action="store",
        dest="LOG_FILE",
        default=None,
        type=str,
        help=argparse.SUPPRESS,
    )
    run_options.add_argument(
        "-s",
        "--structure",
        action="store",
        dest="STRUCTURE",
        default="list",
        type=str,
        help=argparse.SUPPRESS,
    )
    run_options.add_argument(
        "-v",
        "--vars",
        action="store",
        dest="VARS",
        default="",
        type=str,
        help=argparse.SUPPRESS,
    )

    # extract argparser arguments:
    args = argparser.parse_args()
    TEMPLATE_FILE = args.TEMPLATE_FILE  # string, Template file
    TEMPLATE_NAME = args.TEMPLATE_NAME  # string, Template name in template file
    DATA = args.DATA  # string, OS path to data files to parse
    OUTPUTTER = args.OUTPUTTER  # string, set OUTPUTTER format
    TIMING = args.TIMING  # boolean, enabled timing
    BASE_PATH = args.data_prefix  # string, to add to templates' inputs urls
    ONE = args.ONE  # boolean to indicate if run in single process
    MULTI = args.MULTI  # boolean to indicate if run in multi process
    LOG_LEVEL = args.LOG_LEVEL  # level of logging
    LOG_FILE = args.LOG_FILE  # file to put the logs in
    STRUCTURE = args.STRUCTURE
    OUT_TEMPLATE = args.OUT_TEMPLATE
    VARS = args.VARS

    supporrted_cli_tool_outputters = ["json", "yaml", "raw", "pprint", ""]

    def timing(message):
        if TIMING:
            print(
                "{:<9} {:<25}; {} MByte of RAM in use".format(
                    round(time.time() - t0, 5),
                    message,
                    process.memory_info().rss / 1000000,
                )
            )

    # setup logging
    logging_config(LOG_LEVEL, LOG_FILE, _ttp_)

    if TIMING:
        t0 = time.time()
        import psutil

        process = psutil.Process(os.getpid())
    else:
        t0 = 0
    # extract vars
    ttp_vars = {}
    if VARS:
        from json import loads

        VARS = VARS.replace("'", '"')
        ttp_vars = loads(VARS)
        if not isinstance(ttp_vars, dict):
            log.error(
                "cli_tool: Error with -v/--vars argument, value type is '{}', value is '{}', expecting dictionary, exiting...".format(
                    type(ttp_vars), ttp_vars
                )
            )
            raise SystemExit()
    # create parser object
    parser_Obj = ttp(base_path=BASE_PATH, vars=ttp_vars)

    # load templates file
    if TEMPLATE_FILE:
        ttp_template = _ttp_["utils"]["load_files"](TEMPLATE_FILE, read=True)[0][1]
        if TEMPLATE_NAME:
            ttp_template = _ttp_["utils"]["load_struct"](
                text_data=ttp_template, load="python"
            )
            ttp_template = ttp_template[TEMPLATE_NAME]
    # add data and templates
    parser_Obj.add_template(template=ttp_template)
    if DATA:
        parser_Obj.set_input(data=DATA)
        timing("Data descriptors loaded")
    timing("Template(s) loaded")

    # parse data
    parser_Obj.parse(one=ONE, multi=MULTI)
    timing("Data parsing finished")

    # print data to screen
    if OUTPUTTER:
        if not OUT_TEMPLATE:
            OUT_TEMPLATE = []
        else:
            OUT_TEMPLATE = [i.strip() for i in OUT_TEMPLATE.split(",")]
        if not OUTPUTTER.lower() in supporrted_cli_tool_outputters:
            log.error(
                "ttp.cli: unsupported outputter '{}', supported: {}, will use 'json' outputter".format(
                    OUTPUTTER, ", ".join(supporrted_cli_tool_outputters)
                )
            )
            OUTPUTTER = "json"
        results = parser_Obj.result(structure=STRUCTURE, templates=OUT_TEMPLATE)
        print(_ttp_["formatters"][OUTPUTTER](results))
        timing("{} dumped".format(OUTPUTTER))
    timing("Done")


if __name__ == "__main__":
    cli_tool()
