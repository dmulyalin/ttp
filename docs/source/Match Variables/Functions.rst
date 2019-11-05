Functions
===============

TTP contains a set of TTP match variables functions that can be applied to match results to transform them in a desired way or validate and filter match results. 

Action functions act upon match result to transform into desired state.
  
.. list-table:: Action functions
   :widths: 10 90
   :header-rows: 1

   * - Name
     - Description
   * - `chain`_ 
     - add functions from chain variable 
   * - `record`_ 
     - Save match result to variable with given name, which can be referenced by actions
   * - `let`_ 
     - Assigns provided value to match variable
   * - `truncate`_ 
     - truncate match results
   * - `joinmatches`_ 
     - join matches using provided character
   * - `resub`_ 
     - replace old patter with new pattern in match using re substitute method
   * - `join`_ 
     - join match using provided character
   * - `append`_ 
     - append provided string to match result
   * - `print`_ 
     - print match result to terminal
   * - `unrange`_ 
     - unrange match result using given parameters
   * - `set`_ 
     - set result to specific value based if certain string was matched
   * - `replaceall`_ 
     - run replace against match for all given values
   * - `resuball`_ 
     - run re substitute against match for all given values
   * - `lookup`_ 
     - find match value in lookup table and return result
   * - `rlookup`_ 
     - find rlookup table key in match result and return associated values
   * - `item`_ 
     - returns item at given index on match result
   * - `macro`_ 
     - runs match result against macro function
   * - `to_list`_ 
     - creates empty list nd appends match result to it
   * - `to_int`_ 
     - transforms result to integer
   * - `to_str`_ 
     - transforms result to python string
   * - `to_ip`_ 
     - transforms result to python ipaddress module IPvXAddress or IPvXInterface object
   * - `to_net`_ 
     - transforms result to python ipaddress module IPvXNetwork object
   * - `to_cidr`_ 
     - transforms netmask to cidr (prefix length) notation
   * - `ip_info`_ 
     - produces a dictionary with information about give ip address or subnet
   * - `dns`_ 
     - performs DNS forward lookup
   * - `rdns`_ 
     - performs DNS reverse lookup
   * - `sformat`_ 
     - string format using python string format method
   * - `uptimeparse`_ 
     - function to parse uptime string
   * - `mac_eui`_ 
     - transforms mac string into EUI format
 
Condition functions can perform various checks with match results and returns either True or False depending on check results.

.. list-table:: Condition functions
   :widths: 10 90
   :header-rows: 1
   
   * - Name
     - Description  
   * - `startswith_re`_ 
     - checks if match starts with certain string using regular expression
   * - `endswith_re`_ 
     - checks if match ends with certain string using regular expression
   * - `contains_re`_ 
     - checks if match contains certain string using regular expression
   * - `contains`_ 
     - checks if match contains certain string
   * - `notstartswith_re`_ 
     - checks if match not starts with certain string using regular expression
   * - `notendswith_re`_ 
     - checks if match not ends with certain string using regular expression
   * - `exclude_re`_ 
     - checks if match not contains certain string using regular expression
   * - `exclude`_ 
     - checks if match not contains certain string
   * - `isdigit`_ 
     - checks if match is digit string e.g. '42'
   * - `notdigit`_ 
     - checks if match is not digit string
   * - `greaterthan`_ 
     - checks if match is greater than given value
   * - `lessthan`_ 
     - checks if match is less than given value
   * - `is_ip`_ 
     - tries to convert match result to ipaddress object and returns True if so, False otherwise
   * - `cidr_match`_ 
     - transforms result to ipaddress object and checks if it overlaps with given prefix
     
Python built-ins
------------------------------------------------------------------------------
Apart from functions provided by ttp, python objects built-in functions can be used as well. For instance string *upper* method can be used to convert match into upper case, or list *index* method to return index of certain value.

**Example**

Data::

 interface Tunnel2422
  description cpe-1
 !
 interface GigabitEthernet1/1
  description core-1
 
Template::

 <group name="interfaces">
 interface {{ interface | upper }}
  description {{ description | split('-') }}
 </group>

Result::

 {
     "interfaces": [
         {
             "description": ["cpe", "1"],
             "interface": "TUNNEL2422"
         },
         {
             "description": ["core", "1"],
             "interface": "GIGABITETHERNET1/1"
         }
     ]
 }

chain
------------------------------------------------------------------------------
``{{ name | chain(variable_name) }}``

* variable_name (mandatory) - string containing variable name

Sometime when many functions needs to be run against match result the template can become difficult to read, in addition if same set of functions needs to be run against several matches and changes needs to be done to the set of functions it can become difficult to maintain such a template. 

To solve above problem *chain* function can be used. Value supplied to that function must reference a valid variable name, that variable should contain string of functions names that should be used for match result, alternatively variable can reference a list of items, each item is a string representing function to run.

**Example-1**

chain referencing variable that contains string of functions separated by pipe symbol.

Data::

 interface GigabitEthernet3/3
  switchport trunk allowed vlan add 138,166-173 
  switchport trunk allowed vlan add 400,401,410
 
Template::

 <vars>
 vlans = "unrange(rangechar='-', joinchar=',') | split(',') | join(':') | joinmatches(':')"
 </vars>
 
 <group name="interfaces">
 interface {{ interface }}
  switchport trunk allowed vlan add {{ trunk_vlans | chain('vlans') }}
 </group>

Result::

 {
     "interfaces": {
         "interface": "GigabitEthernet3/3",
         "trunk_vlans": "138:166:167:168:169:170:171:172:173:400:401:410"
     }
 }
 
**Example-2**

chain referencing variable that contains list of strings, each string is a function.

Data::

 interface GigabitEthernet3/3
  switchport trunk allowed vlan add 138,166-173 
  switchport trunk allowed vlan add 400,401,410
 
Template::

 <vars>
 vlans = [
    "unrange(rangechar='-', joinchar=',')",
    "split(',')",
    "join(':')",
    "joinmatches(':')"
 ]
 </vars>
 
 <group name="interfaces">
 interface {{ interface }}
  switchport trunk allowed vlan add {{ trunk_vlans | chain('vlans') }}
 </group>

