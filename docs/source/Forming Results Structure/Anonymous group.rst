Anonymous group
===============

If no nested dictionary functionality required or results structure needs to be kept as flat as possible, templates without <group> tag can be used - so called *non hierarchical templates*. 

Top <group> tag can also lack of name attribute, making at anonymous group - group without a name.

In both cases above, TTP will automatically reconstruct <group> tag name attribute making it equal to ``_anonymous_*`` value, note ``*`` path formatter, that is to make sure that anonymous group results will **always be a list**.  

At the end ``_anonymous_`` group results merged with the rest of groups' results. Because of how results combined, template that has anonymous groups will always produce a list results structure.

.. note::

    <group> tag without name attribute does have support for all group attributes and functions as well as nested groups. However, keep in mind that for nested groups name attribute inherited from parent groups.

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
    ]