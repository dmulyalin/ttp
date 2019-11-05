Attributes
==========

There are a number of attributes that outputs system can use. Some attributes can be specific to output itself (name, description), others can be used by formatters or returners. 

.. list-table::
   :widths: 10 90
   :header-rows: 1

   * - Name
     - Description
   * - `name`_ 
     - name of the output, can be referenced in group *output* attribute
   * - `description`_ 
     - attribute to contain description of outputter
   * - `load`_ 
     - name of the loader to use to load output tag text
   * - `returner`_ 
     - returner to use to return data e.g. self, file, terminal
   * - `format`_ 
     - formatter to use to format results        

name
******************************************************************************
``name="output_name"``

Name of the output, optional attribute, can be used to reference it in groups :ref:`Groups/Attributes:output` attribute, in that case that output will become group specific and will only process results for this group. 

description
******************************************************************************
``name="descrition_string"``

descrition_string, optional string that contains output description or notes, can serve documentation purposes.

load
******************************************************************************
``load="loader_name"``    

Name of the loader to use to render supplied output tag text data, default is python.

Supported loaders:

* python - uses python `exec <https://docs.python.org/3/library/functions.html#exec>`_ method to load data structured in native Python formats
* yaml - relies on `PyYAML <https://pyyaml.org/>`_ to load YAML structured data
* json - used to load JSON formatted variables data
* ini - `configparser <https://docs.python.org/3/library/configparser.html>`_ Python standard module used to read variables from ini structured file
* csv - csv formatted data loaded with Python *csv* standard library module

If load is csv, first column by default will be used to create lookup dictionary, it is possible to supply :ref:`TTP_TAGS/Outputs/Formatters:key` with column name that should be used as a keys for row data. If any other type of load provided e.g. python or yaml, that data must have a dictionary structure, there keys will be compared against match result and on success data associated with given key will be included in results.
     
returner
******************************************************************************
``returner=returner_name"``    

Name of the returner to use to return results.

format
******************************************************************************
``format=formatter_name"``    

Name of the formatter to use to format results.