Template Variables 
==================
   
ttp supports definition of custom variables using dedicated xml tags <v>, <vars> or <variables>. Withing this tags variables can be defined in various formats and loaded using one of supported loaders. Variables can also be defined in external text files using *include* attribute. 

Custom variables can be used in a number of places within the templates, primarily in match variable functions, to store data off the groups definitions.

Data can also be recorded in variables during parsing and referenced later to construct dynamic path or within variables functions.

Variable tag attributes
-----------------------

.. list-table::
   :widths: 10 90
   :header-rows: 1

   * - Attribute
     - Description
   * - `name`_   
     - String of dot-separated path items
   * - `load`_   
     - Indicates which loader to use to read tag data, default is *python*
   * - `include`_   
     - Specifies location of the file with variables data to load
   * - `key`_   
     - If csv loader used, *key* specifies column name to use as a key

Variable getters
----------------
	
TTP template variables also support a number of getters - functions targeted to get some information and assign it to variable.

.. list-table::
   :widths: 10 90
   :header-rows: 1

   * - Function
     - Description
   * - `gethostname`_   
     - this function tries to extract hostname out of source data prompts
   * - `getfilename`_   
     - returns a name of the source data
   * - `get_time`_   
     - returns current time
   * - `get_date`_   
     - returns current date
   * - `get_timestamp`_   
     - returns combination of current date and time
   * - `get_timestamp_ms`_   
     - returns combination of current date and time with milliseconds
   * - `get_timestamp_iso`_   
     - returns timestamp in ISO format in UTC timezone
   * - `get_time_ns`_   
     - returns current time in nanoseconds since Epoch
	 
load
------------------------------------------------------------------------------
``load="loader_name"``	

* loader_name (optional) - name of the loader to use to render supplied variables data, default is python.

Supported loaders:

* python - uses python *exec* method to load data structured in native Python formats
* yaml - relies on PyYAML to load YAML structured data
* json - used to load json formatted variables data
* ini - *configparser* Python standart module used to read variables from ini structured file
* csv - csv formatted data loaded with Python *csv* standart library module

**Example**

Template

.. code-block:: html

    <input load="text">
    interface GigabitEthernet1/1
     ip address 192.168.123.1 255.255.255.0
    !
    </input>
    
    <!--Python formatted variables data-->
    <vars name="vars">
    python_domains = ['.lab.local', '.static.on.net', '.abc']
    </vars>
    
    <!--YAML formatted variables data-->
    <vars load="yaml" name="vars">
    yaml_domains:
      - '.lab.local'
      - '.static.on.net'
      - '.abc'
    </vars>
    
    <!--Json formatted variables data-->
    <vars load="json" name="vars">
    {
        "json_domains": [
            ".lab.local",
            ".static.on.net",
            ".abc"
        ]
    }
    </vars>
    
    <!--INI formatted variables data-->
    <variables load="ini" name="vars">
    [ini_domains]
    1: '.lab.local'
    2: '.static.on.net'
    3: '.abc'
    </variables>
    
    <!--CSV formatted variables data-->
    <variables load="csv" name="vars.csv">
    id, domain
    1,  .lab.local
    2,  .static.on.net
    3,  .abc
    </variables>
    
    <group name="interfaces">
    interface {{ interface }}
     ip address {{ ip }} {{ mask }}	
    </group>
	
Result as displayed by Python pprint outputter

.. code-block::

    [   {   'interfaces': {   'interface': 'GigabitEthernet1/1',
                              'ip': '192.168.123.1',
                              'mask': '255.255.255.0'},
            'vars': {   'csv_data': {   '1': {' domain': '  .lab.local'},
                                        '2': {' domain': '  .static.on.net'},
                                        '3': {' domain': '  .abc'}},
                        'ini_data': {   '1': "'.lab.local'",
                                        '2': "'.static.on.net'",
                                        '3': "'.abc'"},
                        'json_data': ['.lab.local', '.static.on.net', '.abc'],
                        'python_data': ['.lab.local', '.static.on.net', '.abc'],
                        'yaml_data': ['.lab.local', '.static.on.net', '.abc']}}]
						
YAML, JSON and Python formats are suitalble for encoding any arbitrary data and loaded as is.

INI structured data loaded into python nested dictionary, where top level keys represent ini section names each with nested dictionary of variables. 

CSV data also transformed into dictionary using first column values to fill in dictionary keys, unless specified otherwise using *key* attribute

