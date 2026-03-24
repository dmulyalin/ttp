Inputs
=======

Inputs define data locations and how data should be loaded or filtered. Inputs can be attached to specific groups so that only data from a given input is parsed by those groups, which can improve overall performance.

.. note:: Input order is preserved because inputs are internally represented using an ``OrderedDict``. This is useful when data produced by one input needs to be used by subsequent inputs.

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

The template below uses inputs so that only files with a ``.txt`` extension in "data-1" are parsed by group "interfaces1", and only files matching ``sw\-\d.*`` in "dataset-2" are parsed by "interfaces2". A base path is provided and prepended to each URL in the *url* input parameter. Input "dataset-1" is defined in YAML, while "dataset-2" uses Python syntax.

As a result of input filtering, only ``sw-1.txt`` is processed by "dataset-1" because it is the only file with a ``.txt`` extension, and only ``sw-2.txt`` is processed by "dataset-2" because ``sw3.txt`` does not match the ``sw\-\d.*`` regular expression.

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