Result::

 {
     "interfaces": {
         "interface": "GigabitEthernet3/3",
         "trunk_vlans": "138:166:167:168:169:170:171:172:173:400:401:410"
     }
 }
    
record
------------------------------------------------------------------------------
``{{ name | record(var_name) }}``

* var_name (mandatory) - a string containing variable name where to record match results

Records match results in template variable with given name after all functions run finished for match result. That recorded variable can be referenced within other functions such as `set`_ 

let
------------------------------------------------------------------------------
``{{ variable | let(var_name, value) }}`` or ``{{ variable | let(value) }}``

* value (mandatory) - a string containing value to be assigned to variable

Statically assigns provided value to variable with name var_name, if single argument provided, that argument considered to be a value and will be assigned to match variable replacing match result.

**Example**

Template::

    <input load="text">
    interface Loopback0
     description Management
     ip address 192.168.0.113/24
    !
    </input>
    
    <group name="interfaces">
    interface {{ interface }}
     description {{ description | let("description_undefined") }}
     ip address {{ ip | contains("24") | let("netmask", "255.255.255.0") }}
    </group>

Result::

    [
        {
            "interfaces": {
                "description": "description_undefined",
                "interface": "Loopback0",
                "ip": "192.168.0.113/24",
                "netmask": "255.255.255.0"
            }
        }
    ]

truncate
--------
``{{ name | truncate(count) }}``

* count (mandatory) - integer to count the number of words to remove

Splits match result using " "(space) char and joins it back up to truncate value. This function can be useful to shorten long match results.

**Example**

If match is "foo bar foo-bar" and truncate(2) will produce "foo bar". 
  
joinmatches
------------------------------------------------------------------------------
``{{ name | joinmatches(char) }}``

* char (optional) - character to use to join matches, default is new line '\\n'

Join results from different matches into a single result string using provider character or string. 

**Example**

Data::

    interface GigabitEthernet3/3
     switchport trunk allowed vlan add 138,166,173 
     switchport trunk allowed vlan add 400,401,410
 
Template::

    interface {{ interface }}
     switchport trunk allowed vlan add {{ trunk_vlans | joinmatches(',') }}

Result::

    {
        "interface": "GigabitEthernet3/3"  
        "trunkVlans": "138,166,173,400,401,410"
    }
    
resub
------------------------------------------------------------------------------
``{{ name | resub(old, new, count) }}``

* old (mandatory) - pattern to be replaced
* new (mandatory) - pattern to be replaced with
* count(optional) - digit, default is 1, indicates count of replacements to do

Performs re.sub(old, new, match, count) on match result and returns produced value

**Example**

Data::

    interface GigabitEthernet3/3
 
Template is::

    interface {{ interface | resub(old = '^GigabitEthernet'), new = 'Ge'}}

Result::

    {
        "interface": "Ge3/3"  
    }
    
join
------------------------------------------------------------------------------
``{{ name | match(char) }}``

* char (mandatory) - character to use to join match

Run joins against match result using provided character and return string


**Example**-1:

Match is a string here and running join against it will insert '.' in between each character 

Data::

    description someimportantdescription
 
Template is::

    description {{ description | join('.') }}

Result::

    {
        "description": "s.o.m.e.i.m.p.o.r.t.a.n.t.d.e.s.c.r.i.p.t.i.o.n"  
    }
    
**Example**-2:

After running split function match result transformed into list object, running join against list will produce string with values separated by ":" character

Data::

    interface GigabitEthernet3/3 
     switchport trunk allowed vlan add 138,166,173,400,401,410
 
Template::

    interface {{ interface }}  
     switchport trunk allowed vlan add {{ trunk_vlans | split(',') | join(':') }}

Result::

    {
        "interface": "GigabitEthernet3/3"  
        "trunkVlans": "138:166:173:400:401:410"
    }
    
append
------------------------------------------------------------------------------
``{{ name | append(string) }}``

* string (mandatory) - string append to match result

Appends string to match result and returns produced value

**Example**

Data::

    interface Ge3/3
 
Template is::

    interface {{ interface | append(' - non production') }}

Result::

    {
        "interface": "Ge3/3 - non production"  
    }
    
print
------------------------------------------------------------------------------
``{{ name | print }}``

Will print match result to terminal as is at the given position, can be used for debugging purposes

**Example**

Data::

    interface GigabitEthernet3/3
     switchport trunk allowed vlan add 138,166,173  
 
Template::

    interface {{ interface }}
     switchport trunk allowed vlan add {{ trunk_vlans | split(',') | print | join(':') print }}

Results printed to terminal::

    ['138', '166', '173']  <--First print statement
    138:166:173            <--Second print statement
    
unrange
------------------------------------------------------------------------------
``{{ name | unrange('rangechar', 'joinchar') }}``

* rangechar (mandatory) - character to indicate range
* joinchar (mandatory) - character used to join range items

If match result has integer range in it, this function can be used to extend that range to specific values, For instance if range is 100-105, after passing that result through this function result '101,102,103,104,105' will be produced. That is useful to extend trunk vlan ranges configured on interface.

**Example**

Data::

    interface GigabitEthernet3/3
     switchport trunk allowed vlan add 138,166,170-173
 
Template::

    interface {{ interface }}
     switchport trunk allowed vlan add {{ trunk_vlans | unrange(rangechar='-', joinchar=',') }}

Result::

    {
        "interface": "GigabitEthernet3/3"  
        "trunkVlans": "138,166,170,171,172,173"
    }
    
set
------------------------------------------------------------------------------
``{{ name | set('var_set_value') }}``

* var_set_value (mandatory) - string to set as a value for variable, can be a name of template variable.

Not all configuration statements have variables or values associated with them, but can serve as an indicator if particular feature disabled or enabled, to match such a cases *set* function can be used. This function allows to assign "var_set_value" to match variable, "var_set_value" considered to be a reference to template variable name, if no template variable with "var_set_value" found, "var_set_value" itself will be assigned to match variable.

It is also possible to use *set* function to introduce arbitrary key-value pairs in match result if set function used without any text in front of it.

**Example-1**

Conditional set function - set only will be invoked in case if preceding line matched. In below example " switchport trunk encapsulation dot1q" line will be searched for, if found, "encap" variable will have "dot1q" value set.

