import sys
sys.path.insert(0,'../..')
import pprint

from ttp import ttp

import logging
logging.basicConfig(level=logging.ERROR)

def test_cerberus_validate_per_input():
    template = """
<input load="text">
csw1# show run | sec ntp
hostname csw1
ntp peer 1.2.3.4
ntp peer 1.2.3.5
</input>

<input load="text">
csw2# show run | sec ntp
hostname csw2
ntp peer 1.2.3.4
ntp peer 3.3.3.3
</input>

<vars>
ntp_schema = {
    "ntp_peers": {
        'type': 'list',
        'schema': {
            'type': 'dict', 
            'schema': {
                'peer': {
                    'type': 'string', 
                    'allowed': ['1.2.3.4', '1.2.3.5']
                }
            }
        }
    }
}
</vars>

<group name="_">
hostname {{ host_name }}
</group>

<group name="ntp_peers*">
ntp peer {{ peer }}
</group>

<output validate="ntp_schema, info='{host_name} NTP peers valid', errors='errors'"/>
    """
    parser = ttp(template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[{'errors': {}, 'info': 'csw1 NTP peers valid', 'valid': True},
                   {'errors': {'ntp_peers': [{1: [{'peer': ['unallowed value 3.3.3.3']}]}]},
                    'info': 'csw2 NTP peers valid',
                    'valid': False}]]
    
# test_cerberus_validate_per_input()

def test_cerberus_validate_per_template():
    template = """
<template results="per_template">
<input load="text">
csw1# show run | sec ntp
ntp peer 1.2.3.4
ntp peer 1.2.3.5
</input>

<input load="text">
csw1# show run | sec ntp
ntp peer 1.2.3.4
ntp peer 3.3.3.3
</input>

<vars>
ntp_schema = {
    "ntp_peers": {
        'type': 'list',
        'schema': {
            'type': 'dict', 
            'schema': {
                'peer': {
                    'type': 'string', 
                    'allowed': ['1.2.3.4', '1.2.3.5']
                }
            }
        }
    }
}
hostname = "gethostname"
</vars>

<group name="ntp_peers*">
ntp peer {{ peer }}
</group>

<output validate="ntp_schema, info='{hostname} NTP peers valid', errors='errors'"/>
</template>
    """
    parser = ttp(template=template, log_level="ERROR")
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [{'errors': {'ntp_peers': [{3: [{'peer': ['unallowed value 3.3.3.3']}]}]},
                    'info': 'csw1 NTP peers valid',
                    'valid': False}]
    
# test_cerberus_validate_per_template()

def test_global_output_deepdiff_with_var_before():
    template = """
<vars>
before = [[{'description': 'some info',
             'interface': 'GigabitEthernet1',
             'ip': '10.123.89.56',
             'mask': '255.255.255.255'},
            {'interface': 'GigabitEthernet2',
             'ip': '10.123.89.55',
             'mask': '255.255.255.0'}]]
</vars>

<input name="Cisco_ios" load="text">
r1#show interfaces | inc line protocol:
interface GigabitEthernet1
 description some info
 vrf forwarding MGMT
 ip address 10.123.89.56 255.255.255.0
interface GigabitEthernet2
 ip address 10.123.89.55 255.255.255.0
</input>

<group>
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ ip }} {{ mask }}
</group>

<output deepdiff="var_before='before'"/>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [{'values_changed': {"root[0][0]['mask']": {'new_value': '255.255.255.0',
                                                              'old_value': '255.255.255.255'}}}]
    
# test_global_output_deepdiff_with_var_before()

def test_group_specific_output_deepdiff_with_var_before():
    template = """
<vars>
before = {"interfaces": [{'description': 'some info',
                          'interface': 'GigabitEthernet1',
                          'ip': '10.123.89.56',
                          'mask': '255.255.255.255'},
                         {'interface': 'GigabitEthernet2',
                          'ip': '10.123.89.55',
                          'mask': '255.255.255.0'}]}
</vars>

<input name="Cisco_ios" load="text">
r1#show interfaces | inc line protocol:
interface GigabitEthernet1
 description some info
 vrf forwarding MGMT
 ip address 10.123.89.56 255.255.255.0
interface GigabitEthernet2
 ip address 10.123.89.55 255.255.255.0
</input>

<group name="interfaces*" output="out_1">
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ ip }} {{ mask }}
</group>

<group name="interfaces_2*">
interface {{ interface }}
 vrf forwarding {{ vrf }}
 ip address {{ ip }} {{ mask }}
</group>

<output name="out_1" deepdiff="var_before='before'"/>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[[{'interfaces_2': [{'interface': 'GigabitEthernet1',
                                        'ip': '10.123.89.56',
                                        'mask': '255.255.255.0',
                                        'vrf': 'MGMT'},
                                       {'interface': 'GigabitEthernet2',
                                        'ip': '10.123.89.55',
                                        'mask': '255.255.255.0'}]},
                    {'values_changed': {"root['interfaces'][0]['mask']": {'new_value': '255.255.255.0',
                                                                          'old_value': '255.255.255.255'}}}]]]
                                                              
# test_group_specific_output_deepdiff_with_var_before()

def test_group_specific_output_deepdiff_with_var_before_with_add_field():
    template = """
<vars>
before = {"interfaces": [{'description': 'some info',
                          'interface': 'GigabitEthernet1',
                          'ip': '10.123.89.56',
                          'mask': '255.255.255.255'},
                         {'interface': 'GigabitEthernet2',
                          'ip': '10.123.89.55',
                          'mask': '255.255.255.0'}]}
</vars>

<input name="Cisco_ios" load="text">
r1#show interfaces | inc line protocol:
interface GigabitEthernet1
 description some info
 vrf forwarding MGMT
 ip address 10.123.89.56 255.255.255.0
interface GigabitEthernet2
 ip address 10.123.89.55 255.255.255.0
</input>

<group name="interfaces*" output="out_1">
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ ip }} {{ mask }}
</group>

<group name="interfaces_2*">
interface {{ interface }}
 vrf forwarding {{ vrf }}
 ip address {{ ip }} {{ mask }}
</group>

<output name="out_1" deepdiff="var_before='before', add_field='diff'"/>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    pprint.pprint(res)
    assert res == [[[{'interfaces_2': [{'interface': 'GigabitEthernet1',
                                        'ip': '10.123.89.56',
                                        'mask': '255.255.255.0',
                                        'vrf': 'MGMT'},
                                       {'interface': 'GigabitEthernet2',
                                        'ip': '10.123.89.55',
                                        'mask': '255.255.255.0'}]},
                     {'diff': {'values_changed': {"root['interfaces'][0]['mask']": {'new_value': '255.255.255.0',
                                                                                    'old_value': '255.255.255.255'}}},
                      'interfaces': [{'description': 'some info',
                                      'interface': 'GigabitEthernet1',
                                      'ip': '10.123.89.56',
                                      'mask': '255.255.255.0'},
                                     {'interface': 'GigabitEthernet2',
                                      'ip': '10.123.89.55',
                                      'mask': '255.255.255.0'}]}]]]
    
# test_group_specific_output_deepdiff_with_var_before_with_add_field()   