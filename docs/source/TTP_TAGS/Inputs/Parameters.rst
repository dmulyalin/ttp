Input parameters
================

Apart from input attributes specified in <input> tag, text payload of <input> tag can be used to pass additional parameters. These parameters is a key value pairs and serve to provide information that should be used during input data loading. Input tag `load`_ attribute can be used to specify which loader to use to load data in tag's text, e.g. if data structured in yaml format, yaml loader can be used to convert it in Python data structure.

.. list-table:: 
   :widths: 10 90
   :header-rows: 1

   * - Parameter
     - Description
   * - `url`_   
     - Single url string or list of urls of input data location 
   * - `extensions`_   
     - Extensions of files to load input data from, e.g. "txt" or "log" or "conf"
   * - `filters`_   
     - Regular expression or list of regexes to use to filter input data files based on their names
     
url
------------------------------------------------------------------------
``url="url-1"`` or ``url=["url-1", "url-2", ... , "url-N"]``

* url-N - string or list of strings that contains absolute or relative (if base path provided) OS path to file or to directory of file(s) that needs to be parsed.
     
extensions
------------------------------------------------------------------------
``extensions="extension-1"`` or ``extensions=["extension-1", "extension-2", ... , "extension-N"]``

* extension-N - string or list of strings that contains file extensions that needs to be parsed e.g. txt, log, conf etc. In case if `url`_ is OS path to directory and not single file, ttp will use this strings to check if file names ends with one of given extensions, if so, file will be loaded and skipped otherwise.

filters
------------------------------------------------------------------------
``filters="regex-1"`` or ``filters=["regex-1", "regex-2", ... , "regex-N"]``

* regex-N - string or list of strings that contains regular expressions. If `url`_ is OS path to directory and not single file, ttp will use this strings to run re search against file names to load only files with names that matched by at least one regex.