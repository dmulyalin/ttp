Extend Tag
==========

Extend tag allows to extend template with content of other templates. Parent template will load **all** 
tags of extended template and process them as if they were inserted in place of the ``extend`` tag 
definition.

.. list-table:: extend tag attributes
   :widths: 10 90
   :header-rows: 1

   * - Attribute
     - Description
   * - `template`_   
     - OS path to template file or reference to template within TTP Templates repository
     
template
--------
``template="path_string"``

``path_string`` (mandatory) - OS path to template file or reference to template within TTP Templates repository in a form of ``ttp://path/to/template`` path.

**Example-1**

This template uses reference to a template within TTP templates repository to load additional groups for parsing below data::

    vlan 1234
     name some_vlan
    !
    vlan 910
     name one_more
    !
    interface Gi1.100
     description Some description 1
     encapsulation dot1q 100
     ip address 10.0.0.1 255.255.255.0
     shutdown
    !
    interface Gi2
     description Some description 2
     ip address 10.1.0.1 255.255.255.0
    !
    
Template content::

    <extend template="ttp://platform/test_platform_show_run_pipe_sec_interface.txt"/>
    
    <group name="vlans.{{ vlan }}">
    vlan {{ vlan }}
     name {{ name }}
    </group>
    
Where ``ttp://platform/test_platform_show_run_pipe_sec_interface.txt`` template content is::

    <group>
    interface {{ interface }}
     description {{ description | re(".+") }}
     encapsulation dot1q {{ dot1q }}
     ip address {{ ip }} {{ mask }}
     shutdown {{ disabled | set(True) }}
    </group>
    
Results::

   [
        [
            [
                {
                    "description": "Some description 1",
                    "disabled": True,
                    "dot1q": "100",
                    "interface": "Gi1.100",
                    "ip": "10.0.0.1",
                    "mask": "255.255.255.0",
                },
                {
                    "description": "Some description 2",
                    "interface": "Gi2",
                    "ip": "10.1.0.1",
                    "mask": "255.255.255.0",
                },
                {"vlans": {"1234": {"name": "some_vlan"}, "910": {"name": "one_more"}}},
            ]
        ]
    ]
    
**Example-2**

This template extending groups from a file on local file system to parse this data::

    vlan 1234
     name some_vlan
    !
    vlan 910
     name one_more
    !
    interface Gi1.100
     description Some description 1
     encapsulation dot1q 100
     ip address 10.0.0.1 255.255.255.0
     shutdown
    !
    interface Gi2
     description Some description 2
     ip address 10.1.0.1 255.255.255.0
    !
    
Template content::

    <extend template="/templates/parse_interfaces.txt"/>
    
    <group name="vlans.{{ vlan }}">
    vlan {{ vlan }}
     name {{ name }}
    </group>
    
Where ``/templates/parse_interfaces.txt`` template content is::

    <group>
    interface {{ interface }}
     description {{ description | re(".+") }}
     encapsulation dot1q {{ dot1q }}
     ip address {{ ip }} {{ mask }}
     shutdown {{ disabled | set(True) }}
    </group>
    
Results::

   [
        [
            [
                {
                    "description": "Some description 1",
                    "disabled": True,
                    "dot1q": "100",
                    "interface": "Gi1.100",
                    "ip": "10.0.0.1",
                    "mask": "255.255.255.0",
                },
                {
                    "description": "Some description 2",
                    "interface": "Gi2",
                    "ip": "10.1.0.1",
                    "mask": "255.255.255.0",
                },
                {"vlans": {"1234": {"name": "some_vlan"}, "910": {"name": "one_more"}}},
            ]
        ]
    ]