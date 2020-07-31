Group Name Attribute
====================

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