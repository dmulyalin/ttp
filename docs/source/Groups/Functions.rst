Functions
===============

Group functions can be applied to group results to transform them in a desired way, functions can also be used to validate and filter match results. 

Condition functions help to evaluate group results and return *False* or *True*, if *False* returned, group results will be discarded.
  
.. list-table:: group functions
   :widths: 10 90
   :header-rows: 1

   * - Name
     - Description
   * - `containsall`_ 
     - checks if group result contains matches for all given variables
   * - `contains`_ 
     - checks if group result contains match at least for one of given variables
   * - `macro`_   
     - Name of the macros function to run against group result 
   * - `group functions`_   
     - String containing list of functions to run this group results through
   * - `to_ip`_   
     - transforms given values in ipaddress IPAddress object
   * - `exclude`_   
     - invalidates group results if **any** of given keys present in group
   * - `excludeall`_   
     - invalidates group results if **all** given keys present in group
   * - `del`_   
     - delete given keys from group results
   * - `sformat`_   
     - format provided string with match result and/or template variables 
   * - `itemize`_   
     - produce list of items extracted out of group match results dictionary 
     
containsall
------------------------------------------------------------------------------
``containsall="variable1, variable2, variableN"``

* variable (mandatory) - a comma-separated string that contains match variable names. This function
    checks if group results contain specified variable, if at least one variable not found in results, whole group
    result discarded

**Example**

For instance we want to get results only for interfaces that has IP address configured on them **and** vrf, 
all the rest of interfaces should not make it to results.

Data::

    interface Port-Chanel11
      description Storage Management
    !
    interface Loopback0
      description RID
      ip address 10.0.0.3/24
    !
    interface Vlan777
      description Management
      ip address 192.168.0.1/24
      vrf MGMT

Template::

    <group name="interfaces" containsall="ip, vrf">
    interface {{ interface }}
      description {{ description }}
      ip address {{ ip }}/{{ mask }}
      vrf {{ vrf }}
    </group>

Result::

    {
        "interfaces": {
            "description": "Management",
            "interface": "Vlan777",
            "ip": "192.168.0.1",
            "mask": "24",
            "vrf": "MGMT"
        }
    }

contains
------------------------------------------------------------------------------
``contains="variable1, variable2, variableN"``

* variable (mandatory) - a comma-separated string that contains match variable names. This function
    checks if group results contains *any* of specified variable, if no variables found in results, whole group
    result discarded, if at least one variable found in results, this check is satisfied.

**Example**

For instance we want to get results only for interfaces that has IP address configured on them **or** vrf.

Data::

    interface Port-Chanel11
      description Storage Management
    !
    interface Loopback0
      description RID
      ip address 10.0.0.3/24
    !
    interface Vlan777
      description Management
      ip address 192.168.0.1/24
      vrf MGMT

Template::

    <group name="interfaces" contains="ip, vrf">
    interface {{ interface }}
      description {{ description }}
      ip address {{ ip }}/{{ mask }}
      vrf {{ vrf }}
    </group>

Result::

    {
        "interfaces": [
            {
                "description": "RID",
                "interface": "Loopback0",
                "ip": "10.0.0.3",
                "mask": "24"
            },
            {
                "description": "Management",
                "interface": "Vlan777",
                "ip": "192.168.0.1",
                "mask": "24",
                "vrf": "MGMT"
            }
        ]
    }
    
macro
------------------------------------------------------------------------------
``macro="name1, name2, ... , nameN"``

* nameN - comma separated string of macro tag names that should be used to run group results through. The sequence of macroses provided *preserved* and macroses executed in specified order, in other words macro named name2 will run after macro name1.

Macro brings Python language capabilities to match results processing and validation during ttp module execution, as it allows to run custom python functions against match results. Macro functions referenced by their name in match variable definitions.

Macro function must accept only one attribute to hold group results, for groups data supplied to macro function is a dictionary of data matched by this group.

Depending on data returned by macro function, ttp will behave differently according to these rules:

* If macro returns True or False - original data unchanged, macro handled as condition functions, invalidating result on False and keeps processing result on True
* If macro returns None - data processing continues, no additional logic associated
* If macro returns single item - that item replaces original data supplied to macro and processed further

**Example**

Template::

    <input load="text">
    interface GigabitEthernet1/1
     description to core-1
    !
    interface Vlan222
     description Phones vlan
    !
    interface Loopback0
     description Routing ID loopback
    !
    </input>
    
    <macro>
    def check_if_svi(data):
        if "Vlan" in data["interface"]:
            data["is_svi"] = True
        else:
            data["is_svi"] = False
        return data
            
    def check_if_loop(data):
        if "Loopback" in data["interface"]:
            data["is_loop"] = True
        else:
            data["is_loop"] = False
        return data
    </macro>
     
    <macro>
    def description_mod(data):
        # function to revert words order in descripotion
        words_list = data.get("description", "").split(" ")
        words_list_reversed = list(reversed(words_list))
        words_reversed = " ".join(words_list_reversed) 
        data["description"] = words_reversed
        return data
    </macro>
     
    <group name="interfaces_macro" macro="description_mod, check_if_svi, check_if_loop">
    interface {{ interface }}
     description {{ description | ORPHRASE }}
     ip address {{ ip }} {{ mask }}
    </group>

