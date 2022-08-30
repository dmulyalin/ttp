Match Variables
===============

Match variables are used as names (keys) for information (values) that needs to be extracted from text data.
You can declare a match variable by naming it within double curly brackets, ``{{`` and ``}}``. For instance::

    <group name="interfaces">
    interface {{ interface }}
     switchport trunk allowed vlan add {{ trunk_vlans }}
    </group>

The match variables ``interface`` and ``trunk_vlans`` will store matching values extracted from this sample data::

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

You can also combine match variables with indicators, functions, and/or regular expression patterns.
These help define the way your data is parsed, processed and structured - especially when combined with groups.


Match Variables reference
-------------------------

.. toctree::
   :maxdepth: 2

   Indicators
   Functions
   Patterns