Data::

    interface GigabitEthernet3/4
     switchport mode access 
     switchport trunk encapsulation dot1q
     switchport mode trunk
     switchport nonegotiate
     shutdown
    !
    interface GigabitEthernet3/7
     switchport mode access 
     switchport mode trunk
     switchport nonegotiate
    !
 
Template::

    <vars>
    mys_set_var = "my_set_value"
    </vars>
    
    <group name="interfacesset">
    interface {{ interface }}
     switchport mode access {{ mode_access | set("True") }}
     switchport trunk encapsulation dot1q {{ encap | set("dot1q") }}
     switchport mode trunk {{ mode | set("Trunk") }} {{ vlans | set("all_vlans") }}
     shutdown {{ disabled | set("True") }} {{ test_var | set("mys_set_var") }}
    !{{ _end_ }}
    </group>

Result::

    {
        "interfacesset": [
            {
                "disabled": "True",
                "encap": "dot1q",
                "interface": "GigabitEthernet3/4",
                "mode": "Trunk",
                "mode_access": "True",
                "test_var": "my_set_value",
                "vlans": "all_vlans"
            },
            {
                "interface": "GigabitEthernet3/7",
                "mode": "Trunk",
                "mode_access": "True",
                "vlans": "all_vlans"
            }
        ]
    }
    
.. note:: Multiple set statements are supported within the line, however, no other variables can be specified except with *set*, as match performed based on the string preceding variables with *set* function, for instance below will not work: ``switchport mode {{ mode }} {{ switchport_mode | set('Trunk') }} {{ trunk_vlans | set('all') }}``

**Example-2**

Unconditional set - in this example "interface_role" will be statically set to "Uplink", but value for "provider" variable will be taken from template variable "my_var" and set to "L2VC".

Data::

    interface Vlan777
      description Management
      ip address 192.168.0.1/24
      vrf MGMT
    !

Template::

    <vars>
    my_var = "L2VC"
    </vars>

    <group>
    interface {{ interface }}
      description {{ description }}
      ip address {{ ip }}/{{ mask }}
      vrf {{ vrf }}
      {{ interface_role | set("Uplink") }}
      {{ provider | set("my_var") }}
    !{{_end_}}
    </group>

Result::

    [
        {
            "description": "Management",
            "interface": "Vlan777",
            "interface_role": "Uplink",
            "ip": "192.168.0.1",
            "mask": "24",
            "provider": "L2VC",
            "vrf": "MGMT"
        }
    ]
    
replaceall
------------------------------------------------------------------------------
``{{ name | replaceall('value1', 'value2', ..., 'valueN') }}``

* value (mandatory) - string to replace in match

Run string replace method on match with *new* and *old* values derived using below rules.

**Case 1** If only one value given *new* set to '' empty value, if several values specified *new* set to first value

**Example-1.1** With *new* set to '' empty value

Data::

    interface GigabitEthernet3/3 
    interface GigEthernet5/7 
    interface GeEthernet1/5
 
Template::

    interface {{ interface | replaceall('Ethernet') }}

Result::

    {'interface': 'Gigabit3/3'} 
    {'interface': 'Gig5/7'} 
    {'interface': 'Ge1/5'}
    
**Example-1.2** With *new* set to 'Ge'

Data::

    interface GigabitEthernet3/3 
    interface GigEth5/7 
    interface Ethernet1/5
 
Template::

    interface {{ interface | replaceall('Ge', 'GigabitEthernet', 'GigEth', 'Ethernet') }}

Result::

    {'interface': 'Ge3/3'} 
    {'interface': 'Ge5/7'} 
    {'interface': 'Ge1/5'}
    
**Case 2** If value found in variables that variable used, if variable value is  a list, function will iterate over list and for each item run replace where *new* set either to "" empty or to first value and *old* equal to each list item

**Example-2.1** With *new* set to 'GE' value

Data::

    interface GigabitEthernet3/3 
    interface GigEthernet5/7 
    interface GeEthernet1/5
 
Template::

    <vars load="python">
    intf_replace = ['GigabitEthernet', 'GigEthernet', 'GeEthernet']
    </vars>
    
    <group name="ifs">
    interface {{ interface | replaceall('GE', 'intf_replace') }}
    <group>   
    
Result::

    {
        "ifs": [
            {
                "interface": "GE3/3"
            },
            {
                "interface": "GE5/7"
            },
            {
                "interface": "GE1/5"
            }
        ]
    }
    
**Example-2.2** With *new* set to '' empty value

Data::

    interface GigabitEthernet3/3 
    interface GigEthernet5/7 
    interface GeEthernet1/5
 
Template::

    <vars load="python">
    intf_replace = ['GigabitEthernet', 'GigEthernet', 'GeEthernet']
    </vars>
    
    <group name="ifs">
    interface {{ interface | replaceall('intf_replace') }}
    <group>   
    
Result::

    {
        "ifs": [
            {
                "interface": "3/3"
            },
            {
                "interface": "5/7"
            },
            {
                "interface": "1/5"
            }
        ]
    }
    
**Case 3** If value found in variables that variable used, if variable value is  a dictionary, function will iterate over dictionary items and set *new* to item key and *old* to item value. 

* If item value is a list, function will iterate over list and run replace using each entry as *old* value
* If item value is a string, function will use that string as *old* value

**Example-3.1** With dictionary values as lists

Data::

    interface GigabitEthernet3/3 
    interface GigEthernet5/7 
    interface GeEthernet1/5
    interface Loopback1/5
    interface TenGigabitEth3/3 
    interface TeGe5/7 
    interface 10GE1/5
 
Template::

    <vars load="python">
    intf_replace = {
                    'Ge': ['GigabitEthernet', 'GigEthernet', 'GeEthernet'],
                    'Lo': ['Loopback'],
                    'Te': ['TenGigabitEth', 'TeGe', '10GE']
                    }
    </vars>
    
    <group name="ifs">
    interface {{ interface | replaceall('intf_replace') }}
    <group>   
    
Result::

    {
        "ifs": [
            {
                "interface": "Ge3/3"
            },
            {
                "interface": "Ge5/7"
            },
            {
                "interface": "Ge1/5"
            },
            {
                "interface": "Lo1/5"
            },
            {
                "interface": "Te3/3"
            },
            {
                "interface": "Te5/7"
            }
        ]
    }
    
