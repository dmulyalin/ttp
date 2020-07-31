Anonymous group
===============

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