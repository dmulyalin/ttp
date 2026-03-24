Template Tag
============

TTP templates support the ``<template>`` tag to define multiple templates within a single file. Each template is processed independently — no data is shared between templates — but the results of one template can be used by lookup functions in another.

Only two levels of hierarchy supported - top template tag and a number of child template tags within it, further template tags nested within children are ignored.

The first use case for this is that templates execute in sequence, so it is possible to use results produced by one template in subsequent templates — for example, the first template can produce a lookup table file that the next template then references.

Another use case is grouping templates under a single file to simplify loading: instead of adding each template to the TTP object individually, all of them can be loaded at once.

For instance::

    from ttp import ttp

    template1="""
    <group>
    interface {{ interface }}
     ip address {{ ip }}/{{ mask }}
    </group>
    """

    template2="""
    <group name="vrfs">
    VRF {{ vrf }}; default RD {{ rd }}
    <group name="interfaces">
      Interfaces: {{ _start_ }}
        {{ intf_list | ROW }}
    </group>
    </group>
    """

    parser = ttp()
    parser.add_data(some_data)
    parser.add_template(template1)
    parser.add_template(template2)
    parser.parse()

Above code will produce same results as this code::

    from ttp import ttp

    template="""
    <template>
    <group>
    interface {{ interface }}
     ip address {{ ip }}/{{ mask }}
    </group>
    </template>

    <template>
    <group name="vrfs">
    VRF {{ vrf }}; default RD {{ rd }}
    <group name="interfaces">
      Interfaces: {{ _start_ }}
        {{ intf_list | ROW }}
    </group>
    </group>
    </template>
    """

    parser = ttp()
    parser.add_data(some_data)
    parser.add_template(template)
    parser.parse()

Template tag attributes
-----------------------------------------------------------------------------

There are a number of attributes supported by template tag. These attributes help to define template processing behavior.

.. list-table::
   :widths: 10 90
   :header-rows: 1

   * - Attribute
     - Description
   * - `name`_
     - Unique template identifier
   * - `base_path`_
     - Fully qualified OS path to data
   * - `results`_
     - Identifies the way results grouping method
   * - `pathchar`_
     - Character to use for group name-path processing

name
******************************************************************************
``name="template_name"``

Template name attribute is a string that indicates the unique name of the template. This attribute required if final results structure should be dictionary and not list (default behavior) as can be indicated in ``ttp.result`` method using ``structure`` argument, e.g.

**Example**

In below example results produced by TTP will be formed into dictionary structure using template names attributes as top level keys.

Consider this code::

    from ttp import ttp
    import json

    template="""
    <template name="template-1">
    <input load="text">
    interface Vlan778
     ip address 2002:fd37::91/124
    </input>
    <group name="interfaces-1">
    interface {{ interface }}
     ip address {{ ip }}
    </group>
    </template>

    <template name="template-2">
    <input load="text">
    interface Vlan778
     description V6 Management vlan
    </input>
    <group name="interfaces-2">
    interface {{ interface }}
     description {{ description | ORPHRASE }}
    </group>
    </template>
    """

    parser=ttp(template=template)
    parser.parse()
    results = parser.result(structure="dictionary")
    print(json.dumps(results, sort_keys=True, indent=4, separators=(',', ': ')))

Results would be::

    {
        "template-1": [
            {
                "interfaces-1": {
                    "interface": "Vlan778",
                    "ip": "2002:fd37::91/124"
                }
            }
        ],
        "template-2": [
            {
                "interfaces-2": {
                    "description": "V6 Management vlan",
                    "interface": "Vlan778"
                }
            }
        ]
    }

base_path
******************************************************************************
``base_path="/os/base/path/to/data/"``

Specifies the base OS file system path to data folders. Individual inputs can refine this further using a relative path in their ``url`` attribute.

**Example**

In below template base_path attribute set to ``/path/to/Data/``, as a result all urls for all inputs within this template will be extended to absolute path in such a way that:

 * Input dataset-1 url ``/data-1/`` will become ``/path/to/Data/data-1/``
 * Input dataset-2 url ``/data-2/`` will become ``/path/to/Data/data-2/``

Absolute path will be used to load data for each input.

Template::

    <template base_path="/path/to/Data/">

    <input name="dataset-1">
    url = "/data-1/"
    </input>

    <input name="dataset-2">
    url = "/data-2/"
    </input>

    <group name="interfaces1" input="dataset-1">
    interface {{ interface }}
     switchport access vlan {{ access_vlan }}
    </group>

    <group name="interfaces2" input="dataset-2">
    interface {{ interface }}
      ip address {{ ip  }}/{{ mask }}
    </group>

    </template>

results
******************************************************************************
``results="per_template|per_input"``

The ``results`` attribute controls how template results are combined. Options are:

    * per_input - default; combines results per input. Each input file is parsed independently, and its result is appended to the overall template results list. Two input files produce two result items.
    * per_template - combines results across all inputs into a single structure. Each parsed input is merged with the previous results, so the template ultimately produces one result item containing data from all input files.

Main use case for per_template behavior is to combine results across all the inputs and produce structure that will be more flat and might be easier to work with in certain situations.

**Example**

In this template we have two templates defined, with same set of inputs/data and groups, but first template has per_input (default) logic, while second template was configured to use per_template behavior.

Template::

    <template>
    <input load="text">
    interface Vlan778
     ip address 2002:fd37::91/124
    interface Vlan800
     ip address 172.16.10.1/24
    </input>

    <input load="text">
    interface Vlan779
     ip address 192.168.1.1/24
    interface Vlan90
     ip address 192.168.90.1/24
    </input>

    <group name="interfaces">
    interface {{ interface }}
     ip address {{ ip }}
    </group>
    </template>


    <template results="per_template">
    <input load="text">
    interface Vlan778
     ip address 2002:fd37::91/124
    interface Vlan800
     ip address 172.16.10.1/24
    </input>

    <input load="text">
    interface Vlan779
     ip address 192.168.1.1/24
    interface Vlan90
     ip address 192.168.90.1/24
    </input>

    <group name="interfaces">
    interface {{ interface }}
     ip address {{ ip }}
    </group>
    </template>

Results::

    [
        [ <-----------------------------------------------first template results:
            {
                "interfaces": [
                    {
                        "interface": "Vlan778",
                        "ip": "2002:fd37::91/124"
                    },
                    {
                        "interface": "Vlan800",
                        "ip": "172.16.10.1/24"
                    }
                ]
            },
            {
                "interfaces": [
                    {
                        "interface": "Vlan779",
                        "ip": "192.168.1.1/24"
                    },
                    {
                        "interface": "Vlan90",
                        "ip": "192.168.90.1/24"
                    }
                ]
            }
        ],
        [ <-----------------------------------------------second template results:
            {
                "interfaces": [
                    {
                        "interface": "Vlan778",
                        "ip": "2002:fd37::91/124"
                    },
                    {
                        "interface": "Vlan800",
                        "ip": "172.16.10.1/24"
                    },
                    {
                        "interface": "Vlan779",
                        "ip": "192.168.1.1/24"
                    },
                    {
                        "interface": "Vlan90",
                        "ip": "192.168.90.1/24"
                    }
                ]
            }
        ]
    ]

pathchar
******************************************************************************
``pathchar="."``

At the moment this argument behavior is not fully implemented/tested, hence refrain from using it.

``pathchar`` specifies the character used to separate path items in the group ``name`` attribute. The default is a dot (``.``).
