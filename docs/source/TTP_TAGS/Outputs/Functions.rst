Functions
=========

Output system provides support for a number of functions. Functions help to process overall parsing results with intention to modify, check or filter them in certain way.

.. list-table::
   :widths: 10 90
   :header-rows: 1

   * - Name
     - Description
   * - `is_equal`_ 
     - checks if results equal to structure loaded from the output tag text 
   * - `set_data`_
     - insert arbitrary data to results at given path, replacing any existing results
   * - `dict_to_list`_
     - transforms dictionary to list of dictionaries at given path     
   * - `macro`_
     - passes results through macro function
     
is_equal
******************************************************************************
``functions="is_equal"``

Function is_equal load output tag text data into python structure (list, dictionary etc.) using given loader and performs comparison with parsing results. is equal returns a dictionary of three elements::

    {
        "is_equal": true|false,
        "output_description": "output description as set in description attribute",
        "output_name": "name of the output"
    } 
    
This function use-cases are various tests or compliance checks, one can construct a set of template groups to produce results, these results can be compared with predefined structures to check if they are matching, based on comparison a conclusion can be made such as whether or not source data satisfies certain criteria.

**Example**

Template::

    <input load="text">
    interface Loopback0
     ip address 192.168.0.113/24
    !
    interface Vlan778
     ip address 2002::fd37/124
    !
    </input>
    
    <group name="interfaces">
    interface {{ interface }}
     ip address {{ ip }}/{{ mask }}
    </group>
    
    <output
    name="test output 1"
    load="json"
    description="test results equality"
    functions="is_equal"
    >
    [
        {
            "interfaces": [
                {
                    "interface": "Loopback0",
                    "ip": "192.168.0.113",
                    "mask": "24"
                },
                {
                    "interface": "Vlan778",
                    "ip": "2002::fd37",
                    "mask": "124"
                }
            ]
        }
    ]
    </output>
    
Results::

    {
        "is_equal": true,
        "output_description": "test results equality",
        "output_name": "test output 1"
    }
  
set_data
******************************************************************************

TBD
  
dict_to_list
******************************************************************************

TBD

macro
******************************************************************************
``macro="func_name"`` or ``functions="macro('func_name1') | macro('func_name2')"``

Output macro function allows to process whole results using custom function(s) defined within <macro> tag.

**Example**

Template::

    <input load="text">
    interface Vlan778
     ip address 2002::fd37::91/124
    !
    interface Loopback991
     ip address 192.168.0.1/32
    !
    </input>
    
    <macro>
    def check_svi(data):
        # data is a list of lists:
        # [[{'interface': 'Vlan778', 'ip': '2002::fd37::91', 'mask': '124'}, 
        #   {'interface': 'Loopback991', 'ip': '192.168.0.1', 'mask': '32'}]]
        for item in data[0]:
            if "Vlan" in item["interface"]:
                item["is_svi"] = True
            else:
                item["is_svi"] = False
    </macro>
    
    <group>
    interface {{ interface }}
     ip address {{ ip }}/{{ mask }}
    </group>
    
    <output macro="check_svi"/>
	
Results::

    [
        [
            {
                "interface": "Vlan778",
                "ip": "2002::fd37::91",
                "is_svi": true,
                "mask": "124"
            },
            {
                "interface": "Loopback991",
                "ip": "192.168.0.1",
                "is_svi": false,
                "mask": "32"
            }
        ]
    ]