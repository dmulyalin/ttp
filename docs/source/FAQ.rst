FAQ
===

Collection of answers to frequently asked questions.

.. contents:: :local:

Why TTP returns nested list of lists of lists?
----------------------------------------------

By default TTP accounts for most general case where several templates added in TTP object,
each template producing its own results, that is why top structure is a list.

Within template, several inputs can be defined (input = string/text to parse), parsing results 
for each input produced independently, joining in a list, where each item corresponds to 
input. That gives second level of lists.

If template does not have groups defined or has groups without ``name`` attribute, results for
such a template will produce list of items on a per-input basis. That is third level of lists.

Above is a default, generalized behavior that (so far) works for all cases, as items always can be 
appended to the list. 

Reference :ref:`results_structure` documentation on how to produce results suitable for your case
using TTP built-in techniques, otherwise, Python results post-processing proved to be useful
as well.

How to add comments in TTP templates?
-------------------------------------

To put single line comment within TTP group use double hash tag - ``##``, e.g.::

    <group name="interfaces">
    ## important comment
    ## another comment
    interface {{ interface }}
     description {{ description }}
    </group>
    
To place comments outside of TTP groups can use XML comments::

    <!--Your comment, can be
    multi line  
    -->
    <group name="interfaces">
    interface {{ interface }}
     description {{ description }}
    </group>
    
If you after writing extensive description about your template, using <doc> tag
could be another option::

    <doc>
    My 
    documentation 
    here
    </doc>
    
    <group name="interfaces">
    interface {{ interface }}
     description {{ description }}
    </group>

How to make TTP always return a list even if single item matched?
-----------------------------------------------------------------

Please reference TTP :ref:`path_formatters` for details on how 
to enforce list or dictionary as part of results structure.

Generally, going through :ref:`results_structure` documentation 
might be useful as well.


How to match several variations of slightly changing output?
------------------------------------------------------------

If you can, better use API, as parsing semi structured text for varying output 
can be "fun" with results fragile. Keep reading if you have no other choice.

In general case, TTP transform templates in regular expressions, if your data changing, 
so your template should as well. For instance, several ``_start_`` lines could be 
used in a template or group ``method`` attribute could be set to ``table`` to match
several variations of output.

Consider this data::

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

Above are the different variations of the same show command output. This template could be
used to match all of them::

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
    
Producing this uniform results::

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

1. ``_start_`` indicator used to denote several start regexes
2. ``default="default_values"`` helps to ensure that results will always have default values
3. ``ORPHRASE`` regex pattern to match single word or several words separated by single space (phrase)
4. ``exclude("disabled=")`` because of ``ORPHRASE`` false matches could be produced, e.g.: ``{'comment': 'Cambium disabled=yes'...`` - that is due to regular expression behavior, need to filter such results
5. ``strip('"')`` removes quote character from left and right of the matched string