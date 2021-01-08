import sys
sys.path.insert(0,'../..')
import pprint

import logging
logging.basicConfig(level=logging.DEBUG)

from ttp import ttp

def test_match_vars_with_hyphen():
    template = """
<input load="text">
interface Port-Channel11
  description Storage
interface Loopback0
  description RID
interface Port-Channel12
  description Management
interface Vlan777
  description Management
</input>

<group>
interface {{ interface-name }}
  description {{ description-bla }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()    
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [[[{'description-bla': 'Storage', 'interface-name': 'Port-Channel11'},
                     {'description-bla': 'RID', 'interface-name': 'Loopback0'},
                     {'description-bla': 'Management', 'interface-name': 'Port-Channel12'},
                     {'description-bla': 'Management', 'interface-name': 'Vlan777'}]]]
    
# test_match_vars_with_hyphen()

def test_match_vars_with_dot():
    template = """
<input load="text">
interface Port-Channel11
  description Storage
interface Loopback0
  description RID
interface Port-Channel12
  description Management
interface Vlan777
  description Management
</input>

<group>
interface {{ interface.name }}
  description {{ description.bla }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()    
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [[[{'description.bla': 'Storage', 'interface.name': 'Port-Channel11'},
                     {'description.bla': 'RID', 'interface.name': 'Loopback0'},
                     {'description.bla': 'Management', 'interface.name': 'Port-Channel12'},
                     {'description.bla': 'Management', 'interface.name': 'Vlan777'}]]]
                     
def test_match_vars_starts_with_digit():
    template = """
<input load="text">
interface Port-Channel11
  description Storage
interface Loopback0
  description RID
interface Port-Channel12
  description Management
interface Vlan777
  description Management
</input>

<group>
interface {{ 77interface.name }}
  description {{ 77description.bla }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()    
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [[[{'77description.bla': 'Storage', '77interface.name': 'Port-Channel11'},
                     {'77description.bla': 'RID', '77interface.name': 'Loopback0'},
                     {'77description.bla': 'Management', '77interface.name': 'Port-Channel12'},
                     {'77description.bla': 'Management', '77interface.name': 'Vlan777'}]]]
                     
def test_match_vars_multiple_non_alpha_chars():
    template = """
<input load="text">
interface Port-Channel11
  description Storage
interface Loopback0
  description RID
interface Port-Channel12
  description Management
interface Vlan777
  description Management
</input>

<group>
interface {{ 77interface.#$%name }}
  description {{ 77description.*(-bla }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()    
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [[[{'77description.*(-bla': 'Storage', '77interface.#$%name': 'Port-Channel11'},
                     {'77description.*(-bla': 'RID', '77interface.#$%name': 'Loopback0'},
                     {'77description.*(-bla': 'Management', '77interface.#$%name': 'Port-Channel12'},
                     {'77description.*(-bla': 'Management', '77interface.#$%name': 'Vlan777'}]]]
                     
def test_match_vars_set_with_hyphen():
    template = """
<input load="text">
interface Port-Channel11
  description Storage
interface Loopback0
  description RID
interface Port-Channel12
  description Management
  no switchport
interface Vlan777
  description Management
interface Port-Channel27
  no switchport
</input>

<group>
interface {{ interface-name }}
  description {{ description-bla | default("Undefined") }}
  no switchport {{ no-switchport | set(True) }}
  {{ is-shutdown | set(False) }}
</group>
    """
    parser = ttp(template=template, log_level="ERROR")
    parser.parse()    
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [[[{'description-bla': 'Storage', 'interface-name': 'Port-Channel11', 'is-shutdown': False},
                     {'description-bla': 'RID', 'interface-name': 'Loopback0', 'is-shutdown': False},
                     {'description-bla': 'Management', 'interface-name': 'Port-Channel12', 'is-shutdown': False, 'no-switchport': True},
                     {'description-bla': 'Management', 'interface-name': 'Vlan777', 'is-shutdown': False},
                     {'description-bla': 'Undefined', 'interface-name': 'Port-Channel27', 'is-shutdown': False, 'no-switchport': True}]]]
   
# test_match_vars_set_with_hyphen()

def test_per_template_mode():
    data_1 = """
interface Port-Chanel11
  description Storage Management
interface Loopback0
  description RID
interface Vlan777
  description Management
    """
    data_2 = """
interface Port-Chane10
  description Storage Management
interface Loopback77
  description RID
interface Vlan321
  description Management    
    """
    template = """
<template name="top_key_name" results="per_template">
<group name="interfaces*">
interface {{ interface }}
  description {{ description }}
</group>
</template>
    """
    parser = ttp(template=template, log_level="error")
    parser.add_input(data_1, template_name="top_key_name")
    parser.add_input(data_2, template_name="top_key_name")
    parser.parse()    
    res = parser.result(structure="dictionary")
    # pprint.pprint(res, width=150)    
    assert res == {'top_key_name': {'interfaces': [{'interface': 'Port-Chanel11'},
                                   {'description': 'RID', 'interface': 'Loopback0'},
                                   {'description': 'Management', 'interface': 'Vlan777'},
                                   {'interface': 'Port-Chane10'},
                                   {'description': 'RID', 'interface': 'Loopback77'},
                                   {'description': 'Management', 'interface': 'Vlan321'}]}}
                                 
# test_per_template_mode()


def test_newline_with_carriage_return():
    data = b"\ninterface Port-Chanel11\r\n\r\n\r\n  description Storage_Management\r\ninterface Loopback0\n  description RID\ninterface Vlan777\n  description Management\r\n".decode("utf-8")
    template = """
<group name="interfaces*">
interface {{ interface }}
  description {{ description }}
</group>
    """
    parser = ttp(data, template, log_level="ERROR")
    parser.parse()    
    res = parser.result()
    # pprint.pprint(res, width=150)    
    assert res == [[{'interfaces': [{'description': 'Storage_Management', 'interface': 'Port-Chanel11'},
                                     {'description': 'RID', 'interface': 'Loopback0'},
                                     {'description': 'Management', 'interface': 'Vlan777'}]}]]
                                     
# test_newline_with_carriage_return()


def test_groups_with_defaults_only_and_with_children_with_defaults_only():
    template = """
<input load="text">
device-hostame uptime is 27 weeks, 3 days, 10 hours, 46 minutes, 10 seconds
</input>

<group name="uptime-1**">
device-hostame uptime is {{ uptime | PHRASE }}
<group name="child_with_default">
 some line with {{ var1 | default("val1") }}
</group>
</group>

<group name="domain" default="Uncknown">
Default domain is {{ fqdn }}
</group>

<group name="ntp-1**">
ntp server {{ server | default('Unconfigured') }}
 ntp source {{ source | default("undefined") }}
<group name="another_child_grp_with_default**">
 npt peer {{ val2 | default("None") }}
<group name="deeper_child_with_defaults" default="something">
 another string {{ val5 }}
 my string {{ val4 }}
</group>
</group>
<group name="another_child_grp_without_default">
 npt peers {{ val3 }}
</group>
</group>

<group name="ntp-2">
ntp server {{ server }}
 ntp source {{ source | default("undefined") }}
</group>

<group name="snmp-1" default="Uncknown">
snmp community {{ community }}
snmp acl {{ acl }}
</group>


<group name="snmp-2-with-group-output**" default="Uncknown" output="out-1">
snmp community {{ community }}
snmp acl {{ acl }}
<group name="snmp_child_with_defaults" default="None">
 snmp source {{ ip }}
</group>
<group name="snmp_child_without_defaults">
 snmp community {{ comm_val }}
</group>
</group>

<output name="out-1"/>
    """
    parser = ttp(template=template, log_level="ERROR")
    parser.parse()    
    res = parser.result()
    # pprint.pprint(res)  
    assert res == [[[{'domain': {'fqdn': 'Uncknown'},
                      'ntp-1': {'another_child_grp_with_default': {'deeper_child_with_defaults': {'val4': 'something',
                                                                                                  'val5': 'something'},
                                                                   'val2': 'None'},
                                'server': 'Unconfigured',
                                'source': 'undefined'},
                      'snmp-1': {'acl': 'Uncknown', 'community': 'Uncknown'},
                      'uptime-1': {'child_with_default': {'var1': 'val1'},
                                   'uptime': '27 weeks, 3 days, 10 hours, 46 minutes, 10 '
                                             'seconds'}},
                     {'snmp-2-with-group-output': {'acl': 'Uncknown',
                                                   'community': 'Uncknown',
                                                   'snmp_child_with_defaults': {'ip': 'None'}}}]]]

test_groups_with_defaults_only_and_with_children_with_defaults_only()