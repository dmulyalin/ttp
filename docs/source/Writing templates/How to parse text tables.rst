How to parse text tables
========================

Parsing text tables is straightforward as long as the table is regular — meaning there are repetitive patterns in the text. For instance, this text::

    Protocol  Address     Age (min)  Hardware Addr   Type   Interface
    Internet  10.12.13.1        98   0950.5785.5cd1  ARPA   FastEthernet2.13
    Internet  10.12.13.3       131   0150.7685.14d5  ARPA   GigabitEthernet2.13
    Internet  10.12.13.4       198   0950.5C8A.5c41  ARPA   GigabitEthernet2.17

is a table and is easy to parse with TTP using this single pattern::

    Internet  {{ ip | IP }}  {{ age | DIGIT }}   {{ mac }}  ARPA   {{ interface }}

``IP`` and ``DIGIT`` are built-in regex patterns matching IP addresses and integers respectively. If the table has additional rows in varying formats, add more patterns to the group. For instance:

    Protocol  Address     Age (min)  Hardware Addr   Type   Interface
    Internet  10.12.13.1        98   0950.5785.5cd1  ARPA   FastEthernet2.13
    Internet  10.12.13.3       131   0150.7685.14d5  ARPA   GigabitEthernet2.13
    Internet  10.12.13.4       198   0950.5C8A.5c41  ARPA   GigabitEthernet2.17
    Internet  10.12.14.5       -     0950.5C8A.5d42  ARPA   GigabitEthernet3
    Internet  10.12.15.6       164   0950.5C8A.5e43  ARPA   GigabitEthernet4.21  *

would require two additional patterns to match all lines::

    <group name="table_data">
    Internet  {{ ip | IP | _start_ }}  {{ age | DIGIT }}   {{ mac }}  ARPA   {{ interface }}
    Internet  {{ ip | IP | _start_ }}  -                   {{ mac }}  ARPA   {{ interface }}
    Internet  {{ ip | IP | _start_ }}  {{ age | DIGIT }}   {{ mac }}  ARPA   {{ interface }}  *
    </group>

We also have to use _start_ indicator, as each line is a complete match and on each subsequent match we need to save previous matches in results. However, above template can be simplified a bit::

    <group name="table_data" method="table">
    Internet  {{ ip | IP }}  {{ age }}   {{ mac }}  ARPA   {{ interface }}
    Internet  {{ ip | IP }}  {{ age }}   {{ mac }}  ARPA   {{ interface }}  *
    </group>

Excluding the DIGIT regex formatter still matches all digits but also matches the hyphen character. In addition, the TTP groups tag has a ``method`` attribute that makes every pattern in a group a group start regex without needing to specify ``_start_`` explicitly. Parsing text table data with the above template produces these results::

    [   [   {   'table_data': [   {   'age': '98',
                                      'interface': 'FastEthernet2.13',
                                      'ip': '10.12.13.1',
                                      'mac': '0950.5785.5cd1'},
                                  {   'age': '131',
                                      'interface': 'GigabitEthernet2.13',
                                      'ip': '10.12.13.3',
                                      'mac': '0150.7685.14d5'},
                                  {   'age': '198',
                                      'interface': 'GigabitEthernet2.17',
                                      'ip': '10.12.13.4',
                                      'mac': '0950.5C8A.5c41'},
                                  {   'age': '-',
                                      'interface': 'GigabitEthernet3',
                                      'ip': '10.12.14.5',
                                      'mac': '0950.5C8A.5d42'},
                                  {   'age': '164',
                                      'interface': 'GigabitEthernet4.21',
                                      'ip': '10.12.15.6',
                                      'mac': '0950.5C8A.5e43'}]}]]

TTP can help parsing text tables data for one more specific use case, for example this data::

    VRF VRF-CUST-1 (VRF Id = 4); default RD 12345:241;
      Old CLI format, supports IPv4 only
      Flags: 0xC
      Interfaces:
        Te0/3/0.401              Te0/3/0.302              Te0/3/0.315
        Te0/3/0.316              Te0/3/0.327

has text table embedded into it, and if we want to extract all the interfaces that belongs to this particular VRF, we can use this template::

    <group name="vrf.{{ vrf_name }}">
    VRF {{ vrf_name }} (VRF Id = {{ vrf_id}}); default RD {{ vrf_rd }};
    <group name="interfaces">
      Interfaces: {{ _start_ }}
        {{ interfaces | ROW | joinmatches(",") }}
    </group>
    </group>

In above temple ``ROW`` regex formatter will help to match all lines with words separated by 2 or more spaces between them, producing this results::

    [
        [
            {
                "vrf": {
                    "VRF-CUST-1": {
                        "interfaces": {
                            "interfaces": "Te0/3/0.401              Te0/3/0.302              Te0/3/0.315 Te0/3/0.316              Te0/3/0.327"
                        },
                        "vrf_id": "4",
                        "vrf_rd": "12345:241"
                    }
                }
            }
        ]
    ]

While TTP extracted all interfaces, they are combined in a single string, below template can be used to produce list of interfaces instead::

    <group name="vrf.{{ vrf_name }}">
    VRF {{ vrf_name }} (VRF Id = {{ vrf_id}}); default RD {{ vrf_rd }};
    <group name="interfaces">
      Interfaces: {{ _start_ }}
        {{ interfaces | ROW | resub(" +", ",", 20) | split(',') | joinmatches }}
    </group>
    </group>

In this template same match result processed inline using ``resub`` function to replace all consequential occurrence of spaces with singe comma character, after substitution, results processing continues through ``split`` function, that split string into a list of items using comma character, finally, ``joinmatches`` function tells TTP to join all matches in single list, producing these results::

    [
        [
            {
                "vrf": {
                    "VRF-CUST-1": {
                        "interfaces": {
                            "interfaces": [
                                "Te0/3/0.401",
                                "Te0/3/0.302",
                                "Te0/3/0.315",
                                "Te0/3/0.316",
                                "Te0/3/0.327"
                            ]
                        },
                        "vrf_id": "4",
                        "vrf_rd": "12345:241"
                    }
                }
            }
        ]
    ]
