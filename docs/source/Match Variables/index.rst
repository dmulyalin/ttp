Match Variables
===============

Match variables used to denote names of pieces of information that needs to be extracted from text data. For instance in this template::

    <group name="interfaces">
    interface {{ interface }}
     switchport trunk allowed vlan add {{ trunk_vlans }}
    </group>
	
Match variables must be placed between ``{{`` and ``}}`` double curly brackets, in above example match variables are ``interface`` and ``trunk_vlans`` will store matching results extracted from this text data::

    interface GigabitEthernet3/4
     switchport trunk allowed vlan add 771,893
	!
    interface GigabitEthernet3/5
     switchport trunk allowed vlan add 138,166-173 

In other words, if above data will be parsed with given template, this results will be produced::

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
	
In addition, match variables can be accompanied with various function to process data during parsing or indicators to change parsing logic or regular expression patterns to use for data parsing. Match variables combined with groups can help to define the way how data parsed, processed and combined. 

Match Variables reference
-------------------------

.. toctree::
   :maxdepth: 2
   
   Indicators
   Functions
   Patterns