resuball
------------------------------------------------------------------------------
``{{ name | resuball('value1', 'value2', ..., 'valueN') }}``

* value(mandatory) - string to replace in match

Same as `replaceall`_ but instead of string replace this function runs python re substitute method, allowing the use of regular expression to match *old* values.

**Example**

If *new* set to "Ge" and *old* set to "GigabitEthernet", running string replace against "TenGigabitEthernet" match will produce "Ten" as undesirable result, to overcome that problem regular expressions can be used. For instance, regex "^GigabitEthernet" will only match "GigabitEthernet3/3" as "^" symbol indicates beginning of the string and will not match "GigabitEthernet" in "TenGigabitEthernet".

Data::

 interface GigabitEthernet3/3 
 interface TenGigabitEthernet3/3 
 
Template::

 <vars load="python">
 intf_replace = {
                 'Ge': ['^GigabitEthernet'],
                 'Te': ['^TenGigabitEthernet']
                 }
 </vars>
 
 <group name="ifs">
 interface {{ interface | resuball('intf_replace') }}
 <group>   
 
Result::

 {
     "ifs": [
         {
             "interface": "Ge3/3"
         },
         {
             "interface": "Ge5/7"
         },
         {
             "interface": "Ge1/5"
         },
         {
             "interface": "Lo1/5"
         },
         {
             "interface": "Te3/3"
         },
         {
             "interface": "Te5/7"
         }
     ]
 }
 
lookup
------------------------------------------------------------------------------
``{{ name | lookup('name', 'add_field') }}``

* name(mandatory) - lookup name and dot-separated path to data within which to perform lookup
* add_field(optional) - default is False, can be set to string that will indicate name of the new field

Lookup function takes match value and perform lookup on that value in lookup table. Lookup table is a dictionary data where keys checked if they are equal to math result.

If lookup was unsuccessful no changes introduces to match result, if it was successful we have two option on what to do with looked up values:
* if add_field is False - match Result replaced with found values
* if add_field is not False - string passed as add_field value used as a name for additional field that will be added to group match results

**Example-1** *add_field* set to False

In this example, as 65101 will be looked up in the lookup table and replaced with found values

Data::

 router bgp 65100
   neighbor 10.145.1.9
     remote-as 65101
   !
   neighbor 192.168.101.1
     remote-as 65102
 
Template::

 <lookup name="ASNs" load="csv">
 ASN,as_name,as_description
 65100,Customer_1,Private ASN for CN451275
 65101,CPEs,Private ASN for FTTB CPEs
 </lookup>
 
 <group name="bgp_config">
 router bgp {{ bgp_as }}
  <group name="peers">
   neighbor {{ peer }}
     remote-as {{ remote_as | lookup('ASNs') }}
  </group>
 </group> 
 
Result::

 {
     "bgp_config": {
         "bgp_as": "65100",
         "peers": [
             {
                 "peer": "10.145.1.9",
                 "remote_as": {
                     "as_description": "Private ASN for FTTB CPEs",
                     "as_name": "CPEs"
                 }
             },
             {
                 "peer": "192.168.101.1",
                 "remote_as": "65102"
             }
         ]
     }
 }

**Example-2** With additional field

Data::

 router bgp 65100
   neighbor 10.145.1.9
     remote-as 65101
   !
   neighbor 192.168.101.1
     remote-as 65102
 
Template::

 <lookup name="ASNs" load="csv">
 ASN,as_name,as_description
 65100,Customer_1,Private ASN for CN451275
 65101,CPEs,Private ASN for FTTB CPEs
 </lookup>
 
 <group name="bgp_config">
 router bgp {{ bgp_as }}
  <group name="peers">
   neighbor {{ peer }}
     remote-as {{ remote_as | lookup('ASNs', add_field='asn_details') }}
  </group>
 </group> 
 
Result::

 {
     "bgp_config": {
         "bgp_as": "65100",
         "peers": [
             {
                 "asn_details": {
                     "as_description": "Private ASN for FTTB CPEs",
                     "as_name": "CPEs"
                 },
                 "peer": "10.145.1.9",
                 "remote_as": "65101"
             },
             {
                 "peer": "192.168.101.1",
                 "remote_as": "65102"
             }
         ]
     }
 }
 
rlookup
------------------------------------------------------------------------------
``{{ name | rlookup('name', 'add_field') }}``

* name(mandatory) - rlookup table name and dot-separated path to data within which to perform search
* add_field(optional) - default is False, can be set to string that will indicate name of the new field

This function searches rlookup table keys in match value. rlookup table is a dictionary data where keys checked if they are equal to math result.

If lookup was unsuccessful no changes introduces to match result, if it was successful we have two options:
* if add_field is False - match Result replaced with found values
* if add_field is not False - string passed as add_field used as a name for additional field to be added to group results, value for that new field is a data from lookup table

**Example**

In this example, bgp neighbors descriptions set to hostnames of peering devices, usually hostnames tend to follow some naming convention to indicate physical location of device or its network role, in below example, naming convention is *<state>-<city>-<role><num>* 

Data::

 router bgp 65100
   neighbor 10.145.1.9
     description vic-mel-core1
   !
   neighbor 192.168.101.1
     description qld-bri-core1
 
Template::

 <lookup name="locations" load="ini">
 [cities]
 -mel- : 7 Name St, Suburb A, Melbourne, Postal Code
 -bri- : 8 Name St, Suburb B, Brisbane, Postal Code
 </lookup>
 
 <group name="bgp_config">
 router bgp {{ bgp_as }}
  <group name="peers">
   neighbor {{ peer }}
     description {{ remote_as | rlookup('locations.cities', add_field='location') }}
  </group>
 </group> 
 
Result::

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
 
startswith_re
------------------------------------------------------------------------------
``{{ name | startswith_re('pattern') }}``

* pattern(mandatory) - string pattern to check

Python re search used to evaluate if match value starts with given string pattern, returns True if so and False otherwise

endswith_re
------------------------------------------------------------------------------
``{{ name | endswith_re('pattern') }}``

* pattern(mandatory) - string pattern to check

Python re search used to evaluate if match value ends with given string pattern, returns True if so and False otherwise

contains_re
------------------------------------------------------------------------------
``{{ name | contains_re('pattern') }}``

