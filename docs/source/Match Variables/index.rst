Match Variables
===============

Match variables used as names (keys) for information (values) that needs to be extracted from text data.  Match variables placed within ``{{`` and ``}}`` double curly brackets. For instance::

    <group name="interfaces">
    interface {{ interface }}
     switchport trunk allowed vlan add {{ trunk_vlans }}
    </group>

Match variables are ``interface`` and ``trunk_vlans`` will store matching values extracted from this sample data::

    interface GigabitEthernet3/4
     switchport trunk allowed vlan add 771,893
	!
    interface GigabitEthernet3/5
     switchport trunk allowed vlan add 138,166-173

After parsing, TTP will produce this result::

    [
        {
            "interfaces": {
                "interface": "GigabitEthernet3/4",
                "trunk_vlans": "771,893"
            },
            {
                "interface": "GigabitEthernet3/5",
                "trunk_vlans": "138,166-173"
            }
        }
    ]

Match variables can reference various function to process data during parsing, indicators to change parsing logic or regular expression patterns to use for data parsing. Match variables combined with groups can help to define the way how data parsed, processed and structured.

Match Variables reference
-------------------------

.. toctree::
   :maxdepth: 2

   Indicators
   Functions
   Patterns
