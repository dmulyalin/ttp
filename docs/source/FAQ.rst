FAQ
===

Collection of answers to frequently asked questions.

.. contents:: :local:

Why does TTP return a nested list of lists of lists?
----------------------------------------------

By default, TTP accounts for the most general case: where a TTP object is assumed to have several templates.
Each template produces its own results, which gives the first level of lists.

Within each template, several inputs can be defined (whereby input = string/text to parse).
Results for each input are parsed independently and then aggregated into a list.
This gives the second level of lists.

If a template does not have any groups, or has groups without a ``name`` attribute, its results
will produce a list of items on a per-input basis. This gives the third level of lists.

This is the default, generalized behaviour that (so far) works for all cases, as items always can be
appended to the list.

Reference :ref:`results_structure` documentation on how to produce results suitable for your case
using TTP built-in techniques. Otherwise, Python results post-processing may also prove useful.

How do I add comments in TTP templates?
-------------------------------------

There are three different ways you can add comments.

1. Single line comments within a group, using ``##``::

    <group name="interfaces">
    ## important comment
    ## another comment
    interface {{ interface }}
     description {{ description }}
    </group>

2. Multi-line comments outside of groups, using XML comments::

    <!--Your comment, can be
    multi line
    -->
    <group name="interfaces">
    interface {{ interface }}
     description {{ description }}
    </group>

3. For more extensive descriptions, use the <doc> tag::

    <doc>
    My
    documentation
    here
    </doc>

    <group name="interfaces">
    interface {{ interface }}
     description {{ description }}
    </group>

Starting with TTP 0.7.0 double hash ## comments can be indented.

How do I make TTP always return a list, even if there is only one matched item?
-----------------------------------------------------------------

Please refer to :ref:`path_formatters` for details on how
to enforce the results structure with a list or dictionary.

The :ref:`results_structure` documentation may also be of use.


How do I match several variations of slightly changing output?
------------------------------------------------------------

It is recommended to use the API wherever possible. Parsing semi-structured text for varying output
can be "fun", and may produce fragile results.

In most cases, TTP transforms templates into regular expressions. If your data changes,
so should your template. Some potential solutions for matching varying output include:

* using several ``_start_`` lines in a template
* setting a group's ``method`` attribute to ``table``
* using the ``ignore`` indicator to ignore portions of the input data
* add additional regular expressions to match and ignore varying data.

Consider this data, which displays the many output variations for a single command::

    # not disabled and no comment
    /ip address add address=10.4.1.245 interface=lo0 network=10.4.1.245
    /ip address add address=10.4.1.246 interface=lo1 network=10.4.1.246

    # not disabled and comment with no quotes
    /ip address add address=10.9.48.241/29 comment=SITEMON interface=ether2 network=10.9.48.240
    /ip address add address=10.9.48.233/29 comment=Camera interface=vlan205@bond1 network=10.9.48.232
    /ip address add address=10.9.49.1/24 comment=SM-Management interface=vlan200@bond1 network=10.9.49.0

    # not disabled and comment with quotes
    /ip address add address=10.4.1.130/30 comment="to core01" interface=vlan996@bond4 network=10.4.1.128
    /ip address add address=10.4.250.28/29 comment="BH 01" interface=vlan210@bond1 network=10.4.250.24
    /ip address add address=10.9.50.13/30 comment="Cust: site01-PE" interface=vlan11@bond1 network=10.9.50.12

    # disabled no comment
    /ip address add address=10.0.0.2/30 disabled=yes interface=bridge:customer99 network=10.0.0.0

    # disabled with comment
    /ip address add address=169.254.1.100/24 comment=Cambium disabled=yes interface=vlan200@bond1 network=169.254.1.0

    # disabled with comment with quotes
    /ip address add address=10.4.248.20/29 comment="Backhaul to AGR (Test Segment)" disabled=yes interface=vlan209@bond1 network=10.4.248.16