* pattern(mandatory) - string pattern to check

Python re search used to evaluate if match value contains given string pattern, returns True if so and False otherwise

contains
------------------------------------------------------------------------------
``{{ name | contains('pattern') }}``

* pattern(mandatory) - string pattern to check

This function evaluates if match value contains given string pattern, returns True if so and False otherwise.

**Example**

*contains* can be used to filter group results based on filtering start res, for instance, if we have configuration of networking device and we want to extract information only about *Vlan* interfaces.

Data::

 interface Vlan123
  description Desks vlan
  ip address 192.168.123.1 255.255.255.0
 !
 interface GigabitEthernet1/1
  description to core-1
 !
 interface Vlan222
  description Phones vlan
  ip address 192.168.222.1 255.255.255.0
 !
 interface Loopback0
  description Routing ID loopback
 
Template::

 <group name="SVIs">
 interface {{ interface | contains('Vlan') }}
  description {{ description | ORPHRASE}}
  ip address {{ ip }} {{ mask }}
 </group>
 
Result::

 {
     "SVIs": [
         {
             "description": "Desks vlan",
             "interface": "Vlan123",
             "ip": "192.168.123.1",
             "mask": "255.255.255.0"
         },
         {
             "description": "Phones vlan",
             "interface": "Vlan222",
             "ip": "192.168.222.1",
             "mask": "255.255.255.0"
         }
     ]
 }

If first line in the group contains match variables it is considered start re, if start re condition check result evaluated to *False*, all the matches that belong to this group will be filtered. In example above line "interface {{ interface | contains('Vlan') }}" is a start re, hence if "interface" variable match will not contain "Vlan", group results will be discarded.
 
notstartswith_re
------------------------------------------------------------------------------
``{{ name | notstartswith_re('pattern') }}``

* pattern(mandatory) - string pattern to check

Python re search used to evaluate if match value starts with given string pattern, returns False if so and True otherwise

notendswith_re
------------------------------------------------------------------------------
``{{ name | notendswith_re('pattern') }}``

* pattern(mandatory) - string pattern to check

Python re search used to evaluate if match value ends with given string pattern, returns False if so and True otherwise

exclude_re
------------------------------------------------------------------------------
``{{ name | exclude_re('pattern') }}``

* pattern(mandatory) - string pattern to check

Python re search used to evaluate if match value contains given string pattern, returns False if so and True otherwise

exclude
------------------------------------------------------------------------------
``{{ name | exclude('pattern') }}``

* pattern(mandatory) - string pattern to check

This function evaluates if match value contains given string pattern, returns False if so and True otherwise.

equal
------------------------------------------------------------------------------
``{{ name | equal('value') }}``

* value(mandatory) - string pattern to check

This function evaluates if match is equal to given value, returns True if so and False otherwise

notequal
------------------------------------------------------------------------------
``{{ name | notequal('value') }}``

* value(mandatory) - string pattern to check

This function evaluates if match is equal to given value, returns False if so and True otherwise

isdigit
------------------------------------------------------------------------------
``{{ name | isdigit }}``

This function checks if match is a digit, returns True if so and False otherwise

notdigit
------------------------------------------------------------------------------
``{{ name | notdigit }}``

This function checks if match is digit, returns False if so and True otherwise

greaterthan
------------------------------------------------------------------------------
``{{ name | greaterthan('value') }}``

* value(mandatory) - integer value to compare with

This function checks if match and supplied value are digits and performs comparison operation, if match is bigger than given value returns True and False otherwise

lessthan
------------------------------------------------------------------------------
``{{ name | lessthan('value') }}``

* value(mandatory) - integer value to compare with

This function checks if match and supplied value are digits and performs comparison, if match is smaller than provided value returns True and False otherwise

item
------------------------------------------------------------------------------
``{{ name | item(item_index) }}``

* item_index(mandatory) - integer, index of item to return

Return item value at given index of iterable. If match result (iterable) is string, *item* returns letter at given index, if match been transformed to list by 
the moment *item* function runs, returns list item at given index. item_index can be positive or negative digit, same rules as for retrieving list items applies 
e.g. if item_index is -1, last item will be returned.

In addition, ttp preforms index out of range checks, returning last or first item if item_index exceeds length of match result.

macro
------------------------------------------------------------------------------
``{{ name | macro(macro_name) }}``

* macro_name(mandatory) - name of macro function to pass match result through

Macro brings Python language capabilities to match results processing and validation during ttp module execution, as it allows to run custom functions against match results. Macro functions referenced by their name in match variable definitions or as a group *macro* attribute.

.. warning:: macro uses python ``exec`` function to parse code payload without imposing any restrictions, hence it is dangerous to run templates from untrusted sources as they can have macro defined in them that can be used to execute any arbitrary code on the system.

Macro function must accept only one attribute to hold match results, for match variable data supplied to macro function is a match result string.

For match variables, depending on data returned by macro function, ttp will behave differently according to these rules:

* If macro returns True or False - original data unchanged, macro handled as condition functions, invalidating result on False and keeps processing result on True
* If macro returns None - data processing continues, no additional logic associated
* If macro returns single item - that item replaces original data supplied to macro and processed further
* If macro return tuple of two elements - fist element must be string - match result, second - dictionary of additional fields to add to results

.. note:: Macro function contained within ``<macro>`` tag, each function loaded and saved into the dictionary of function name and function object, as a result cross referencing macro functions is not supported.

**Example**

In this example macro functions referenced in match variables.

Template::

    <input load="text">
    interface Vlan123
     description Desks vlan
     ip address 192.168.123.1 255.255.255.0
    !
    interface GigabitEthernet1/1
     description to core-1
    !
    interface Vlan222
     description Phones vlan
     ip address 192.168.222.1 255.255.255.0
    !
    interface Loopback0
     description Routing ID loopback
    !
    </input>
    
    <macro>
    def check_if_svi(data):
        if "Vlan" in data:
            return data, {"is_svi": True}
        else:
           return data, {"is_svi": False}
            
    def check_if_loop(data):
        if "Loopback" in data:
            return data, {"is_loop": True}
        else:
           return data, {"is_loop": False}
    </macro>
     
    <macro>
    def description_mod(data):
        # To revert words order in descripotion
        words_list = data.split(" ")
        words_list_reversed = list(reversed(words_list))
        words_reversed = " ".join(words_list_reversed) 
        return words_reversed
    </macro>
 
    <group name="interfaces_macro">
    interface {{ interface | macro("check_if_svi") | macro("check_if_loop") }}
     description {{ description | ORPHRASE | macro("description_mod")}}
     ip address {{ ip }} {{ mask }}
    </group>
 
