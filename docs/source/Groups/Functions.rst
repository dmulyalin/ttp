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
   * - `cerberus`_   
     - function to run results through Cerberus validation engine
   * - `void`_   
     - invalidates group results, allowing to skip them
   * - `str_to_unicode`_   
     - converts Python2 str srings in unicode strings
   * - `equal`_   
     - verifies that key's value is equal to provided value
   * - `to_int`_   
     - converts given keys to integer (int or float) or tries to convert all match result values
   * - `contains_val`_   
     - check if certain key contains certain value, return True if so and False otherwise
   * - `exclude_val`_   
     - check if certain key contains certain value, return False if so and True otherwise
     
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

* nameN - comma separated string of macro functions names that should be used to run group results through. The sequence is *preserved* and macros executed in specified order, in other words macro named name2 will run after macro name1.

Macro brings Python language capabilities to group results processing and validation during TTP module execution, as it allows to run custom python functions. Macro functions referenced by their name in group tag definitions.

Macro function must accept only one attribute to hold group match results.

Depending on data returned by macro function, TTP will behave differently according to these rules:

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
    
cerberus
------------------------------------------------------------------------------
``cerberus="schema='var_name', log_errors=False, allow_unknown=True, add_errors=False"``

* schema - string, mandatory, name of template variable that contains Cerberus schema structure
* log_errors - bool, default is False, if set to True will log Cerberus validation errors with WARNING level
* allow_unknown - bool, default is True, if set to False, Cerberus will invalidate match results with keys that are not defined in schema
* add_errors - bool, default is False, if set to True, Cerberus validation errors will be added to results under "validation_errors" key

**Prerequisites**

`Cerberus library <https://docs.python-cerberus.org/en/stable/>`_ need to be installed on the system.

This function uses `Cerberus validation engine <https://docs.python-cerberus.org/en/stable/>`_ to validate group results, returning True if validation succeeded and False otherwise. 

This function makes use of Cerberus Validation class, and schema must be defined in one of template variables sections.

**Example**

Let's say we want to extract information only for interfaces that satisfy these set of criteria:

* has "Gigabit" in the name
* contains "Customer" in description
* dot1q vlan id is in 200-300 range 
* interface belongs to one of these VRFs - "Management" or "Data"

Template::

    <input load="text">
    interface GigabitEthernet1/3.251
     description Customer #32148
     encapsulation dot1q 251
     vrf forwarding Management
     ipv6 address 2002:fd37::91/124
    !
    interface GigabitEthernet1/3.321
     description Customer #151678
     encapsulation dot1q 321
     vrf forwarding Voice
     ip address 172.16.32.10 255.255.255.128
    !
    interface Vlan779
     description South Bank Customer #78295
     vrf forwarding Data
     ip address 192.168.23.53 255.255.255.0
    !
    interface TenGigabitEthernet3/1.298
     description PDSENS Customer #783290
     encapsulation dot1q 298
     vrf forwarding Data
     ipv6 address 2001:ad56::1273/64
    !
    </input>
    
    <vars>
    my_schema = {
        "interface": {
            "regex": ".*Gigabit.*"
        },
        "vrf": {
            "allowed": ["Data", "Management"]
        },
        "description": {
            "regex": ".*Customer.*"
        },
        "vid": {
            "min": 200, 
            "max": 300
        }
    }
    </vars>
    
    <group name="filtered_interfaces*" cerberus="my_schema">
    interface {{ interface }}
     description {{ description | ORPHRASE }}
     encapsulation dot1q {{ vid | to_int }}
     vrf forwarding {{ vrf }}
     ip address {{ ip }} {{ mask }}
     ipv6 address {{ ipv6 }}/{{ maskv6 }} 
    </group>
    
Result::

    [
        [
            {
                "filtered_interfaces": [
                    {
                        "description": "Customer #32148",
                        "interface": "GigabitEthernet1/3.251",
                        "ipv6": "2002:fd37::91",
                        "maskv6": "124",
                        "vid": 251,
                        "vrf": "Management"
                    },
                    {
                        "description": "PDSENS Customer #783290",
                        "interface": "TenGigabitEthernet3/1.298",
                        "ipv6": "2001:ad56::1273",
                        "maskv6": "64",
                        "vid": 298,
                        "vrf": "Data"
                    }
                ]
            }
        ]
    ]
    
By default only results that passed validation criteria will be returned by TTP, however, if ``add_errors`` set to True::

    <group name="filtered_interfaces*" cerberus="schema='my_schema', add_errors=True">
    interface {{ interface }}
     description {{ description | ORPHRASE }}
     encapsulation dot1q {{ vid | to_int }}
     vrf forwarding {{ vrf }}
     ip address {[ ip }} {{ mask }}
     ipv6 address {{ ipv6 }}/{{ maskv6 }} 
    </group>
    
Results produced by TTP will contain validation errors information::

    [
        [
            {
                "filtered_interfaces": [
                    {
                        "description": "Customer #32148",
                        "interface": "GigabitEthernet1/3.251",
                        "ipv6": "2002:fd37::91",
                        "maskv6": "124",
                        "vid": 251,
                        "vrf": "Management"
                    },
                    {
                        "description": "Customer #151678",
                        "interface": "GigabitEthernet1/3.321",
                        "validation_errors": {
                            "vid": [
                                "max value is 300"
                            ],
                            "vrf": [
                                "unallowed value Voice"
                            ]
                        },
                        "vid": 321,
                        "vrf": "Voice"
                    },
                    {
                        "description": "South Bank Customer #78295",
                        "interface": "Vlan779",
                        "validation_errors": {
                            "interface": [
                                "value does not match regex '.*Gigabit.*'"
                            ]
                        },
                        "vrf": "Data"
                    },
                    {
                        "description": "PDSENS Customer #783290",
                        "interface": "TenGigabitEthernet3/1.298",
                        "ipv6": "2001:ad56::1273",
                        "maskv6": "64",
                        "vid": 298,
                        "vrf": "Data"
                    }
                ]
            }
        ]
    ]
    