This template could be used to match all of them::

    <vars>
    default_values = {
        "comment": "",
        "disabled": False
    }
    </vars>

    <group default="default_values">
    ## not disabled and no comment
    /ip address add address={{ ip | _start_ }} interface={{ interface }} network={{ network }}

    ## not disabled and comment with/without quotes
    /ip address add address={{ ip | _start_ }}/{{ mask }} comment={{ comment | ORPHRASE | exclude("disabled=") | strip('"')}} interface={{ interface }} network={{ network }}

    ## disabled no comment
    /ip address add address={{ ip | _start_ }}/{{ mask }} disabled={{ disabled }} interface={{ interface }} network={{ network }}

    ## disabled with comment with/without quotes
    /ip address add address={{ ip | _start_ }}/{{ mask }} comment={{ comment | ORPHRASE | exclude("disabled=") | strip('"') }} disabled={{ disabled }} interface={{ interface }} network={{ network }}
    </group>

Producing uniform results::

    parser = ttp(data=data, template=template, log_level="ERROR")
    parser.parse()
    res = parser.result(structure="flat_list")
    pprint.pprint(res, width=200)
    assert res == [{'comment': '', 'disabled': False, 'interface': 'lo0', 'ip': '10.4.1.245', 'network': '10.4.1.245'},
                   {'comment': '', 'disabled': False, 'interface': 'lo1', 'ip': '10.4.1.246', 'network': '10.4.1.246'},
                   {'comment': 'SITEMON', 'disabled': False, 'interface': 'ether2', 'ip': '10.9.48.241', 'mask': '29', 'network': '10.9.48.240'},
                   {'comment': 'Camera', 'disabled': False, 'interface': 'vlan205@bond1', 'ip': '10.9.48.233', 'mask': '29', 'network': '10.9.48.232'},
                   {'comment': 'SM-Management', 'disabled': False, 'interface': 'vlan200@bond1', 'ip': '10.9.49.1', 'mask': '24', 'network': '10.9.49.0'},
                   {'comment': 'to core01', 'disabled': False, 'interface': 'vlan996@bond4', 'ip': '10.4.1.130', 'mask': '30', 'network': '10.4.1.128'},
                   {'comment': 'BH 01', 'disabled': False, 'interface': 'vlan210@bond1', 'ip': '10.4.250.28', 'mask': '29', 'network': '10.4.250.24'},
                   {'comment': 'Cust: site01-PE', 'disabled': False, 'interface': 'vlan11@bond1', 'ip': '10.9.50.13', 'mask': '30', 'network': '10.9.50.12'},
                   {'comment': '', 'disabled': 'yes', 'interface': 'bridge:customer99', 'ip': '10.0.0.2', 'mask': '30', 'network': '10.0.0.0'},
                   {'comment': 'Cambium', 'disabled': 'yes', 'interface': 'vlan200@bond1', 'ip': '169.254.1.100', 'mask': '24', 'network': '169.254.1.0'},
                   {'comment': 'Backhaul to AGR (Test Segment)', 'disabled': 'yes', 'interface': 'vlan209@bond1', 'ip': '10.4.248.20', 'mask': '29', 'network': '10.4.248.16'}]

Notes:

1. ``_start_`` indicator denotes several start regexes
2. ``default="default_values"`` helps to ensure that results will always have default values
3. ``ORPHRASE`` is a regex pattern for matching either 1) a single word or 2) several words separated by single spaces (a phrase)
4. ``exclude("disabled=")`` because of ``ORPHRASE`` false matches that could be produced, e.g.: ``{'comment': 'Cambium disabled=yes'...`` This is due to regular expression behavior, and you will need to filter such results
5. ``strip('"')`` removes quote character from left and right of the matched string

How do I combine multiple matches into the same match variable?
------------------------------------------------------------

You can use the ``joinmatch`` function to join multiple matches into a single variable.
For example, if you had a parameter with multiple configuration statements, you could combine them:

Data::

    interface GigabitEthernet3/3
     switchport trunk allowed vlan add 138,166,173
     switchport trunk allowed vlan add 400,401,410

Template::

    interface {{ interface }}
     switchport trunk allowed vlan add {{ trunk_vlans | joinmatches(',') }}

Result::

    [
        [
            {
                "interface": "GigabitEthernet3/3",
                "trunk_vlans": "138,166,173,400,401,410"
            }
        ]
    ]


How do I capture all lines that aren't matched by a variable?
-------------------------------------------------------------

This can be done using the ``_line_`` indicator, which matches **any** line of text. Combined
with the ``joinmatches`` function, you can use this to capture all non-matched lines, e.g.:

Data::

    interface Gi0/37
     description CPE_Acces
     switchport mode trunk
     switchport port-security
     switchport port-security maximum 5
     switchport port-security mac-address sticky
    !

Template::

    <group>
    interface {{ interface }}
     description {{ description }}
     switchport mode {{ mode }
     {{ remaining_config | _line_ | joinmatches }}
    ! {{ _end_ }}
    </group>

Results::

    [[{'description': 'CPE_Acces',
       'mode': 'trunk',
       'interface': 'Gi0/37',
       'remaining_config': 'switchport port-security\n'
                           'switchport port-security maximum 5\n'
                           'switchport port-security mac-address sticky'}
                          ]]

How do I capture multi-line output?
-----------------------------------

If you want to capture something that spans multiple lines, you can combine the lines into one variable
by using ``_line_`` with the ``joinmatches`` function.

For instance, we want to match the system description in LLDP neighbors output, but it spans multiple lines:

Sample data::

    Local Intf: Te2/1/23
    System Name: r1.lab.local

    System Description:
    Cisco IOS Software, Catalyst 1234 L3 Switch Software (cat1234e-ENTSERVICESK9-M), Version 1534.1(1)SG, RELEASE SOFTWARE (fc3)
    Technical Support: http://www.cisco.com/techsupport
    Copyright (c) 1986-2012 by Cisco Systems, Inc.
    Compiled Sun 15-Apr-12 02:35 by p

    Time remaining: 92 seconds

Template::

    <group>
    Local Intf: {{ local_intf }}
    System Name: {{ peer_name }}

    <group name="peer_system_description">
    System Description: {{ _start_ }}
    {{ sys_description | _line_ | joinmatches(" ") }}
    Time remaining: {{ ignore }} seconds {{ _end_ }}
    </group>

    </group>

Result::

    [[[{'local_intf': 'Te2/1/23',
        'peer_name': 'r1.lab.local',
        'peer_system_description': {'sys_description': 'Cisco IOS Software, Catalyst 1234 L3 Switch '
                                                       'Software (cat1234e-ENTSERVICESK9-M), Version '
                                                       '1534.1(1)SG, RELEASE SOFTWARE (fc3) Technical '
                                                       'Support: http://www.cisco.com/techsupport '
                                                       'Copyright (c) 1986-2012 by Cisco Systems, Inc. '
                                                       'Compiled Sun 15-Apr-12 02:35 by p'}}]]]

How do I escape < and >  characters in a template?
------------------------------------------------

In XML, ``<`` and ``>`` have special meanings. Since TTP templates are XML documents,
we need to use escape sequences to match these characters:

Data::

    Name:Jane<br>
    Name:Michael<br>
    Name:July<br>

Template::

    Name:{{ name }}&lt;br&gt;

The above template would **not** work. The Python XML Etree library will transform ``&lt;br&gt;`` to ``<br>`` and
will fail to parse it as there is no closing tag.
Instead, to properly interpret escape sequences, we need to wrap the template strings in ``<group>`` tags::

    <group name="people">
    Name:{{ name }}&lt;br&gt;
    </group>

Result::

    [[{'people': [{'name': 'Jane'}, {'name': 'Michael'}, {'name': 'July'}]}]]