Result::

    [
        {
            "interfaces_macro": [
                {
                    "description": "vlan Desks",
                    "interface": "Vlan123",
                    "ip": "192.168.123.1",
                    "is_loop": false,
                    "is_svi": true,
                    "mask": "255.255.255.0"
                },
                {
                    "description": "core-1 to",
                    "interface": "GigabitEthernet1/1",
                    "is_loop": false,
                    "is_svi": false
                },
                {
                    "description": "vlan Phones",
                    "interface": "Vlan222",
                    "ip": "192.168.222.1",
                    "is_loop": false,
                    "is_svi": true,
                    "mask": "255.255.255.0"
                },
                {
                    "description": "loopback ID Routing",
                    "interface": "Loopback0",
                    "is_loop": true,
                    "is_svi": false
                }
            ]
        }
    ]
    
to_list
------------------------------------------------------------------------------
``{{ name | to_list }}``

to_list transform match result in python list object in such a way that if match result is a string, empty lit will be created and result will be appended to it, if match result not a string by the time to_list function runs, this function does nothing.

**Example**

Template::

    <input load="text" name="test1-18">
    interface GigabitEthernet1/1
     description to core-1
     ip address 192.168.123.1 255.255.255.0
    !
    </input> 
    <group name="interfaces_functions_test1_18" 
    input="test1-18"
    output="test1-18"
    >
    interface {{ interface }}
     description {{ description | ORPHRASE | split(" ") | to_list }}
     ip address {{ ip | to_list }} {{ mask }}
    </group>

Result::

    [{
        "interfaces_functions_test1_18": {
            "description": [
                "to",
                "core-1"
            ],
            "interface": "GigabitEthernet1/1",
            "ip": [
                "192.168.123.1"
            ],
            "mask": "255.255.255.0"
        }
    }]

to_str
------------------------------------------------------------------------------
``{{ name | to_str }}``

This function transforms match result to string object running python ``str(match_result)`` built-in function, that is useful for such a cases when match result been transformed to some other object during processing and it needs to be converted back to string.

to_int
------------------------------------------------------------------------------
``{{ name | to_int }}``

This function will try to transforms match result into integer object running python ``int(match_result)`` built-in function, if it fails to do so, execution will continue, results will not e invalidated. to_int is useful if you need to convert string representation of integer in actual integer object to run mathematical operation with it.

to_ip
------------------------------------------------------------------------------
``{{ name | to_ip }}`` or ``{{ name | to_ip("ipv4") }}``

* to_ip(version) - uses python ipaddress module to transform match result in one of ipaddress supported objects, by default will use ipaddress module built-in logic to determine version of IP address, optionally version can be provided using *ipv4* or *ipv6* arguments to create IPv4Address or IPv6Address ipaddress module objects. In addition ttp does the check to detect if slash "/" present - e.g. 137.168.1.3/27 - in match result or space " " present in match result - e.g. 137.168.1.3 255.255.255.224, if so it will create IPInterface, IPv4Interface or IPv6Interface object depending on provided arguments.

After match result transformed into ipaddress' IPaddress or IPInterface object, built-in functions and attributes of these objects can be called using match variable functions chains.

.. note:: reference ipaddress module documentation for complete list of functions and attributes

**Example**

It is often that devices use "ip address 137.168.1.3 255.255.255.224" syntaxes to configure interface's IP addresses, let's assume we need to convert it to "137.168.1.3/27" representation and vice versa.

Template::

    <input load="text">
    interface Loopback0
     ip address 1.0.0.3 255.255.255.0
    !
    interface Vlan777
     ip address 192.168.0.1/24
    !
    </input>
    
    <group name="interfaces">
    interface {{ interface }}
     ip address {{ ip | PHRASE | to_ip | with_prefixlen }}
     ip address {{ ip | to_ip | with_netmask }}
    </group>
    
Result::

    [
        {
            "interfaces": [
                {
                    "interface": "Loopback0",
                    "ip": "1.0.0.3/24"
                },
                {
                    "interface": "Vlan777",
                    "ip": "192.168.0.1/255.255.255.0"
                }
            ]
        }
    ]

with_prefixlen and with_netmask are python ipaddress module IPv4Interface object's built-in functions. 

to_net
------------------------------------------------------------------------------
``{{ name | to_net }}``

This function leverages python built-in ipaddress module to transform match result into IPNetwork object provided that match is a valid ipv4 or ipv6 network strings e.g. 192.168.0.0/24
 or fe80:ab23::/64.
 
**Example**

Let's assume we need to get results for private routes only from below data, to_net can be used to transform match result into network object together with IPNetwork built-in function is_private to filter results.

Template::

    <input load="text">
    RP/0/0/CPU0:XR4#show route
    i L2 10.0.0.2/32 [115/20] via 10.0.0.2, 00:41:40, tunnel-te100
    i L2 172.16.0.3/32 [115/10] via 10.1.34.3, 00:45:11, GigabitEthernet0/0/0/0.34
    i L2 1.1.23.0/24 [115/20] via 10.1.34.3, 00:45:11, GigabitEthernet0/0/0/0.34
    </input>
    
    <group name="routes">
    {{ code }} {{ subcode }} {{ net | to_net | is_private | to_str }} [{{ ad }}/{{ metric }}] via {{ nh_ip }}, {{ age }}, {{ nh_interface }}
    </group>
    
Result::

    [
        {
            "routes": [
                {
                    "ad": "115",
                    "age": "00:41:40",
                    "code": "i",
                    "metric": "20",
                    "net": "10.0.0.2/32",
                    "nh_interface": "tunnel-te100",
                    "nh_ip": "10.0.0.2",
                    "subcode": "L2"
                },
                {
                    "ad": "115",
                    "age": "00:45:11",
                    "code": "i",
                    "metric": "10",
                    "net": "172.16.0.3/32",
                    "nh_interface": "GigabitEthernet0/0/0/0.34",
                    "nh_ip": "10.1.34.3",
                    "subcode": "L2"
                }
            ]
        }
    ]

