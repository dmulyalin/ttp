Attributes
====================

There are a number of attributes supported by input tag, these attributes help to define input behavior and how data should be loaded and parsed.

Additionally input tag text payload can contain structured data, that data can be retrieved using ``get_input_load`` method. Input tag ``load`` attribute instructs how to load that data. For instance, if tag text structured in yaml format, yaml loader can be used to load it in Python data structure. 

Attributes in input tag and attributes loaded from input tag text are combined in single structure if both are dictionaries, as a result, most of the attributes can be specified in either way.

.. list-table:: 
   :widths: 10 90
   :header-rows: 1

   * - Attribute
     - Description
   * - `name`_   
     - Uniquely identifies input within template
   * - `groups`_   
     - comma-separated list of group(s) that should be used to parse input data
   * - `load`_   
     - loader name that should be used to load text data from input tag
   * - `url`_   
     - single or list of urls of data location
   * - `extensions`_   
     - single or list of file extensions to load, e.g. "txt" or "log" or "conf"
   * - `filters`_   
     - single or list of regular expression  to filter file names
	 
name
------------------------------------------------------------------------
``name="string"``

* string (optional) - name of the input to reference in group *input* attribute. Default value is "Default_Input" and used internally to store set of data that should be parsed by all groups.

groups
------------------------------------------------------------------------
``groups="group1, group2, ... , groupN"``

* groupN (optional) - comma separated string of group names that should be used to parse given input data. Default value is ``all``.

TTP makes a list of groups for each input that should parse that input's data following these logic:

* if input's ``groups`` attribute is ``all`` - input data will be parsed by each group that does not has ``input`` attribute defined
* if input's ``groups`` given and not ``all`` - only specified groups will parse this input's data. However, if group has ``input`` attribute defined, additional check done as per below note

.. note:: Group tag :ref:`Groups/Attributes:input` attribute can reference inputs' names or OS path to files and considered to be more specific. For example, when several groups in the template have identical ``name`` attribute, referencing these groups by name in input tag ``groups`` attribute will result in input data will be parsed by all the groups with that name, on the other hand, if input name referenced in group's tag ``input`` attribute, data of this input will only be parsed by this group even if several group have the same name.

load
------------------------------------------------------------------------
``load="loader_name"``

* loader_name - name of the loader that should be used to load input tag text data, supported values are ``python, yaml, json or text``, if text used as a loader, text data within input tag itself used as an input data and parsed by a set of given groups or by all groups.

**Example**

Below template contains input with text data that should be parsed, that is useful for testing purposes or for small data sets.

Template::

    <input name="test1" load="text" groups="interfaces.trunks">
    interface GigabitEthernet3/3
     switchport trunk allowed vlan add 138,166-173 
    !
    interface GigabitEthernet3/4
     switchport trunk allowed vlan add 100-105
    !
    interface GigabitEthernet3/5
     switchport trunk allowed vlan add 459,531,704-707
    </input>
    
    <group name="interfaces.trunks">
    interface {{ interface }}
     switchport trunk allowed vlan add {{ trunk_vlans }}
    </group>

Result::

    [
        {
            "interfaces": {
                "trunks": [
                    {
                        "interface": "GigabitEthernet3/3",
                        "trunk_vlans": "138,166-173"
                    },
                    {
                        "interface": "GigabitEthernet3/4",
                        "trunk_vlans": "100-105"
                    },
                    {
                        "interface": "GigabitEthernet3/5",
                        "trunk_vlans": "459,531,704-707"
                    }
                ]
            }
        }
    ]
     
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