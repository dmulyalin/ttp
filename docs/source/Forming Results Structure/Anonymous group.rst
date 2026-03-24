Anonymous group
===============

When no nested dictionary hierarchy is required, or results should be kept as flat as possible, templates without a ``<group>`` tag can be used — so-called *non-hierarchical templates*.

A top-level ``<group>`` tag can also omit the ``name`` attribute, making it an anonymous group.

In both cases, TTP automatically sets the group name to ``_anonymous_*`` (note the ``*`` path formatter), which ensures that anonymous group results are **always a list**.

Anonymous group results are merged with the rest of the groups' results at the end. Any template with anonymous groups always produces a list result structure.

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
