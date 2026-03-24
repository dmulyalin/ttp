Group Name Attribute
====================

The group ``name`` attribute uniquely identifies a group and places its results within the results structure. It is a dot-separated string where each dot represents the next level of hierarchy. The string is split into **path items** using the dot character and converted into a nested hierarchy of dictionaries and/or lists.

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
                "vlan": {
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

The name attribute enables forming an arbitrary-depth structure in a deterministic way, facilitating programmatic consumption of results.