include
------------------------------------------------------------------------------
``include="path"``	

* path - absolute OS path to text file with variables data.

name
------------------------------------------------------------------------------
``name="variables_tag_name"``

* variables_tag_name - dot separated string that specifies path in results structure where variables should be saved, by default it is empty, meaning variables will not be saved in results. Path string follows all the same rules as for group name attribute, for instance *{{ var_name }}* can be used to dynamically form path or "*" and "**" can indicate what type of structure to use for child - list or dictionary.

**Example**

Template

.. code-block:: html

    <vars name="vars.info**.{{ hostname }}">
    # path will be formaed dynamically
    hostname='switch-1'
    serial='AS4FCVG456'
    model='WS-3560-PS'
    </vars>
    
    <vars name="vars.ip*">
    # variables that will be saved under {'vars': {'ip': []}} path
    IP="Undefined"
    MASK="255.255.255.255"
    </vars>
    
    <vars load="yaml">
    # set of vars in yaml format that will not be included in results
    intf_mode: "layer3"
    </vars>
    
    <input load="text">
    interface Vlan777
     description Management
     ip address 192.168.0.1 24
     vrf MGMT
    !
    </input>
    
    <group name="interfaces">
    interface {{ interface }}
     description {{ description }}
     ip address {{ ip | record("IP") }} {{ mask }}
     vrf {{ vrf }}
     {{ mode | set("intf_mode") }}
    </group>

Result

.. code-block::

    [
        {
            "interfaces": {
                "description": "Management",
                "interface": "Vlan777",
                "ip": "192.168.0.1",
                "mask": "24",
                "mode": "layer3",
                "vrf": "MGMT"
            },
            "vars": {
                "info": {
                    "switch-1": {
                        "model": "WS-3560-PS",
                        "serial": "AS4FCVG456"
                    }
                },
                "ip": [
                    {
                        "IP": "192.168.0.1",
                        "MASK": "255.255.255.255"
                    }
                ]
            }
        }
    ]
	
key
------------------------------------------------------------------------------
``key="column_name"``	

* column_name - optional string attribute that can be used by csv loader to use given column values as a key for dictionary constructed out of csv data.

gethostname
------------------------------------------------------------------------------
``var_name="gethostname"``	

Using this getter function TTP tries to extract device's hostname out of it prompt. Supported prompts are:

* juniper such as ``some.user@hostname>``
* huawei such as ``<hostname>``
* Cisco IOS Exec such as ``hostname>``
* Cisco IOS XR such as ``RP/0/4/CPU0:hostname#``
* Cisco IOS Priviledged such as ``hostname#``
* Fortigate such as ``hostname (context) #``

**Example**

Template::

    <input load="text">
    switch1#show run int
    interface GigabitEthernet3/11
     description input_1_data
    </input>
    
    <vars name="vars">
    hostname_var = "gethostname"
    </vars>
    
    <group name="interfaces">
    interface {{ interface }}
     description {{ description }}
    </group>

Result::

    [
        {
            "interfaces": {
                "description": "input_1_data",
                "interface": "GigabitEthernet3/11"
            },
            "vars": {
                "hostname_var": "switch1"
            }
        }
    ]

getfilename
------------------------------------------------------------------------------
``var_name="getfilename"``	

This function returns the name of input data file if data was loaded from file, if data was loaded from text it will return "text_data".

get_time
------------------------------------------------------------------------------
``var_name="get_time"``	

Returns current time in ``%H:%M:%S`` format.

get_date
------------------------------------------------------------------------------
``var_name="get_date"``	

Returns current date in ``%Y-%m-%d`` format.

get_timestamp
------------------------------------------------------------------------------
``var_name="get_timestamp"``	

Returns current timestamp in ``%Y-%m-%d %H:%M:%S`` format.

get_timestamp_ms
------------------------------------------------------------------------------
``var_name="get_timestamp_ms"``	

Returns current timestamp but with milliseconds precision in a format of ``%Y-%m-%d %H:%M:%S.%ms``

get_timestamp_iso
------------------------------------------------------------------------------
``var_name="get_timestamp_iso"``	

Returns current timestamp in ISO format with UTC timezone e.g. ``2020-06-30T11:07:01.212349+00:00``. Uses python datetime function to produce timestamp.

get_time_ns
------------------------------------------------------------------------------
``var_name="get_time_ns"``	

This function uses time.time_ns method to return current time in nanoseconds since Epoch