void
------------------------------------------------------------------------------
``void=""`` or ``functions="void"``

The purpose of this function is to return False on group results validation, effectively allowing to skip results for this group.

str_to_unicode
------------------------------------------------------------------------------
``str_to_unicode=""`` or ``functions="str_to_unicode"``

If python2 used to run TTP, this function iterates over group results and converts strings of type ``str`` into ``unicode`` type strings. For python3 this function does nothing.

equal
------------------------------------------------------------------------------
``equal="key, value"``

* key - name of the key to verify value for
* value - value to verify equality against

This functions check if value of certain key is equal to value provided and returns True is so and False otherwise.

**Example**

Template::

    <input load="text">
    interface FastEthernet1/0/1
     description Foo
    !
    interface FastEthernet1/0/2
     description wlap2
    !
    </input>
    
    <group name="interfaces" equal="description, Foo">
    interface {{ interface }}
     description {{ description }}
    </group>
    
Results::

    [
        [
            {
                "interfaces": {
                    "description": "Foo",
                    "interface": "FastEthernet1/0/1"
                }
            }
        ]
    ]
    
to_int
------------------------------------------------------------------------------
``to_int=""`` or ``to_int="key1, key2, keyN"``

* keyN - name of keys to run conversion for, if omitted, all group match results items will be attempted to convert into integer.

This function tries to convert string representation of digit into integer using python int() function, if fails it next tries to convert to integer using python float() function. 
If either int() or float() conversion was successful, string converted to digit will replace match result, on failure nothing will be done with match results.

**Example**

Template::

    <input load="text">
    Subscription ID = 1
    Version = 1
    Num Subpackets = 1
    Subpacket[0]
       Subpacket ID = PDCP PDU with Ciphering (0xC3)
       Subpacket Version = 26.1
       Subpacket Size = 60,5 bytes
       SRB Cipher Algo = LTE AES
       DRB Cipher Algo = LTE AES
       Num PDUs = 1
    </input>
    
    <group name="all_to_int" to_int="">
    Subscription ID = {{ Subscription_ID }}
    Version = {{ version }}
    Num Subpackets = {{ Num_Subpackets }}
       Subpacket ID = {{ Subpacket_ID | PHRASE }}
       Subpacket Version = {{ Subpacket_Version }}
       Subpacket Size = {{ Subpacket_Size | PHRASE }}
       SRB Cipher Algo = {{ SRB_Cipher_Algo | PHRASE }}
       DRB Cipher Algo = {{ DRB_Cipher_Algo | PHRASE }}
       Num PDUs = {{ Num_PDUs }}
    </group>
    
    <group name="some_to_int" to_int="version, Subpacket_Version">
    Subscription ID = {{ Subscription_ID }}
    Version = {{ version }}
    Num Subpackets = {{ Num_Subpackets }}
       Subpacket ID = {{ Subpacket_ID | PHRASE }}
       Subpacket Version = {{ Subpacket_Version }}
       Subpacket Size = {{ Subpacket_Size | PHRASE }}
       SRB Cipher Algo = {{ SRB_Cipher_Algo | PHRASE }}
       DRB Cipher Algo = {{ DRB_Cipher_Algo | PHRASE }}
       Num PDUs = {{ Num_PDUs }}
    </group>
    
Results::

    [
        [
            {
                "all_to_int": {
                    "DRB_Cipher_Algo": "LTE AES",
                    "Num_PDUs": 1,
                    "Num_Subpackets": 1,
                    "SRB_Cipher_Algo": "LTE AES",
                    "Subpacket_ID": "PDCP PDU with Ciphering (0xC3)",
                    "Subpacket_Size": "60,5 bytes",
                    "Subpacket_Version": 26.1,
                    "Subscription_ID": 1,
                    "version": 1
                },
                "some_to_int": {
                    "DRB_Cipher_Algo": "LTE AES",
                    "Num_PDUs": "1",
                    "Num_Subpackets": "1",
                    "SRB_Cipher_Algo": "LTE AES",
                    "Subpacket_ID": "PDCP PDU with Ciphering (0xC3)",
                    "Subpacket_Size": "60,5 bytes",
                    "Subpacket_Version": 26.1,
                    "Subscription_ID": "1",
                    "version": 1
                }
            }
        ]
    ]
    
contains_val
------------------------------------------------------------------------------
``contains_val="key, value"``

* ``key`` - name of key to check value for
* ``value`` - value to check against

This function checks if certain key in group results equal to value provided, returning True if so and False otherwise.

**Example**

Template::

    <input load="text">
    interface Vlan779
     ip address 2.2.2.2/24
    !
    interface Vlan780
     ip address 2.2.2.3/24
    !
    </input>
    
    <group name="interfaces" contains_val="'ip', '2.2.2.2/24'">
    interface {{ interface }}
     ip address {{ ip }}
    </group>

Result::

    
    [
        {
            "interfaces": {
                "interface": "Vlan779",
                "ip": "2.2.2.2/24"
            }
        }
    ]
    

exclude_val
------------------------------------------------------------------------------
``exclude_val="key, value"``

* ``key`` - name of key to check value for
* ``value`` - value to check against

This function checks if certain key in group results equal to value provided, returning False if so and True otherwise.