Attributes
==========

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

load
------------------------------------------------------------------------------
``load="loader_name"``

* loader_name (optional) - name of the loader to use to render supplied variables data, default is python.

Supported loaders:

* python - uses python *exec* method to load data structured in native Python formats
* yaml - relies on PyYAML to load YAML structured data
* json - used to load json formatted variables data
* ini - *configparser* Python standard module used to read variables from ini structured file
* csv - csv formatted data loaded with Python *csv* standard library module

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

YAML, JSON and Python formats are suitable for encoding any arbitrary data and loaded as is.

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
