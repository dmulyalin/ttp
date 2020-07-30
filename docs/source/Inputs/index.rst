Inputs
=======

Inputs can be used to specify data location and how it should be loaded or filtered. Inputs can be attached to groups for parsing, for instance this particular input data should be parsed by this set of groups only. That can help to increase the overall performance as only data belonging to particular group will be parsed. 

.. note:: Order of inputs preserved as internally they represented using OrderedDict object, that can be useful if data produced by first input needs to bused by other inputs.

Assuming we have this folders structure to store data that needs to be parsed::

    /my/base/path/
        Data/
          Inputs/
             data-1/
                sw-1.conf
                sw-1.txt
             data-2/
                sw-2.txt
                sw3.txt                       

Where content::

    [sw-1.conf]
    interface GigabitEthernet3/7
     switchport access vlan 700
    !
    interface GigabitEthernet3/8
     switchport access vlan 800
    !

    [sw-1.txt]
    interface GigabitEthernet3/2
     switchport access vlan 500
    !
    interface GigabitEthernet3/3
     switchport access vlan 600
    !
    
    [sw-2.txt]
    interface Vlan221
      ip address 10.8.14.130/25
    
    interface Vlan223
      ip address 10.10.15.130/25
    
    [sw3.txt]
    interface Vlan220
      ip address 10.9.14.130/24
    
    interface Vlan230
      ip address 10.11.15.130/25

Template below uses inputs in such a way that for "data-1" folder only files that have ".txt" extension will be parsed by group "interfaces1", for input named "dataset-2" only files with names matching "sw\-\d.*" regular expression will be parsed by "interfaces2" group. In addition, base path provided that will be appended to each url within *url* input parameter. Tag text for input "dataset-1" structured using YAML representation, while "dataset-2" uses python language definition.

As a result of inputs filtering, only "sw-1.txt" will be processed by "dataset-1" input because it is the only file that has ".txt" extension, only  "sw-2.txt" will be processed by input "dataset-2" because "sw3.txt" not matched by "sw\-\d.*" regular expression.

Template::

    <template base_path="/my/base/path/">
    <input name="dataset-1" load="yaml" groups="interfaces1">
    url: "/Data/Inputs/data-1/"
    extensions: ["txt"]
    </input>
    
    <input name="dataset-2" load="python" groups="interfaces2">
    url = ["/Data/Inputs/data-2/"]
    filters = ["sw\-\d.*"]
    </input>
    
    <group name="interfaces1">
    interface {{ interface }}
     switchport access vlan {{ access_vlan }}
    </group>
    
    <group name="interfaces2">
    interface {{ interface }}
      ip address {{ ip  }}/{{ mask }}
    </group>
    </template>
    
And result would be::

    [
        {
            "interfaces1": [
                {
                    "access_vlan": "500",
                    "interface": "GigabitEthernet3/2"
                },
                {
                    "access_vlan": "600",
                    "interface": "GigabitEthernet3/3"
                }
            ]
        },
        {
            "interfaces2": [
                {
                    "interface": "Vlan221",
                    "ip": "10.8.14.130",
                    "mask": "25"
                },
                {
                    "interface": "Vlan223",
                    "ip": "10.10.15.130",
                    "mask": "25"
                }
            ]
        }
    ]

Inputs reference
-------------------

.. toctree::
   :maxdepth: 2
   
   Attributes
   Functions
   Parameters