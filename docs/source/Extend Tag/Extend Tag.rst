Extend Tag
==========

Extend tag allows to extend template with content of other templates. Parent template will load **all**
tags of extended template and process them as if they were inserted in place of the ``extend`` tag
definition.

Extend tag can be nested within groups as well, but in that case only ``group`` and ``extend`` tags loaded from
extended template, other tags (lookup, vars, input, output) are ignored. Nested extend only supports `groups`_ filter.

.. list-table:: extend tag attributes
   :widths: 10 90
   :header-rows: 1

   * - Attribute
     - Description
   * - `template`_
     - OS path to template file or reference to template within TTP Templates repository
   * - `inputs`_
     - filter, comma separated list of input tag names to load
   * - `groups`_
     - filter, comma separated list of group tag names to load
   * - `vars`_
     - filter, comma separated list of template variables tag names to load
   * - `lookups`_
     - filter, comma separated list of lookup tag names to load
   * - `outputs`_
     - filter, comma separated list of output tag names to load
   * - `macro`_
     - name of macro function to pass template content through

template
--------
``template="path_string"``

``path_string`` (mandatory) - relative current working directory or absolute OS path to template file or reference to template within TTP Templates repository in a form of ``ttp://path/to/template`` path. Alternatively, OS path to file within ``TTP_TEMPLATES_DIR`` directory, where ``TTP_TEMPLATES_DIR`` is an environment variable.

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

**Example-3**

This example demonstrates how to use ``extend`` tag withing groups.

Sample data::

    router bgp 65100
     !
     router-id 1.1.1.1
     !
     neighbor 2.2.2.2 remote-as 65000
     neighbor 2.2.2.3 remote-as 65001

Parent template is::

    <group name="bgp_config">
    router bgp {{ bgp_as }}

    <extend template="/template/bgp_params.txt"/>

    <group name="peers">
     neighbor {{ peer }} remote-as {{ asn }}
    </group>

    </group>

Where ``/template/bgp_params.txt`` content is::

    <group name="config">
     router-id {{ rid }}
    </group>

After parsing these results produced::

    [[{'bgp_config': {'bgp_as': '65100',
                      'config': {'rid': '1.1.1.1'},
                      'peers': [{'asn': '65000', 'peer': '2.2.2.2'},
                                {'asn': '65001', 'peer': '2.2.2.3'}]}}]]

**Example-4**

This example demonstrates how to use ``extend`` tag and ``TTP_TEMPLATES_DIR`` to load templates.

Given this files structure::

    C:
    └───TTP_TEMPLATES
        └───parse_vlans_template.txt

And having ``TTP_TEMPLATES_DIR`` set to ``C:\TTP_TEMPLATES\`` value, we can use this template
to refer to ``parse_vlans_template.txt`` file from within extend tag::

    <extend template="parse_vlans_template.txt"/>

Where ``parse_vlans_template.txt`` content is::

    <group name="vlans.{{ vlan }}">
    vlan {{ vlan }}
     name {{ name }}
    </group>

inputs
------
``inputs="name1, name2, .. , nameN"``

This filter allows to form a comma separated list of input tags to load from extended template, identified by input tag name attribute.

groups
------
``groups="name1, name2, .. , nameN"`` or ``groups="1, 5, .. , N"``

This filter allows to form a comma separated list of groups to load from extended template, identified by group tag name attribute or group index. Group indexes counted from top group starting from 0.

vars
----
``vars="name1, name2, .. , nameN"``

This filter allows to form a comma separated list of template variable tags to load from extended template, identified by variables tag name attribute.

lookups
-------
``lookups="name1, name2, .. , nameN"``

This filter allows to form a comma separated list of lookup tags to load from extended template, identified by lookup tag name attribute.

outputs
-------
``outputs="name1, name2, .. , nameN"``

This filter allows to form a comma separated list of output tags to load from extended template, identified by output tag name attribute.

macro
-----
``macro="macro_name"``

Apply arbitrary Python function on template text content before embedding it into parent template.

.. warning:: macro uses python ``exec`` function to parse code payload without imposing any restrictions, hence it is dangerous to
   run templates from untrusted sources as they can have macro defined in them that can be used to execute any arbitrary code on the system.

Macro function must accept single argument to hold embedded template string and must return string
with resulted template content.

**Example**

In this example we define macro function to append 4 spaces to embedded template content.

Template::

    <macro>
    def indent(template_text):
        # macro to indent each line of original template with 4 space characters
        return "\\n".join(f"    {line}" for line in template_text.splitlines())
    </macro>

    <extend template="./assets/extend_vlan.txt" macro="indent"/>

Where file ``./assets/extend_vlan.txt`` content is::

    <group name="vlans.{{ vlan }}">
    vlan {{ vlan }}
     name {{ name }}
    </group>

After passing through macro final template content will look like::

    <macro>
    def indent(data):
        # macro to indent each line of original template with 4 space characters
        return "\\n".join(f"    {line}" for line in data.splitlines())
    </macro>

        <group name="vlans.{{ vlan }}">
        vlan {{ vlan }}
         name {{ name }}
        </group>

For this sample data::

    # this data indented with 4 spaces
        vlan 1234
         name some_vlan
        !
        vlan 910
         name one_more
        !

Final template will produce results::

    [
        [{"vlans": {"1234": {"name": "some_vlan"}, "910": {"name": "one_more"}}}]
    ]
