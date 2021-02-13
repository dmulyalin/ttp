.. _path_formatters:

Path formatters
===============

By default ttp assumes that all the *path items* must be joined into a dictionary structure, in other words group name "item1.item2.item3" will be transformed into nested dictionary::

    {"item1": 
	 {"item2": 
	  {"item3": {}
    	}
      }
    }

That structure will be populated with results as parsing progresses, but in case if for "item3" more than single result datum needs to be saved, ttp will transform "item3" child to list and save further results by appending them to that list. That process happens automatically but can be influenced using *path formatters*.

Supported path formatters \* and \*\* for group *name* attribute can be used following below rules:

* If single start character \* used as a suffix (appended to the end) of path item, next level (child) of this path item always will be a list
* If double start character \*\* used as a suffix (appended to the end) of path item, next level (child) of this path item always will be a dictionary

**Example**

Consider this group with name attribute formed in such a way that interfaces item child will be a list and child of L3 path item also will be a list.::

    <group name="interfaces*.vlan.L3*.vrf-enabled">
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
            "interfaces": [              <----this is the start of nested list
                {
                    "vlan": {
                        "L3": [          <----this is the start of another nested list
                            {
                                "vrf-enabled": {
                                    "description": "Management",
                                    "interface": "Vlan777",
                                    "ip": "192.168.0.1",
                                    "mask": "24",
                                    "vrf": "MGMT"
                                }
                            }
                        ]
                    }
                }
            ]
        }
    ]