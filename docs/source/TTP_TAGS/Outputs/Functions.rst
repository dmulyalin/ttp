Functions
=========

Output system provides support for a number of functions. Functions help to process overall parsing results with intention to modify, check or filter them in certain way.

.. list-table::
   :widths: 20 80
   :header-rows: 1

   * - Name
     - Description
   * - `is_equal`_ 
     - checks if results equal to structure loaded from the output tag text 
   * - `set_data`_
     - insert arbitrary data to results at given path, replacing any existing results
   * - `dict_to_list`_
     - transforms dictionary to list of dictionaries at given path     
   * - `traverse`_
     - returns data at given path location of results tree
   * - `macro`_
     - passes results through macro function
   * - `output functions`_ 
     - pipe separated list of functions to run results through  
   * - `deepdiff`_ 
     - function to compare result structures
     
is_equal
------------------------------------------------------------
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
------------------------------------------------------------

This function not yet tested and not available for use, listed here as a placeholder.
  
dict_to_list
------------------------------------------------------------
``dict_to_list="key_name='key', path='dot.separated.path'"``

* key_name - string, name of the key to use to assign previous key as a value
* path - string, dot separated path to data that need to be transformed

This functions help to flatten dictionary data by converting it to list e.g. if data is::

    {"Fa0" : {"admin": "administratively down"}, "Ge0/1": {"access_vlan": "24"}}

and key_name="interface", dit_to_list function will return this list::

    [ {"admin": "administratively down", "interface": "Fa0"},
      {"access_vlan": "24", "interface": "Ge0/1"} ]

Primary usecase is to produce list data out of dictionary, this function used internally by table output formatter for that purpose.

**Example**

Template::

    <input load="text">
    some.user@router-fw-host> show configuration interfaces | display set 
    set interfaces ge-0/0/11 unit 0 description "SomeDescription glob1"
    set interfaces ge-0/0/11 unit 0 family inet address 10.0.40.121/31
    set interfaces lo0 unit 0 description "Routing Loopback"
    set interfaces lo0 unit 0 family inet address 10.6.4.4/32
    </input>
    
    <group name="{{ interface }}{{ unit }}**" method="table">
    set interfaces {{ interface }} unit {{ unit }} family inet address {{ ip }}
    set interfaces {{ interface }} unit {{ unit }} description "{{ description | ORPHRASE }}"
    </group>
    
    <output dict_to_list="key_name='interface'"/>

Result::

    [
        [
            [
                {
                    "description": "SomeDescription glob1",
                    "interface": "ge-0/0/110",
                    "ip": "10.0.40.121/31"
                },
                {
                    "description": "Routing Loopback",
                    "interface": "lo00",
                    "ip": "10.6.4.4/32"
                }
            ]
        ]
    ]

As a comparison example, here is how results would look like without running them through dict_to_list function::

    [
        [
            {
                "ge-0/0/110": {
                    "description": "SomeDescription glob1",
                    "ip": "10.0.40.121/31"
                },
                "lo00": {
                    "description": "Routing Loopback",
                    "ip": "10.6.4.4/32"
                }
            }
        ]
    ]

traverse
------------------------------------------------------------
``traverse="path='dot.separated.path'"``

* path - string, dot separated path to data that need to be transformed

traverse function walks results tree up to the level of given path and return data at that location.

**Example**

Template::

    <input load="text">
    some.user@router-fw-host> show configuration interfaces | display set 
    set interfaces ge-0/0/11 unit 0 description "SomeDescription glob1"
    set interfaces ge-0/0/11 unit 0 family inet address 10.0.40.121/31
    set interfaces lo0 unit 0 description "Routing Loopback"
    set interfaces lo0 unit 0 family inet address 10.6.4.4/32
    </input>
    
    <group name="my.long.path.{{ interface }}{{ unit }}**" method="table">
    set interfaces {{ interface }} unit {{ unit }} family inet address {{ ip }}
    set interfaces {{ interface }} unit {{ unit }} description "{{ description | ORPHRASE }}"
    </group>
    
    <output traverse="path='my.long.path'"/>

Result::

    [
        [
            {
                "ge-0/0/110": {
                    "description": "SomeDescription glob1",
                    "ip": "10.0.40.121/31"
                },
                "lo00": {
                    "description": "Routing Loopback",
                    "ip": "10.6.4.4/32"
                }
            }
        ]
    ]
    
For comparison, without traverse TTP would return these results::

    [
        [
            {
                "my": {
                    "long": {
                        "path": {
                            "ge-0/0/110": {
                                "description": "SomeDescription glob1",
                                "ip": "10.0.40.121/31"
                            },
                            "lo00": {
                                "description": "Routing Loopback",
                                "ip": "10.6.4.4/32"
                            }
                        }
                    }
                }
            }
        ]
    ]


macro
------------------------------------------------------------
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
    
output functions
------------------------------------------------------------
``functions="function1('attributes') | function2('attributes') | ... | functionN('attributes')"``

* functionN - name of the output function together with it's attributes

String, that contains pipe separated list of output functions with functions' attributes
deepdiff
------------------------------------------------------------
``deepdiff="before, after, add_field=difference, ignore_order=False, verbose_level=2``

* before - string, name of input, which results should be used to compare with
* after - string, name of input, which results should be used for comparing
* add_field - string, name of field to add compare results, by default is False, hence compare results will replace results data
* kwargs - any arguments supported by deepdiff DeepDiff object, such as ignore_order or verbose_level

**Prerequisites:** Python deepdiff library need to be installed.

This function takes parsing results for specified inputs and compares them one against another using deepdiff DeepDiff object. 

The usecase for this function might be having two folders on the hard drive, one folder with data before and second folder with data after some changes were done to network devices, TTP can be used to parse this data (can be show commands output for instance) and run results comparison using deepdiff function, which can show the differences between Python structures content, as opposed to comparing text data itself.

**Example**

In this example, results of inputs with names ``input_before`` and ``input_after`` will be compared one against the other.

Template::

    <input name="input_before" load="text">
    interface FastEthernet1/0/1
     description Foo
    !
    </input>
    
    <input name="one_more" load="text">
    interface FastEthernet1/0/1
     description FooBar
    !
    </input>
    
    <input name="input_after" load="text">
    interface FastEthernet1/0/1
     description Bar
    !
    </input>
    
    <group  
    name="interfaces*">
    interface {{ interface }}
     description {{ description }}
    </group>
    
    <output deepdiff="input_before, input_after, add_field=difference, ignore_order=False, verbose_level=2"/>
	
Results::

    [   [   {   'interfaces': [   {   'description': 'Foo',
                                      'interface': 'FastEthernet1/0/1'}]},
            {   'interfaces': [   {   'description': 'FooBar',
                                      'interface': 'FastEthernet1/0/1'}]},
            {   'interfaces': [   {   'description': 'Bar',
                                      'interface': 'FastEthernet1/0/1'}]},
            {   'difference': {   'values_changed': {   "root['interfaces'][0]['description']": {   'new_value': 'Bar',
                                                                                                'old_value': 'Foo'}}}}]]
	
As you can see comparison results were appended to overall results as a dictionary with top key set to ``add_field`` value ``difference`` in this case, if ``add_field`` would be omitted, parsing results will be replaced with comparison outcome and TTP will produce this output::

[   {   'values_changed': {   "root['interfaces'][0]['description']": {   'new_value': 'Bar',
                                                                          'old_value': 'Foo'}}}]