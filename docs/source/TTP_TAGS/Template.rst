Template
========

TTP templates support <template> tag to define several templates within single template, each template processes separately, no data shared across templates.

Only two levels of hierarchy supported - top template tag and a number of child template tags within it, further template tags nested within children are ignored.

First use case for this functionality stems from the fact that templates executed in sequence, meaning it is possible to organize such a work flow when results produced by one template can be leveraged by next template(s), for instance first template can produce lookup table text file and other template will rely on.

Another use case is templates grouping under single definition and that can simplify loading - instead of adding each template to TTP object, all of them can be loaded in one go.

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

There are a number of attributes can be used with template tag, these attributes help to define template processing behavior.

.. list-table:: 
   :widths: 10 90
   :header-rows: 1

   * - Attribute
     - Description
   * - `name`_   
     - Uniquely identifies template
   * - `base_path`_   
     - Fully qualified OS path to data
   * - `results`_   
     - Identifies the way how results should be grouped
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

This attributes allows to specify base OS file system path to the location of data folders, folders with actual data can be detailed further using relative path in inputs' url attribute.

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

Template results attribute allows to influence the logic used to combine template results, options are:

    * per_input - default, allows to combine results on a per input basis. For instance, if we have two text files with data that needs to be parsed, first file will be parsed by a set of groups associated with this template, combining results in a structure, that will be appended to the list of overall template results. Same will happen with next file. As a result, for this particular template two result items will be produced, one for each file. 
	* per_template - allows to combine results on a per template basis. For instance, if we have two text files with data that needs to be parsed, first file will be parsed by a set of groups associated with this template, combining results in a structure, that structure will be used by TTP to merge with results produced by next file. As a result, for this particular template single results item will be produced, that item will contain merged results for all inputed files/datum.
	
Main usecase for per_template behavior is to combine results across all the inputs and produce structure that will be more flat and might be easier to work with in certain situations.
	
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

pathchar allows to specify character to use to separate path items for groups name attribute, by default it is dot character.