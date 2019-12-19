Input parameters
================

Apart from input attributes specified in <input> tag, text payload of <input> tag can be used to pass additional parameters. 

These parameters can be arbitrary key value pairs and can be used to provide information for input data loading. These parameters can be retrieved from TTP object using ``get_input_load`` method.

Input tag ``load`` attribute can be used to specify which loader to use to load data in tag's text, e.g. if data structured in yaml format, yaml loader can be used to convert it in Python data structure.

Below are the parameters that recognized by TTP itself and can be used to load data for processing from Operating System absolute or relative path location, filtering it through defined constraints.

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

* url-N - string or list of strings that contains absolute or relative OS path to file or to directory of file(s) that needs to be parsed.

Few notes on relative path:

* if template tag ``base_path`` attribute provide, base_path value used to extend relative path - appended to relative path of each url
* if no template tag ``base_path`` attribute provided, in case if url parameter contains relative path, this path will be extended in relation to the folder where TTP invoked

TTP uses Python built-in OS module to load input files. Examples of relative path: ``./relative/path/`` or ``../relative/path/`` or ``relative/path/`` - any path that OS module considers as a relative path.

**Example-1**

Template tag contains ``base_path`` attribute.

Template::

    <template base_path="C:/base/path/to/">
    <input load="yaml">
    url: "./Data/Inputs/dataset_1/"
    </input>
    
    <group name="interfaces">
    interface {{ interface }}
      ip address {{ ip  }}/{{ mask }}
    </group>
    </template>
	
After combining base path and provided url, TTP will use ``C:/base/path/to/Data/Inputs/dataset_1/`` to load input data files.

**Example-2**

No ``base_path`` attribute.

Template::

    <input load="yaml">
    url: "./Data/Inputs/dataset_1/"
    </input>
    
    <group name="interfaces">
    interface {{ interface }}
      ip address {{ ip  }}/{{ mask }}
    </group>

In this case TTP will search for data files using relative path ``./Data/Inputs/dataset_1/``, extending it in relation to current directory, directory where TTP was executed.
     
extensions
------------------------------------------------------------------------
``extensions="extension-1"`` or ``extensions=["extension-1", "extension-2", ... , "extension-N"]``

* extension-N - string or list of strings that contains file extensions that needs to be parsed e.g. txt, log, conf etc. In case if `url`_ is OS path to directory and not single file, ttp will use this strings to check if file names ends with one of given extensions, if so, file will be loaded and skipped otherwise.

filters
------------------------------------------------------------------------
``filters="regex-1"`` or ``filters=["regex-1", "regex-2", ... , "regex-N"]``

* regex-N - string or list of strings that contains regular expressions. If `url`_ is OS path to directory and not single file, ttp will use this strings to run re search against file names to load only files with names that matched by at least one regex.