is_private check invalidated public 1.1.23.0/24 subnet and only private networks were included in results.

to_cidr
------------------------------------------------------------------------------
``{{ name | to_cidr }}``

Function to convert subnet mask in prefix length representation, for instance if match result is "255.255.255.0", to_cidr function will return "24"

ip_info
------------------------------------------------------------------------------
``{{ name | ip_info }}``

Python ipaddress module helps to convert plain text string into IP addresses objects, as part of that process ipaddress module calculates a lot of additional information, ip_info function retrieves that information from that object and returns it in dictionary format.

**Example**

Below loopback0 IP address will be converted to IPv4Address object and ip_info will return information about that IP only, for other interfaces ttp will be able to create IPInterface objects, that apart from IP details contains information about network.

Template::

    <input load="text">
    interface Loopback0
     ip address 1.0.0.3 255.255.255.0
    !
    interface Vlan777
     ip address 192.168.0.1/24
    !
    interface Vlan777
     ip address fe80::fd37/124
    !
    </input>
    
    <group name="interfaces">
    interface {{ interface }}
     ip address {{ ip | to_ip | ip_info }} {{ mask }}
     ip address {{ ip | to_ip | ip_info }}
    </group>
    
Result::

    [
        {
            "interfaces": [
                {
                    "interface": "Loopback0",
                    "ip": {
                        "compressed": "1.0.0.3",
                        "exploded": "1.0.0.3",
                        "ip": "1.0.0.3",
                        "is_link_local": false,
                        "is_loopback": false,
                        "is_multicast": false,
                        "is_private": false,
                        "is_reserved": false,
                        "is_unspecified": false,
                        "max_prefixlen": 32,
                        "version": 4
                    },
                    "mask": "255.255.255.0"
                },
                {
                    "interface": "Vlan777",
                    "ip": {
                        "broadcast_address": "192.168.0.255",
                        "compressed": "192.168.0.1/24",
                        "exploded": "192.168.0.1/24",
                        "hostmask": "0.0.0.255",
                        "hosts": 254,
                        "ip": "192.168.0.1",
                        "is_link_local": false,
                        "is_loopback": false,
                        "is_multicast": false,
                        "is_private": true,
                        "is_reserved": false,
                        "is_unspecified": false,
                        "max_prefixlen": 32,
                        "netmask": "255.255.255.0",
                        "network": "192.168.0.0/24",
                        "network_address": "192.168.0.0",
                        "num_addresses": 256,
                        "prefixlen": 24,
                        "version": 4,
                        "with_hostmask": "192.168.0.1/0.0.0.255",
                        "with_netmask": "192.168.0.1/255.255.255.0",
                        "with_prefixlen": "192.168.0.1/24"
                    }
                },
                {
                    "interface": "Vlan777",
                    "ip": {
                        "broadcast_address": "fe80::fd3f",
                        "compressed": "fe80::fd37/124",
                        "exploded": "fe80:0000:0000:0000:0000:0000:0000:fd37/124",
                        "hostmask": "::f",
                        "hosts": 14,
                        "ip": "fe80::fd37",
                        "is_link_local": true,
                        "is_loopback": false,
                        "is_multicast": false,
                        "is_private": true,
                        "is_reserved": false,
                        "is_unspecified": false,
                        "max_prefixlen": 128,
                        "netmask": "ffff:ffff:ffff:ffff:ffff:ffff:ffff:fff0",
                        "network": "fe80::fd30/124",
                        "network_address": "fe80::fd30",
                        "num_addresses": 16,
                        "prefixlen": 124,
                        "version": 6,
                        "with_hostmask": "fe80::fd37/::f",
                        "with_netmask": "fe80::fd37/ffff:ffff:ffff:ffff:ffff:ffff:ffff:fff0",
                        "with_prefixlen": "fe80::fd37/124"
                    }
                }
            ]
        }
    ]

is_ip
------------------------------------------------------------------------------
``{{ name | is_ip }}``

is_ip function tries to convert provided match result in Python ipaddress module IPAddress or IPInterface object, if that happens without any exceptions (errors), is_ip returns True and False otherwise.

**Example**

Template::

    <input load="text">
    interface Loopback0
     ip address 192.168.0.113/24
    !
    interface Loopback1
     ip address 192.168.1.341/24
    !
    </input>
    
    <group name="interfaces">
    interface {{ interface }}
     ip address {{ ip | is_ip }}
    </group>

Result::

    [
        {
            "interfaces": [
                {
                    "interface": "Loopback0",
                    "ip": "192.168.0.113/24"
                },
                {
                    "interface": "Loopback1"
                }
            ]
        }
    ]
    
192.168.1.341/24 match result was invalidated as it is not a valid IP address.

cidr_match
------------------------------------------------------------------------------
``{{ name | cidr_match(prefix) }}``

This function allows to convert provided prefix in ipaddress IPNetwork object and convert match_result into IPInterface object, after that, cidr_match will run *overlaps* check to see if provided prefix and match result ip address overlapping. 

**Example**

In example below IP of Loopback1 interface is not overlapping with 192.168.0.0/16 range, hence it will be invalidated.

Template::

    <input load="text">
    interface Loopback0
     ip address 192.168.0.113/24
    !
    interface Loopback1
     ip address 10.0.1.251/24
    !
    </input>
    
    <group name="interfaces">
    interface {{ interface }}
     ip address {{ ip | cidr_match("192.168.0.0/16") }}
    </group>

Result::

    [{
        "interfaces": [
            {
                "interface": "Loopback0",
                "ip": "192.168.0.113/24"
            },
            {
                "interface": "Loopback1"
            }
        ]
    }]

dns
------------------------------------------------------------------------------
``{{ name | dns(record='A', timeout=1, servers=[], add_field=False) }}``

This function performs forward DNS lookup of match results and returns sorted list of IP addresses returned by DNS. 

Prerequisites: `dnspython <http://www.dnspython.org/>`_ needs to be installed

Options:

