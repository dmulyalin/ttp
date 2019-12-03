Lookups
=======
   
Lookups tag allows to define a lookup table that will be transformed into lookup dictionary, dictionary that can be used to lookup values to include them into parsing results. Lookup table can be called from match variable using *lookup* function.

.. list-table:: lookup tag attributes
   :widths: 10 90
   :header-rows: 1

   * - Name
     - Description
   * - `name`_ 
     - name of the lookup table to reference in match variable *lookup* function
   * - `load`_ 
     - name of the loader to use to load lookup text
   * - `include`_   
     - specifies location of the file to load lookup table from
   * - `key`_   
     - If csv loader used, *key* specifies column name to use as a key

name
------------------------------------------------------------------------------
``name="lookup_table_name"``

* lookup_table_name(mandatory) - string to use as a name for lookup table, that is required attribute without it lookup data will not be loaded.
     
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

If load is csv, first column by default will be used to create lookup dictionary, it is possible to supply `key`_ with column name that should be used as a keys for row data. If any other type of load provided e.g. python or yaml, that data must have a dictionary structure, there keys will be compared against match result and on success data associated with given key will be included in results.

include
------------------------------------------------------------------------------
``include="path"``    

* path - absolute OS path to text file with lookup table data.

key
------------------------------------------------------------------------------
``key="column_name"``    

* column_name - optional string attribute that can be used by csv loader to use given column values as a key for dictionary constructed out of csv data.


CSV Example
------------------------------------------------------------------------------

Template::

    <lookup name="aux_csv" load="csv">
    ASN,as_name,as_description,prefix_num
    65100,Subs,Private ASN,734
    65200,Privs,Undef ASN,121
    </lookup>
    
    <input load="text">
    router bgp 65100
    </input>
    
    <group name="bgp_config">
    router bgp {{ bgp_as | lookup("aux_csv", add_field="as_details") }}
    </group> 

Result::

    [
        {
            "bgp_config": {
                "as_details": {
                    "as_description": "Private ASN",
                    "as_name": "Subs",
                    "prefix_num": "734"
                },
                "bgp_as": "65100"
            }
        }
    ]
    
Because no *key* attribute provided, csv data was loaded in python dictionary using first column - ASN - as a key. This is the resulted lookup dictionary::

    { 
      "65100": {
            "as_name": "Subs",
            "as_description" : "Private ASN",
            "prefix_num": "734"
        },
      "65200": {
            "as_name": "Privs",
            "as_description" : "Undef ASN",
            "prefix_num": "121"
        }
    }
    
If *key* will be set to "as_name", lookup dictionary will become::

    { 
      "Subs": {
            "ASN": "65100",
            "as_description" : "Private ASN",
            "prefix_num": "734"
        },
      "Privs": {
            "ASN": "65200",
            "as_description" : "Undef ASN",
            "prefix_num": "121"
        }
    }
    
INI Example
------------------------------------------------------------------------------

If table provided in INI format, data will be transformed into dictionary with top key equal to lookup table names, next level of keys will correspond to INI sections which will nest a dictionary of actual key-value pairs. For instance in below template with lookup name "location", INI data will be loaded into this python dictionary structure:: 

    { "locations": 
        { "cities": {
            "-mel-": "7 Name St, Suburb A, Melbourne, Postal Code",
            "-bri-" : "8 Name St, Suburb B, Brisbane, Postal Code"
        }
    }}
    
As a result dictionary data to use for lookup can be referenced using "locations.cities" string in lookup/rlookup match variables function.

Template::

    <input load="text">
    router bgp 65100
      neighbor 10.145.1.9
        description vic-mel-core1
      !
      neighbor 192.168.101.1
        description qld-bri-core1
    </input>

    <lookup name="locations" load="ini">
    [cities]
    -mel- : 7 Name St, Suburb A, Melbourne, Postal Code
    -bri- : 8 Name St, Suburb B, Brisbane, Postal Code
    </lookup>
    
    <group name="bgp_config">
    router bgp {{ bgp_as }}
     <group name="peers">
      neighbor {{ peer }}
        description {{ description | rlookup('locations.cities', add_field='location') }}
     </group>
    </group> 
    
Result::

    [
        {
            "bgp_config": {
                "bgp_as": "65100",
                "peers": [
                    {
                        "description": "vic-mel-core1",
                        "location": "7 Name St, Suburb A, Melbourne, Postal Code",
                        "peer": "10.145.1.9"
                    },
                    {
                        "description": "qld-bri-core1",
                        "location": "8 Name St, Suburb B, Brisbane, Postal Code",
                        "peer": "192.168.101.1"
                    }
                ]
            }
        }
    ]
    
YAML Example
------------------------------------------------------------------------------

YAML data must be structured as a dictionary, once loaded it will correspond to python dictionary that will be used to lookup values.

Template::

    <lookup name="yaml_look" load="yaml">
    '65100':
      as_description: Private ASN
      as_name: Subs
      prefix_num: '734'
    '65101':
      as_description: Cust-1 ASN
      as_name: Cust1
      prefix_num: '156'
    </lookup>
    
    <input load="text">
    router bgp 65100
    </input>
    
    <group name="bgp_config">
    router bgp {{ bgp_as | lookup("yaml_look", add_field="as_details") }}
    </group> 
    
Result::

    [
        {
            "bgp_config": {
                "as_details": {
                    "as_description": "Private ASN",
                    "as_name": "Subs",
                    "prefix_num": "734"
                },
                "bgp_as": "65100"
            }
        }
    ]  