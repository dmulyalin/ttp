Groups
======

Groups are a core component of TTP, together with match variables. A group is a collection of regular expressions derived from a template. Groups are denoted using the XML group tag (``<g>``, ``<grp>``, or ``<group>``) and can be nested to form a hierarchy. Parsing results for each group are combined into a single datum — a dictionary — which is then merged with the broader results data.

As TTP was developed primarily for parsing semi-structured configuration data from networking devices, the groups concept reflects that most configuration data can be divided into distinct pieces of information, each representing a particular property or feature, further broken down into smaller repetitive data. TTP groups combine regular expressions for parsing these small, repetitive pieces of text.

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
