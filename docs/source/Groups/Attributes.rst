Attributes
==========

Each group tag (<g>, <grp>, <group>) can have a number of attributes, they used during module execution to provide desired results. Attributes can be mandatory or optional. Each attribute is a string of data formatted in certain way.

.. list-table:: group attributes
   :widths: 10 90
   :header-rows: 1

   * - Attribute
     - Description
   * - `name`_   
     - Uniquely identifies group(s) within template and specifies results path location
   * - `input`_  
     - Name of input tag or OS path string to files location
   * - `default`_   
     - Contains default value that should be set for all variables if nothing been matched
   * - `method`_   
     - Indicates parsing method, supported values are *group* or *table*
   * - `output`_   
     - Specify group specific outputs to run group result through          

name
------------------------------------------------------------------------------
``name="path_string"``

* path_string (mandatory) - this is the only attribute that *must* be set for each group as it used to form group path - path is a dot separated string that indicates group results placement in results structure.

More on name attribute: Group Name Attribute

input
------------------------------------------------------------------------------
``input="input1, input2, ... inputN"``

* inputN (optional) - comma separated string that contains name(s) of the input tag(s) that should be used to source data for this group, alternatively input string value can reference Operating System fully qualified or relative path to location of text file(s) that should be parsed by this group. OS relative path should be accompanied with template base_path attribute, that attribute will be perpended to group input to form fully qualified path.

Input attribute of the group considered to be more specific in case if group name referenced in input :ref:`Inputs/Attributes:groups` attribute, as a result several groups can share same name, but reference different inputs with different set of data to be parsed.

.. note:: Input attributed only supported at top group, nested groups input attributes are ignored.

**Example-1**

Template::

    <input name="test1" load="text">
    interface GigabitEthernet3/3
     switchport trunk allowed vlan add 138,166-173 
    </input>
    
    <group name="interfaces" input="test1">
    interface {{ interface }}
     switchport trunk allowed vlan add {{ trunk_vlans }}
    </group>
    
Result::

    [
        {
            "interfaces": {
                "interface": "GigabitEthernet3/3",
                "trunk_vlans": "138,166-173"
            }
        }
    ]
    
**Example-2**

In this example several inputs define, by default groups set to 'all' for them, moreover, groups have identical name attribute. In this case group's *input* attribute helps to define which input should be parsed by which group.

Template::

    <input name="input_1" load="text">
    interface GigabitEthernet3/11
     description input_1_data
     switchport trunk allowed vlan add 111,222
    !
    </input>
    
    <input name="input_2" load="text">
    interface GigabitEthernet3/22
     description input_2_data
     switchport trunk allowed vlan add 222,888
    !
    </input>
    
    <group name="interfaces.trunks" input="input_1">
    interface {{ interface }}
     switchport trunk allowed vlan add {{ trunk_vlans }}
     description {{ description | ORPHRASE }}
     {{ group_id | set("group_1") }}
    !{{ _end_ }}
    </group>
    
    <group name="interfaces.trunks" input="input_2">
    interface {{ interface }}
     switchport trunk allowed vlan add {{ trunk_vlans }}
     description {{ description | ORPHRASE }}
     {{ group_id | set("group_2") }}
    !{{ _end_ }}
    </group>
    
Result::

    [
        {
            "interfaces": {
                "trunks": {
                    "description": "input_1_data",
                    "group_id": "group_1",
                    "interface": "GigabitEthernet3/11",
                    "trunk_vlans": "111,222"
                }
            }
        },
        {
            "interfaces": {
                "trunks": {
                    "description": "input_2_data",
                    "group_id": "group_2",
                    "interface": "GigabitEthernet3/22",
                    "trunk_vlans": "222,888"
                }
            }
        }
    ]

default
------------------------------------------------------------------------------
``default="value"``

* value (optional) - string that should be used as a default value for all variables within this group or template variable name. 

If default value reference template variable that contains dictionary, that dictionary structure will merge with group results. If group does not have matches, in that case default structure will be uses as group results.

.. warning:: referencing default might produce unexpected results for groups that has matches versus groups without matches, as always, test before use.

**Example-1**

Template::

    <input name="test1" load="text">
    interface GigabitEthernet3/3
     switchport trunk allowed vlan add 138,166-173 
    </input>
    
    <group name="interfaces" input="test1" default="some_default_value">
    interface {{ interface }}
     description {{ description }}
     switchport trunk allowed vlan add {{ trunk_vlans }}
     ip address {{ ip }}
    </group>

Result::

    [
        {
            "interfaces": {
                "description": "some_default_value",
                "interface": "GigabitEthernet3/3",
                "ip": "some_default_value",
                "trunk_vlans": "138,166-173"
            }
        }
    ]

