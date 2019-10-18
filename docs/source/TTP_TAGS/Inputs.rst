Inputs
======
   
Inputs can be used to specify data location and how it should be loaded or filtered. Inputs can be attached to groups for parsing, for instance this particular input data should be parsed by this set of groups only. That can help to increase the overall performance as only data belonging to particular group will be parsed. 

.. note:: Order of inputs preserved as internally they represented using OrderedDict object, that can be useful if data produced by first input needs to bused by other inputs.

Assuming we have this folders structure to store data that needs to be parsed::

    /my/base/path/
             |-Data/
               |-Inputs/
                 |- data-1/
                 |---- sw-1.conf
                 |---- sw-1.txt
                 |- data-2/
                 |---- sw-2.txt
                 |---- sw3.txt                       

Where content::

    [sw-1.conf]
    interface GigabitEthernet3/7
     switchport access vlan 700
    !
    interface GigabitEthernet3/8
     switchport access vlan 800
    !

    [sw-1.txt]
    interface GigabitEthernet3/2
     switchport access vlan 500
    !
    interface GigabitEthernet3/3
     switchport access vlan 600
    !
    
    [sw-2.txt]
    interface Vlan221
      ip address 10.8.14.130/25
    
    interface Vlan223
      ip address 10.10.15.130/25
    
    [sw3.txt]
    interface Vlan220
      ip address 10.9.14.130/24
    
    interface Vlan230
      ip address 10.11.15.130/25

Template below uses inputs in such a way that for "data-1" folder only files that have ".txt" extension will be parsed by group "interfaces1", for input named "dataset-2" only files with names matching "sw\-\d.*" regular expression will be parsed by "interfaces2" group. In addition, base path provided that will be appended to each url within *url* input parameter. Tag text for input "dataset-1" structured using YAML representation, while "dataset-2" uses python language definition.

As a result of inputs filtering, only "sw-1.txt" will be processed by "dataset-1" input because it is the only file that has ".txt" extension, only  "sw-2.txt" will be processed by input "dataset-2" because "sw3.txt" not matched by "sw\-\d.*" regular expression.

Template::

    <template base_path="/my/base/path/">
    <input name="dataset-1" load="yaml" groups="interfaces1">
    url: "/Data/Inputs/data-1/"
    extensions: ["txt"]
    </input>
    
    <input name="dataset-2" load="python" groups="interfaces2">
    url = ["/Data/Inputs/data-2/"]
    filters = ["sw\-\d.*"]
    </input>
    
    <group name="interfaces1">
    interface {{ interface }}
     switchport access vlan {{ access_vlan }}
    </group>
    
    <group name="interfaces2">
    interface {{ interface }}
      ip address {{ ip  }}/{{ mask }}
    </group>
    </template>
    
And result would be::

    [
        {
            "interfaces1": [
                {
                    "access_vlan": "500",
                    "interface": "GigabitEthernet3/2"
                },
                {
                    "access_vlan": "600",
                    "interface": "GigabitEthernet3/3"
                }
            ]
        },
        {
            "interfaces2": [
                {
                    "interface": "Vlan221",
                    "ip": "10.8.14.130",
                    "mask": "25"
                },
                {
                    "interface": "Vlan223",
                    "ip": "10.10.15.130",
                    "mask": "25"
                }
            ]
        }
    ]


Input tag attributes
-----------------------------------------------------------------------------

There are a number of attributes can be specified in input tag, these attributes help to define input behavior and how data should be loaded and parsed.

.. list-table:: 
   :widths: 10 90
   :header-rows: 1

   * - Attribute
     - Description
   * - `name`_   
     - Uniquely identifies input within template
   * - `groups`_   
     - Specifies group(s) that should be used to parse input data
   * - `load`_   
     - Identifies loader that should be used to load text data for input tag itself
   * - `preference`_   
     - specify preference on how to handle inputs' groups and groups' input
	 
name
******************************************************************************
``name="string"``

* string (optional) - name of the input to reference in group *input* attribute. Default value is "Default_Input" and used internally to store set of data that should be parsed by all groups.

groups
******************************************************************************
``groups="group1, group2, ... , groupN"``

* groupN (optional) - Default value is "all", comma separated string of group names that should be used to parse given input data. Default value is "all" - input data will be parsed by each group. 

.. note:: Group tag :ref:`Groups/Attributes:input` attribute can be used to reference inputs' names or OS path to files, it is considered to be more specific, for example when several groups in the  template have identical *name* attribute, referencing these groups by name in input tag *groups* attribute will result in input data to be parsed by all the groups with that name, on the other hand, if input name referenced in group tag *input* attribute, data of this input will only be parsed by this group even if several group have the same name.

load
******************************************************************************
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
    
preference
******************************************************************************
``preference="merge|group_inputs|input_groups"``

TBD

Input tag functions
-----------------------------------------------------------------------------

Input tag support functions to pre-process data.

.. list-table:: 
   :widths: 10 90
   :header-rows: 1

   * - Attribute
     - Description
   * - `functions`_   
     - String with functions defined int it
   * - `commands`_   
     - Comma separated list of commands output to extract from text data
   * - `test`_   
     - Test function to verify input function handling
	 
functions
******************************************************************************
``functions="function1('attr1', 'attr2') | function2"``	 

TBD

commands
******************************************************************************
``commands="command1, command2, ... , commandN"``	 

TBD

test
******************************************************************************
``test=""``	 

TBD

Input parameters
------------------------------------------------------------------------------

Apart from input attributes specified in <input> tag, text payload of <input> tag can be used to pass additional parameters. These parameters is a key value pairs and serve to provide information that should be used during input data loading. Input tag `load`_ attribute can be used to specify which loader to use to parse data in tag's text, e.g. if data structured in yaml format, yaml loader can be used to convert it in Python data structure.

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
******************************************************************************
``url="url-1"`` or ``url=["url-1", "url-2", ... , "url-N"]``

* url-N - string or list of strings that contains absolute or relative (if base path provided) OS path to file or to directory of file(s) that needs to be parsed.
     
extensions
******************************************************************************
``extensions="extension-1"`` or ``extensions=["extension-1", "extension-2", ... , "extension-N"]``

* extension-N - string or list of strings that contains file extensions that needs to be parsed e.g. txt, log, conf etc. In case if `url`_ is OS path to directory and not single file, ttp will use this strings to check if file names ends with one of given extensions, if so, file will be loaded and skipped otherwise.

filters
******************************************************************************
``filters="regex-1"`` or ``filters=["regex-1", "regex-2", ... , "regex-N"]``

* regex-N - string or list of strings that contains regular expressions. If `url`_ is OS path to directory and not single file, ttp will use this strings to run re search against file names to load only files with names that matched by at least one regex.