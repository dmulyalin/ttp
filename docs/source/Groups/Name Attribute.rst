Name Attribute
==============

Group attribute *name* used to uniquely identify group and its results within results structure. This attribute is a dot separated string, there is every dot represents a next level in hierarchy. This string is split into **path items** using dot character and converted into nested hierarchy of dictionaries and/or lists.

Consider a group with this name attribute value::

    <group name="interfaces.vlan.L3.vrf-enabled">
    interface {{ interface }}
      description {{ description }}
      ip address {{ ip }}/{{ mask }}
      vrf {{ vrf }}
    </group>
	
If below data parsed with that template::

    interface Vlan777
      description Management
      ip address 192.168.0.1/24
      vrf MGMT
	  
This result will be produced::

    [
        {
            "interfaces": {
                "SVIs": {
                    "L3": {
                        "vrf-enabled": {
                            "description": "Management",
                            "interface": "Vlan777",
                            "ip": "192.168.0.1",
                            "mask": "24",
                            "vrf": "MGMT"
                        }
                    }
                }
            }
        }
    ]
	
Name attribute allows to from arbitrary (from practical perspective) depth structure in deterministic fashion, enabling further programmatic consumption of produced results.

Path formatters
---------------

By default ttp assumes that all the *path items* must be joined into a dictionary structure, in other words group name "item1.item2.item3" will be transformed into nested dictionary::

    {"item1": 
	 {"item2": 
	  {"item3": {}
    	}
      }
    }

That structure will be populated with results as parsing progresses, but in case if for "item3" more than single result datum needs to be saved, ttp will transform "item3" child to list and save further results by appending them to that list. That process happens automatically but can be influenced using *path formatters*.

Supported path formatters \* and \*\* for group *name* attribute can be used following below rules:

* If single start character \* used as a suffix (appended to the end) of path item, next level (child) of this path item always will be a list
* If double start character \*\* used as a suffix (appended to the end) of path item, next level (child) of this path item always will be a dictionary

**Example**

Consider this group with name attribute formed in such a way that interfaces item child will be a list and child of L3 path item also will be a list.::

    <group name="interfaces*.vlan.L3*.vrf-enabled">
    interface {{ interface }}
      description {{ description }}
      ip address {{ ip }}/{{ mask }}
      vrf {{ vrf }}
    </group>
	
If below data parsed with that template::

    interface Vlan777
      description Management
      ip address 192.168.0.1/24
      vrf MGMT
	  
This result will be produced::

    [
        {
            "interfaces": [              <----this is the start of nested list
                {
                    "vlan": {
                        "L3": [          <----this is the start of another nested list
                            {
                                "vrf-enabled": {
                                    "description": "Management",
                                    "interface": "Vlan777",
                                    "ip": "192.168.0.1",
                                    "mask": "24",
                                    "vrf": "MGMT"
                                }
                            }
                        ]
                    }
                }
            ]
        }
    ]
		
Dynamic Path
------------

Above are examples of static path, where all the path items are known and predefined beforehand, however, ttp supports dynamic path formation using match variable results for certain match variable names, i.e we have match variable name set to *interface* and correspondent match result would be Gi0/1, it is possible to use Gi0/1 as a path item. 

Search for dynamic path item value happens using below sequence:

* *First* - group match results searched for path item value, 
* *Second* - upper group results cache (latest values) used,
* *Third* - template variables searched for path item value,
* *Last* - group results discarded as invalid

Dynamic path items specified in group *name* attribute using "*{{ item_name }}*" format, there "*{{ item_name }}*" dynamically replaced with value found using above sequence.

**Example-1**

In this example interface variable match values will be used to substitute {{ interface }} dynamic path items.

Data::

    interface Port-Chanel11
      description Storage
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

    <group name="interfaces.{{ interface }}">
    interface {{ interface }}
      description {{ description }}
      ip address {{ ip }}/{{ mask }}
      vrf {{ vrf }}
    </group>
	  
Result::

    [
        {
            "interfaces": {
                "Loopback0": {
                    "description": "RID",
                    "ip": "10.0.0.3",
                    "mask": "24"
                },
                "Port-Chanel11": {
                    "description": "Storage"
                },
                "Vlan777": {
                    "description": "Management",
                    "ip": "192.168.0.1",
                    "mask": "24",
                    "vrf": "MGMT"
                }
            }
        }
    ]
	
Because each path item is a string, and each item produced by spilling name attributes using '.' dot character, it is possible to produce dynamic path there portions of path item will be dynamically substituted.


Data::

    interface Port-Chanel11
      description Storage
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

    <group name="interfaces.cool_{{ interface }}_interface">
    interface {{ interface }}
      description {{ description }}
      ip address {{ ip }}/{{ mask }}
      vrf {{ vrf }}
    </group>
	  
Result::

    [
        {
            "interfaces": {
                "cool_Loopback0_interface": {
                    "description": "RID",
                    "ip": "10.0.0.3",
                    "mask": "24"
                },
                "cool_Port-Chanel11_interface": {
                    "description": "Storage"
                },
                "cool_Vlan777_interface": {
                    "description": "Management",
                    "ip": "192.168.0.1",
                    "mask": "24",
                    "vrf": "MGMT"
                }
            }
        }
    ]
	