Because ``default`` value used for group start regexes, if no matches produced by group, default values will be saved at group path, same is true for child groups

**Example-2**

Group with no matches but default values.

Template::

    <input load="text">
    device-hostame uptime is 27 weeks, 3 days, 10 hours, 46 minutes, 10 seconds
    </input>
    
    <group name="uptime**">
    device-hostame uptime is {{ uptime | PHRASE }}
    <group name="software">
     software version {{ version | default("uncknown") }}
    </group>
    </group>
    
    <group name="domain" default="Uncknown">
    Default domain is {{ fqdn }}
    </group>

Result::

    [
        [
            {
                "domain": {
                    "fqdn": "Uncknown"
                },
                "uptime": {
                    "uptime": "27 weeks, 3 days, 10 hours, 46 minutes, 10 seconds",
                    "software": {
                        "version": "uncknown"
                    }
                }
            }
        ]
    ]
    
In above example in input there is no data to match by group ``domain``, this group default values were saved in results. Same is for child group ``software`` - no data to match in input, hence default values appears in results, because match variable ``software`` is start RE.

**Example-3**

In this template, ``default`` attribute reference dictionary defined in template variable.

Template::

    <input load="text">
    interface Lo0
     ip address 1.1.1.1 255.255.255.255
    !
    interface Lo1
     description this interface has description
    </input>
    
    <input load="text">
    interface Lo10
     ip address 1.1.1.2 255.255.255.255
    !
    interface Lo11
     description another interface with description
     ip address 1.1.1.3 255.255.255.255
    </input>
    
    <vars>
    var_name = {
        "L3": True,
        "has_ip": True
    }
    </vars>
    
    <group name="interfaces">
    interface {{ interface }}
     description {{ description | ORPHRASE }}
     <group name="IPv4_addresses" default="var_name">
     ip address {{ IP }} {{ MASK }}
     </group>
    </group>
    
Results::

    [[{'interfaces': [{'IPv4_addresses': {'IP': '1.1.1.1',
                                          'L3': True,
                                          'MASK': '255.255.255.255',
                                          'has_ip': True},
                       'interface': 'Lo0'},
                      {'description': 'this interface has description',
                       'interface': 'Lo1'}]},
      {'interfaces': [{'IPv4_addresses': {'IP': '1.1.1.2',
                                          'L3': True,
                                          'MASK': '255.255.255.255',
                                          'has_ip': True},
                       'interface': 'Lo10'},
                      {'IPv4_addresses': {'IP': '1.1.1.3',
                                          'L3': True,
                                          'MASK': '255.255.255.255',
                                          'has_ip': True},
                       'description': 'another interface with description',
                       'interface': 'Lo11'}]}]]

method
------------------------------------------------------------------------------
``method="value"``

* value (optional) - [group | table] default is *group*. If method it *group* only first regular expression in group considered as group-start-re, in addition template lines that contain *_start_* indicator also used as group-start-re.

On the other hand, if method set to *table* each and every regular expression in the group considered as group-start-re, that is very useful if semi-table data structure parsed, and we have several variations of row.

**Example**

In this example arp table needs to be parsed, but to match all the variations we have to define several template expressions.

Data::

    CSR1Kv-3-lab#show ip arp
    Protocol  Address          Age (min)  Hardware Addr   Type   Interface
    Internet  10.1.13.1              98   0050.5685.5cd1  ARPA   GigabitEthernet2.13
    Internet  10.1.13.3               -   0050.5685.14d5  ARPA   GigabitEthernet2.13

Template:

This is the template with default method *group*::

    <group name="arp">
    Internet  {{ ip }}  {{ age | DIGIT }}   {{ mac }}  ARPA   {{ interface }}
    Internet  {{ ip }}  -                   {{ mac }}  ARPA   {{ interface| _start_}}
    </group>

This is functionally the same template but with method *table*::

    <group name="arp" method="table">
    Internet  {{ ip }}  {{ age | DIGIT }}   {{ mac }}  ARPA   {{ interface }}
    Internet  {{ ip }}  -                   {{ mac }}  ARPA   {{ interface }}
    </group>

Result::

    [
        {
            "arp": [
                {
                    "age": "98",
                    "interface": "GigabitEthernet2.13",
                    "ip": "10.1.13.1",
                    "mac": "0050.5685.5cd1"
                },
                {
                    "interface": "GigabitEthernet2.13",
                    "ip": "10.1.13.3",
                    "mac": "0050.5685.14d5"
                }
            ]
        }
    ]
    
    
output
------------------------------------------------------------------------------
``output="output1, output2, ... , outputN"``

* outputN - comma separated string of output tag names that should be used to run group results through. The sequence of outputs provided *are preserved* and run run in specified order, meaning that output2 will run only after output1.

.. note:: only top group supports output attribute, nested groups' output attributes are ignored.