Input tag attributes
====================

There are a number of attributes can be specified in input tag, these attributes help to define input behavior and how data should be loaded and parsed.

.. list-table:: 
   :widths: 10 90
   :header-rows: 1

   * - Attribute
     - Description
   * - `name`_   
     - Uniquely identifies input within template
   * - `groups`_   
     - Specifies group(s) that should be used to parse input data
   * - `load`_   
     - Identifies loader that should be used to load text data for input tag itself
   * - `preference`_   
     - specify preference on how to handle inputs' groups and groups' input
	 
name
------------------------------------------------------------------------
``name="string"``

* string (optional) - name of the input to reference in group *input* attribute. Default value is "Default_Input" and used internally to store set of data that should be parsed by all groups.

groups
------------------------------------------------------------------------
``groups="group1, group2, ... , groupN"``

* groupN (optional) - Default value is "all", comma separated string of group names that should be used to parse given input data. Default value is "all" - input data will be parsed by each group. 

Each group will be used only once to parse input data, for instance if ``groups="group1, group1"``, group1 will be parse that input data only once, as TTP makes a list of unique (non repeating values, internally, that achieved by converting list to set and back to sorted list) groups for each input.

.. note:: Group tag :ref:`Groups/Attributes:input` attribute can be used to reference inputs' names or OS path to files, it is considered to be more specific, for example when several groups in the  template have identical *name* attribute, referencing these groups by name in input tag *groups* attribute will result in input data to be parsed by all the groups with that name, on the other hand, if input name referenced in group tag *input* attribute, data of this input will only be parsed by this group even if several group have the same name.

load
------------------------------------------------------------------------
``load="loader_name"``

* loader_name - name of the loader that should be used to load input tag text data, supported values are ``python, yaml, json or text``, if text used as a loader, text data within input tag itself used as an input data and parsed by a set of given groups or by all groups.

**Example**

Below template contains input with text data that should be parsed, that is useful for testing purposes or for small data sets.

Template::

    <input name="test1" load="text" groups="interfaces.trunks">
    interface GigabitEthernet3/3
     switchport trunk allowed vlan add 138,166-173 
    !
    interface GigabitEthernet3/4
     switchport trunk allowed vlan add 100-105
    !
    interface GigabitEthernet3/5
     switchport trunk allowed vlan add 459,531,704-707
    </input>
    
    <group name="interfaces.trunks">
    interface {{ interface }}
     switchport trunk allowed vlan add {{ trunk_vlans }}
    </group>

Result::

    [
        {
            "interfaces": {
                "trunks": [
                    {
                        "interface": "GigabitEthernet3/3",
                        "trunk_vlans": "138,166-173"
                    },
                    {
                        "interface": "GigabitEthernet3/4",
                        "trunk_vlans": "100-105"
                    },
                    {
                        "interface": "GigabitEthernet3/5",
                        "trunk_vlans": "459,531,704-707"
                    }
                ]
            }
        }
    ]
    
preference
------------------------------------------------------------------------
``preference="merge|group_inputs|input_groups"``

One of the main purposes of Inputs is to define data to groups mappings, in other words - to define that this set of files/data need to be parsed by this group(s). There are two ways to define that mapping:

    1 Use Input tag `groups`_ attribute to list names of all groups that should be used to parse input's data, default value for input groups is ``all``
	2 Use Groups :ref:`Groups/Attributes:input` attribute to define a list of inputs that this group should process
	
By default groups ``inputs`` (method 2) has higher preference compared to input groups (method 1), this is due to the fact that groups name attribute might not be unique across the template, moreover by default input ``groups`` value set to ``all``, meaning we will have overlap between the set of groups matched by input groups and group inputs. Hence decision logic in place making groups ``inputs`` more preferred. 

Preference attribute helps to influence decision logic above if needed. For instance if preference set to ``input_groups`` then groups ``inputs`` will be ignored, if set to merge then combination of unique values of groups matched by input ``groups`` and groups ``input`` attributes will be used.

**Example**

Template::