.. note:: 
 
  Substitution of dynamic path items happens using re.sub method without the limit set on the count of such a substitutions, e.g. if path item "cool_{{ interface }}_interface_{{ interface }}" and if interface value is "Gi0/1" resulted path item will be "cool_Gi0/1_interface_Gi0/1"
	
Nested hierarchies also supported with dynamic path, as if no variable found in the group match results ttp will try to find variable in the dynamic path cache or template variables.

**Example-3**

Data::

    ucs-core-switch-1#show run | section bgp
    router bgp 65100
      vrf CUST-1
        neighbor 59.100.71.193
          remote-as 65101
          description peer-1
          address-family ipv4 unicast
            route-map RPL-1-IMPORT-v4 in
            route-map RPL-1-EXPORT-V4 out
          address-family ipv6 unicast
            route-map RPL-1-IMPORT-V6 in
            route-map RPL-1-EXPORT-V6 out
        neighbor 59.100.71.209
          remote-as 65102
          description peer-2
          address-family ipv4 unicast
            route-map AAPTVRF-LB-BGP-IMPORT-V4 in
            route-map AAPTVRF-LB-BGP-EXPORT-V4 out
	  
Template::

    <vars>
    hostname = "gethostname"
    </vars>
    
    <group name="{{ hostname }}.router.bgp.BGP_AS_{{ asn }}">
    router bgp {{ asn }}
      <group name="vrfs.{{ vrf_name }}">
      vrf {{ vrf_name }}
        <group name="peers.{{ peer_ip }}">
        neighbor {{ peer_ip }}
          remote-as {{ peer_asn }}
          description {{ peer_description }}
    	  <group name="afi.{{ afi }}.unicast">
          address-family {{ afi }} unicast
            route-map {{ rpl_in }} in
            route-map {{ rpl_out }} out
    	  </group>
    	</group>
       </group>
    </group>
	
Result::

    - ucs-core-switch-1:
        router:
          bgp:
            BGP_AS_65100:
              vrfs:
                CUST-1:
                  peers:
                    59.100.71.193:
                      afi:
                        ipv4:
                          unicast:
                            rpl_in: RPL-1-IMPORT-v4
                            rpl_out: RPL-1-EXPORT-V4
                        ipv6:
                          unicast:
                            rpl_in: RPL-1-IMPORT-V6
                            rpl_out: RPL-1-EXPORT-V6
                      peer_asn: '65101'
                      peer_description: peer-1
                    59.100.71.209:
                      afi:
                        ipv4:
                          unicast:
                            rpl_in: RPL-2-IMPORT-V6
                            rpl_out: RPL-2-EXPORT-V6
                      peer_asn: '65102'
                      peer_description: peer-2
					  
Dynamic path with path formatters
---------------------------------					  
	
Dynamic path with path formatters is also supported. In example below child for *interfaces* will be a list.

**Example**

Data::

    interface Port-Chanel11
      description Storage
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

    <group name="interfaces*.{{ interface }}">
    interface {{ interface }}
      description {{ description }}
      ip address {{ ip }}/{{ mask }}
      vrf {{ vrf }}
    </group>
	  
Result::

    [
        {
            "interfaces": [
                {
                    "Loopback0": {
                        "description": "RID",
                        "ip": "10.0.0.3",
                        "mask": "24"
                    },
                    "Port-Chanel11": {
                        "description": "Storage"
                    },
                    "Vlan777": {
                        "description": "Management",
                        "ip": "192.168.0.1",
                        "mask": "24",
                        "vrf": "MGMT"
                    }
                }
            ]
        }
    ]

No name attribute
-----------------

If no nested functionality required or results structure needs to be kept as flat as possible, templates without <group> tag can be used - so called *non hierarchical templates*. 

There is a notion of *top* <group> tag exists, that at the tag that located in the top of xml document hierarchy,  that tag can be lacking name attribute as well. 

In both cases above, ttp will automatically reconstruct <group> tag and name attribute for it, setting name to "_anonymous_" value. At the end _anonymous_ path will be stripped of results tree to flatten it.

.. note::

    <group> tag without name attribute does have support for all the other group attributes as well as nested groups, however, nested groups *must* have name attribute set on them otherwise nested hierarchy will not be preserved leading to unpredictable results. 
	
.. warning::
    
	Template variables name attribute ignored if groups with "_anonymous_" path used, as a result template variables will not be save into results.

**Example**

Example for <group> without *name* attribute.

Data::

    interface Port-Chanel11
      description Storage
    !
    interface Loopback0
      description RID
      ip address 10.0.0.3/24
    !
    interface Vlan777
      description Management
      ip address 192.168.0.1/24
      vrf MGMT
    !
	
Template::

    <group>
    interface {{ interface }}
      description {{ description }}
    <group name = "ips">
      ip address {{ ip }}/{{ mask }}
    </group>
      vrf {{ vrf }}
    !{{_end_}}
    </group>
	
Result::

    [
        {
            "description": "Storage",
            "interface": "Port-Chanel11"
        },
        {
            "description": "RID",
            "interface": "Loopback0",
            "ips": {
                "ip": "10.0.0.3",
                "mask": "24"
            }
        },
        {
            "description": "Management",
            "interface": "Vlan777",
            "ips": {
                "ip": "192.168.0.1",
                "mask": "24"
            },
            "vrf": "MGMT"
        }
    ]