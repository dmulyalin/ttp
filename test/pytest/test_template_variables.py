import sys
sys.path.insert(0,'../..')
import pprint

from ttp import ttp

def test_include_attribute_with_yaml_loader():
    template = """
<vars name="loaded_vars" load="yaml" include="./assets/yaml_vars.txt"/>

<input load="text">
Protocol  Address     Age (min)  Hardware Addr   Type   Interface
Internet  10.12.13.1        98   0950.5785.5cd1  ARPA   FastEthernet2.13
Internet  10.12.13.2        98   0950.5785.5cd2  ARPA   Loopback0
Internet  10.12.13.3       131   0150.7685.14d5  ARPA   GigabitEthernet2.13
Internet  10.12.13.4       198   0950.5C8A.5c41  ARPA   GigabitEthernet2.17
</input>

<group name="arp_test">
Internet  {{ ip }}  {{ age }}   {{ mac }}  ARPA   {{ interface | re("INTF_RE") }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[{'arp_test': [{'age': '98',
                                   'interface': 'FastEthernet2.13',
                                   'ip': '10.12.13.1',
                                   'mac': '0950.5785.5cd1'},
                                  {'age': '131',
                                   'interface': 'GigabitEthernet2.13',
                                   'ip': '10.12.13.3',
                                   'mac': '0150.7685.14d5'},
                                  {'age': '198',
                                   'interface': 'GigabitEthernet2.17',
                                   'ip': '10.12.13.4',
                                   'mac': '0950.5C8A.5c41'}],
                     'loaded_vars': {'INTF_RE': 'GigabitEthernet\\S+|Fast\\S+',
                                     'var_1': 'value_1',
                                     'var_2': [1, 2, 3, 4, 'a']}}]]
    
# test_include_attribute_with_yaml_loader()

def test_sros_gethostname_getter():
    """
    Test ALU SROS prompt matching using gethostname, reference:
    https://documentation.nokia.com/cgi-bin/dbaccessfilename.cgi/9300700701_V1_7750%20SR%20OS%20Basic%20System%20Configuration%20Guide%208.0r1.pdf
    """
    data = ["""
A:ALA-12> show system information
===============================================================================
System Information
===============================================================================
System Name : A:ALA-12>
System Contact : Fred Information Technology
System Location : Bldg.1-floor 2-Room 201    
    """,
    """
A:ALA-12# show system information
===============================================================================
System Information
===============================================================================
System Name : A:ALA-12#
System Contact : Fred Information Technology
System Location : Bldg.1-floor 2-Room 201    
    """,
    """
*A:ALA-12> show system information
===============================================================================
System Information
===============================================================================
System Name : *A:ALA-12>
System Contact : Fred Information Technology
System Location : Bldg.1-floor 2-Room 201    
    """,
    """
*A:ALA-12# show system information
===============================================================================
System Information
===============================================================================
System Name : *A:ALA-12#
System Contact : Fred Information Technology
System Location : Bldg.1-floor 2-Room 201    
    """,
    """
*A:ALA-12>config>system# show system information
===============================================================================
System Information
===============================================================================
System Name : *A:ALA-12>config>system#
System Contact : Fred Information Technology
System Location : Bldg.1-floor 2-Room 201    
    """,
    """
A:ALA-12>config>system# show system information
===============================================================================
System Information
===============================================================================
System Name : A:ALA-12>config>system#
System Contact : Fred Information Technology
System Location : Bldg.1-floor 2-Room 201    
    """
    ]
    template = """
<vars name="vars">
hostname="gethostname"
</vars>

<group name="info">
System Name : {{ sysname }}
System Contact : {{ contacts | PHRASE }}
System Location : {{ locarion | PHRASE }}
</group>
    """
    parser = ttp(template=template)
    for item in data:
        parser.add_input(item)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[{'info': {'contacts': 'Fred Information Technology',
                              'locarion': 'Bldg.1-floor 2-Room 201',
                              'sysname': 'A:ALA-12>'},
                     'vars': {'hostname': 'ALA-12'}},
                    {'info': {'contacts': 'Fred Information Technology',
                              'locarion': 'Bldg.1-floor 2-Room 201',
                              'sysname': 'A:ALA-12#'},
                     'vars': {'hostname': 'ALA-12'}},
                    {'info': {'contacts': 'Fred Information Technology',
                              'locarion': 'Bldg.1-floor 2-Room 201',
                              'sysname': '*A:ALA-12>'},
                     'vars': {'hostname': 'ALA-12'}},
                    {'info': {'contacts': 'Fred Information Technology',
                              'locarion': 'Bldg.1-floor 2-Room 201',
                              'sysname': '*A:ALA-12#'},
                     'vars': {'hostname': 'ALA-12'}},
                    {'info': {'contacts': 'Fred Information Technology',
                              'locarion': 'Bldg.1-floor 2-Room 201',
                              'sysname': '*A:ALA-12>config>system#'},
                     'vars': {'hostname': 'ALA-12'}},
                    {'info': {'contacts': 'Fred Information Technology',
                              'locarion': 'Bldg.1-floor 2-Room 201',
                              'sysname': 'A:ALA-12>config>system#'},
                     'vars': {'hostname': 'ALA-12'}}]]

# test_sros_gethostname_getter()