Result::

    [
        {
            "interfaces_macro": [
                {
                    "description": "core-1 to",
                    "interface": "GigabitEthernet1/1",
                    "is_loop": false,
                    "is_svi": false
                },
                {
                    "description": "vlan Phones",
                    "interface": "Vlan222",
                    "is_loop": false,
                    "is_svi": true
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
    
group functions
------------------------------------------------------------------------------
``functions="function1('attributes') | function2('attributes') | ... | functionN('attributes')"``

* functionN - name of the group function together with it's attributes

The main advantage of using string of functions against defining functions directly in the group tag is the fact that it allows to define sequence of functions to run group results through and that order will be honored. For instance we have two below group definitions:

Group1::

    <group name="interfaces_macro" functions="contains('ip') | macro('description_mod') | macro('check_if_svi') | macro('check_if_loop')">
    interface {{ interface }}
     description {{ description | ORPHRASE }}
     ip address {{ ip }} {{ mask }}
    </group>

Group2::

    <group name="interfaces_macro" contains="ip" macro="description_mod, check_if_svi, check_if_loop">
    interface {{ interface }}
     description {{ description | ORPHRASE }}
     ip address {{ ip }} {{ mask }}
    </group>

While above groups have same set of functions defined, for Group1 function will run in provided order, while for Group2 order is undefined due to the fact that XML tag attributes loaded in python dictionary, meaning that key-value mappings are unordered.

.. warning:: pipe '|' symbol must be used to separate function names, not comma

**Example**

Template::

    <input load="text">
    interface GigabitEthernet1/1
     description to core-1
     ip address 192.168.123.1 255.255.255.0
    !
    interface Vlan222
     description Phones vlan
    !
    interface Loopback0
     description Routing ID loopback
     ip address 192.168.222.1 255.255.255.0
    !
    </input>
    
    <macro>
    def check_if_svi(data):
        if "Vlan" in data["interface"]:
            data["is_svi"] = True
        else:
            data["is_svi"] = False
        return data
            
    def check_if_loop(data):
        if "Loopback" in data["interface"]:
            data["is_loop"] = True
        else:
            data["is_loop"] = False
        return data
    </macro>
     
    <macro>
    def description_mod(data):
        # To revert words order in descripotion
        words_list = data.get("description", "").split(" ")
        words_list_reversed = list(reversed(words_list))
        words_reversed = " ".join(words_list_reversed) 
        data["description"] = words_reversed
        return data
    </macro>
     
    <group name="interfaces_macro" functions="contains('ip') | macro('description_mod') | macro('check_if_svi') | macro('check_if_loop')">
    interface {{ interface }}
     description {{ description | ORPHRASE }}
     ip address {{ ip }} {{ mask }}
    </group>
    
Result::

    [
        {
            "interfaces_macro": [
                {
                    "description": "core-1 to",
                    "interface": "GigabitEthernet1/1",
                    "ip": "192.168.123.1",
                    "is_loop": false,
                    "is_svi": false,
                    "mask": "255.255.255.0"
                },
                {
                    "description": "loopback ID Routing",
                    "interface": "Loopback0",
                    "ip": "192.168.222.1",
                    "is_loop": true,
                    "is_svi": false,
                    "mask": "255.255.255.0"
                }
            ]
        }
    ]

to_ip
------------------------------------------------------------------------------
``functions="to_ip(ip_key='X', mask_key='Y')"`` or ``to_ip="'X', 'Y'"`` or ``to_ip="ip_key='X', mask_key='Y'"``

* ip_key - name of the key that contains IP address string
* mask_key - name of the key that contains mask string

This functions can help to construct ipaddress IpAddress object out of ip_key and mask_key values, on success this function will return ipaddress object assigned to ip_key.

**Example**

Template::

    <input load="text">
    interface Loopback10
     ip address 192.168.0.10  subnet mask 24
    !
    interface Vlan710
     ip address 2002::fd10 subnet mask 124
    !
    </input>
    
    <group name="interfaces_with_funcs" functions="to_ip('ip', 'mask')">
    interface {{ interface }}
     ip address {{ ip }}  subnet mask {{ mask }}
    </group>
    
    <group name="interfaces_with_to_ip_args" to_ip = "'ip', 'mask'">
    interface {{ interface }}
     ip address {{ ip }}  subnet mask {{ mask }}
    </group>
    
    <group name="interfaces_with_to_ip_kwargs" to_ip = "ip_key='ip', mask_key='mask'">
    interface {{ interface }}
     ip address {{ ip }}  subnet mask {{ mask }}
    </group>

Results::

    [   {   'interfaces_with_funcs': [   {   'interface': 'Loopback10',
                                             'ip': IPv4Interface('192.168.0.10/24'),
                                             'mask': '24'},
                                         {   'interface': 'Vlan710',
                                             'ip': IPv6Interface('2002::fd10/124'),
                                             'mask': '124'}],
            'interfaces_with_to_ip_args': [   {   'interface': 'Loopback10',
                                                  'ip': IPv4Interface('192.168.0.10/24'),
                                                  'mask': '24'},
                                              {   'interface': 'Vlan710',
                                                  'ip': IPv6Interface('2002::fd10/124'),
                                                  'mask': '124'}],
            'interfaces_with_to_ip_kwargs': [   {   'interface': 'Loopback10',
                                                    'ip': IPv4Interface('192.168.0.10/24'),
                                                    'mask': '24'},
                                                {   'interface': 'Vlan710',
                                                    'ip': IPv6Interface('2002::fd10/124'),
                                                    'mask': '124'}]}]
                                                    
exclude
------------------------------------------------------------------------------
``exclude="variable1, variable2, ..., variableN"``

* variableN - name of the variable on presence of which to invalidate/exclude group results

This function allows to invalidate group match results based on the fact that **any** of the given variable names/keys are present. 

**Example**

Here groups with either ``ip`` or ``description`` variables matches, will be excluded from results.

Template::

    <input load="text">
    interface Vlan778
     description some description 1
     ip address 2002:fd37::91/124
    !
    interface Vlan779
     description some description 2
    !
    interface Vlan780
     switchport port-security mac 4
    !
    </input>

    <group name="interfaces" exclude="ip, description">
    interface {{ interface }}
     ip address {{ ip }}/{{ mask }}
     description {{ description | ORPHRASE }}
     switchport port-security mac {{ sec_mac }}
    </group>
    
Results::

    [
        {
            "interfaces": {
                "interface": "Vlan780",
                "sec_mac": "4"
            }
        }
    ]

excludeall
------------------------------------------------------------------------------
``excludeall="variable1, variable2, ..., variableN"``

* variable - name of the variable on presence of which to invalidate/exclude group results

excludeall allows to invalidate group results based on the fact that **all** of the given variable names/keys are present in match results. 

del
------------------------------------------------------------------------------
``del="variable1, variable2, ..., variableN"``

* variableN - name of the variable to delete results for

**Example**

Template::

    <input load="text">
    interface Vlan778
     description some description 1
     ip address 2002:fd37::91/124
    !
    interface Vlan779
     description some description 2
    !
    interface Vlan780
     switchport port-security mac 4
    !
    </input>
    
    <group name="interfaces-test1-31" del="description, ip">
    interface {{ interface }}
     ip address {{ ip }}/{{ mask }}
     description {{ description | ORPHRASE }}
     switchport port-security mac {{ sec_mac }}
    </group>
    
Results::

    [
        {
            "interfaces-test1-31": [
                {
                    "interface": "Vlan778",
                    "mask": "124"
                },
                {
                    "interface": "Vlan779"
                },
                {
                    "interface": "Vlan780",
                    "sec_mac": "4"
                }
            ]
        }
    ]
    
sformat
------------------------------------------------------------------------------
``sformat="string='text', add_field='name'"`` or ``sformat="'text', 'name'"``

* string - mandatory, string to format
* add_field - mandatory, name of new field with value produced by sformat to add to group results

sformat (string format) method used to form string in certain way using template variables and group match results. The order of variables to use for formatting is:

    1 global variables produced by :ref:`Match Variables/Functions:record` function
    2 template variables as specified in <vars> tag
    3 group match results
    
Next variables in above list override the previous one.

**Example**

Template::

    <vars>
    domain = "com"
    </vars>
    
    <input load="text">
    switch-1 uptime is 27 weeks, 3 days, 10 hours, 46 minutes, 10 seconds
    </input>
    
    <input load="text">
    Default domain is lab.local
    </input>
    
    <group name="uptime">
    {{ hostname | record("hostname")}} uptime is {{ uptime | PHRASE }}
    </group>
    
    <group name="fqdn_dets_1" sformat="string='{hostname}.{fqdn},{domain}', add_field='fqdn'">
    Default domain is {{ fqdn }}
    </group>

Results::

    [
        {
            "uptime": {
                "hostname": "switch-1",
                "uptime": "27 weeks, 3 days, 10 hours, 46 minutes, 10 seconds"
            }
        },
        {
            "fqdn_dets_1": {
                "fqdn": "switch-1.lab.local,com"
            }
        }
    ]
    
string ``{hostname}.{fqdn},{domain}`` formatted using ``hostname`` variable from globally recorded vars, ``fqdn`` variable from group match results and ``domain`` variable defined in template vars. In this example ``add_field`` was set to ``fqdn`` to override fqdn match variable matched values

itemize
------------------------------------------------------------------------------
``itemize="key='name', path='path.to.result'"`` or ``functions="itemize(key='name', path='path.to.result')"``

* key - mandatory, name of the key to use create a list of items from
* path - optional, by default path taken from group name attribute, dot separated string of there to save a list of items within results tree

This function allows to take single item result from group match results and place it into the list at path provided. Motivation behind this function is to be able to provide create a list of items out of match results produced by group. For instance produce a list of all IPs configured on device or VRFs or OSPF processes etc. without the need to iterate over parsing results to extract items in question.

**Example**

Let's say we need to extract a list of all interfaces configured on device.

Template::

    <input load="text">
    interface Vlan778
     description some description 1
     ip address 2002:fd37::91/124
    !
    interface Vlan779
     description some description 2
    !
    interface Vlan780
     switchport port-security mac 4
     ip address 192.168.1.1/124
    !
    </input>
    
    <group name="interfaces_list" itemize="interface">
    interface {{ interface }}
     ip address {{ ip }}
    </group>

Results::

    [
        {
            "interfaces_list": [
                "Vlan778",
                "Vlan779",
                "Vlan780"
            ]
        }
    ]