Groups
======

Groups are the core component of ttp together with match variables. Group is a collection of regular expressions derived from template, groups denoted using XML group tag (<g>, <grp>, <group>) and can be nested to form hierarchy. Parsing results for each group combined into a single datum - dictionary, that dictionary merged with bigger set of results data.

As ttp was developed primarily for parsing semi-structured configuration data of various network elements, groups concept stems from the fact that majority of configuration data can be divided in distinctive pieces of information, each of which can denote particular property or feature configured on device, moreover, it is not uncommon that these pieces of information can be broken down into even smaller pieces of repetitive data. TTP helps to combine regular expressions in groups for the sake of parsing small, repetitive pieces of text data.

For example, this is how industry standard CLI configuration data for interfaces might look like::

    interface Vlan163
     description [OOB management]
     ip address 10.0.10.3 255.255.255.0
    !
    interface GigabitEthernet6/41
     description [uplink to core]
     ip address 192.168.10.3 255.255.255.0

It is easy to notice that there is a lot of data which is the same and there is a lot of information which is different as well, if we would say that overall device's interfaces configuration is a collection of repetitive data, with interfaces being a smallest available datum, we can outline it in ttp template below and use it parse valuable information from text data::

    <group name="interfaces">
    interface {{ interface }}
     description {{ description | PHRASE }}
     ip address {{ ip }} {{ mask }}
    </group>

After parsing this configuration data with that template results will be::

    [
        {
            "interfaces": [
                {
                    "description": "[OOB management]",
                    "interface": "Vlan163",
                    "ip": "10.0.10.3",
                    "mask": "255.255.255.0"
                },
                {
                    "description": "[uplink to core]",
                    "interface": "GigabitEthernet6/41",
                    "ip": "192.168.10.3",
                    "mask": "255.255.255.0"
                }
            ]
        }
    ]

As a result each interfaces group produced separate dictionary and all interfaces dictionaries were combined in a list under *interfaces* key which is derived from group name.

Group reference
-------------------

.. toctree::
   :maxdepth: 2

   Attributes
   Functions