* ``record`` - by default perform 'A' lookup, any dnspython supported record can be given, e.g. 'AAAA' for IPv6 lookup
* ``timeout`` - default is 1 second, amount of time to wait for response, overall lifetime of operation will be set to number of servers multiplied by timeout
* ``servers`` - comma separated string of DNS servers to use for lookup, by default uses DNS servers configured on machine running the code
* ``add_field`` - boolean or string, if string, its value will be used as a key for DNS lookup results, if False - DNS lookup results will replace match results

If DNS will fail for whatever reason, match results will be returned without any modifications.

**Example**

Template::

    <input load="text">
    interface GigabitEthernet3/11
     description wikipedia.org
    !
    </input>
    
    <group name="interfaces">
    interface {{ interface }}
     description {{ description | dns }}
    </group>
    
    <group name="interfaces_dnsv6">
    interface {{ interface }}
     description {{ description | dns(record='AAAA') }}
    </group>
    
    <group name="interfaces_dnsv4_google_dns">
    interface {{ interface }}
     description {{ description | dns(record='A', servers='8.8.8.8') }}
    </group>
    
    <group name="interfaces_dnsv6_add_field">
    interface {{ interface }}
     description {{ description | dns(record='AAAA', add_field='IPs') }}
    </group>
    
Result::

    [
        {
            "interfaces": {
                "description": [
                    "103.102.166.224"
                ],
                "interface": "GigabitEthernet3/11"
            },
            "interfaces_dnsv4_google_dns": {
                "description": [
                    "103.102.166.224"
                ],
                "interface": "GigabitEthernet3/11"
            },
            "interfaces_dnsv6": {
                "description": [
                    "2001:df2:e500:ed1a::1"
                ],
                "interface": "GigabitEthernet3/11"
            },
            "interfaces_dnsv6_add_field": {
                "IPs": [
                    "2001:df2:e500:ed1a::1"
                ],
                "description": "wikipedia.org",
                "interface": "GigabitEthernet3/11"
            }
        }
    ]
    
rdns
------------------------------------------------------------------------------
``{{ name | dns(timeout=1, servers=[], add_field=False) }}``

This function performs reverse DNS lookup of match results and returns FQDN obtained from DNS. 

Prerequisites: `dnspython <http://www.dnspython.org/>`_ needs to be installed

Arguments:

* ``timeout`` - default is 1 second, amount of time to wait for response, overall lifetime of operation will be set to number of servers multiplied by timeout
* ``servers`` - comma separated string of DNS servers to use for lookup, by default uses DNS servers configured on machine running the code
* ``add_field`` - boolean or string, if string, its value will be used as a key for DNS lookup results, if False - DNS lookup results will replace match results

If DNS will fail for whatever reason, match results will be returned without any modifications.

**Example**

Template::

    <input load="text">
    interface GigabitEthernet3/11
     ip address 8.8.8.8 255.255.255.255
    !
    </input>
    
    <group name="interfaces_rdns">
    interface {{ interface }}
     ip address {{ ip | rdns }} {{ mask }}
    </group>
    
    <group name="interfaces_rdns_google_server">
    interface {{ interface }}
     ip address {{ ip | rdns(servers='8.8.8.8') }} {{ mask }}
    </group>
    
    <group name="interfaces_rdns_add_field">
    interface {{ interface }}
     ip address {{ ip | rdns(add_field='FQDN') }} {{ mask }}
    </group>
    
Result::

    [
        {
            "interfaces_rdns_add_field": {
                "FQDN": "dns.google",
                "interface": "GigabitEthernet3/11",
                "ip": "8.8.8.8",
                "mask": "255.255.255.255"
            },
            "interfaces_rdnsv4": {
                "interface": "GigabitEthernet3/11",
                "ip": "dns.google",
                "mask": "255.255.255.255"
            },
            "interfaces_rdnsv4_google_server": {
                "interface": "GigabitEthernet3/11",
                "ip": "dns.google",
                "mask": "255.255.255.255"
            }
        }
    ]
    
sformat
------------------------------------------------------------------------------
``{{ name | sformat("string_to_format") }}``

* string_to_format - string to format with match result

sformat allows to embed match result within arbitrary string using syntaxis supported by python built-in format function.

**Example**

Template::

    <input load="text">
    interface Vlan778
     ip address 2002:fd37::91/124
    !
    </input>
    
    <group name="interfaces">
    interface {{ interface }}
     ip address {{ ip | sformat("ASN 65100 IP - {}") }}
    </group>

Results::

    [
        {
            "interfaces": {
                "interface": "Vlan778",
                "ip": "ASN 65100 IP - 2002:fd37::91/124"
            }
        }
    ]

uptimeparse
------------------------------------------------------------------------------
``{{ name | uptimeparse }}`` or ``{{ name | uptimeparse(format="seconds|dict") }}``

This function can be used to parse text strings of below format to extract uptime information::

    2 years, 5 months, 27 weeks, 3 days, 10 hours, 46 minutes
    27 weeks, 3 days, 10 hours, 46 minutes
    10 hours, 46 minutes
    1 minutes
    
Arguments:

* ``format`` - default is seconds, optional argument to specify format of returned results, if seconds - integer, number of seconds will be returned, if dict - will return a dictionary of extracted time

    
**Example**

Template::

    <input load="text">
    device-hostame uptime is 27 weeks, 3 days, 10 hours, 46 minutes, 10 seconds
    </input>
    
    <group name="uptime-1-seconds">
    device-hostame uptime is {{ uptime | PHRASE | uptimeparse }}
    </group>
    
    <group name="uptime-2-dictionary">
    device-hostame uptime is {{ uptime | PHRASE | uptimeparse(format="dict") }}
    </group>

Results::

    [
        {
            "uptime-1-seconds": {
                "uptime": 16627570
            },
            "uptime-2-dictionary": {
                "uptime": {
                    "days": "3",
                    "hours": "10",
                    "mins": "46",
                    "secs": "10",
                    "weeks": "27"
                }
            }
        }
    ]
    
mac_eui
------------------------------------------------------------------------------
``{{ name | mac_eui }}``

This function normalizes mac address representation format by deleting ``-:.`` characters from mac address string and converting it into aa:bb:cc:dd:ee:ff. It also handles the case when mac address trailing zeros stripped by device in show commands output, by staffing zeros to make mac address 12 symbols long, e.g. aabb.ccdd.ee will be converted to aa:bb:cc:dd:ee:00