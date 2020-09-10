import sys
sys.path.insert(0,'../..')
import pprint

from ttp import ttp

def test_simple_anonymous_template():
    template_1 = """interface {{ interface }}
  description {{ description | ORPHRASE }}"""

    data_1 = """
interface Port-Chanel11
  description Storage Management
interface Loopback0
  description RID
"""
    parser = ttp(template=template_1, data=data_1)
    # check that data added:
    datums_added = {"{}:{}".format(template.name, input_name): input_obj.data for template in parser._templates for input_name, input_obj in template.inputs.items()}
    # pprint.pprint(datums_added)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    # assert res == [[[{'description': 'Storage Management', 'interface': 'Port-Chanel11'}, {'description': 'RID', 'interface': 'Loopback0'}]]]
    
# test_simple_anonymous_template()

def test_anonymous_group_with_vars():
    template = """
<input load="text">
interface Port-Chanel11
  description Storage Management
interface Loopback0
  description RID
</input>

<vars name="my.var.s">
a = 1
b = 2
</vars>

<group>
interface {{ interface }}
  description {{ description | ORPHRASE }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[[{'description': 'Storage Management', 'interface': 'Port-Chanel11'},
   {'description': 'RID', 'interface': 'Loopback0'},
   {'my': {'var': {'s': {'a': 1, 'b': 2}}}}]]]
   
# test_anonymous_group_with_vars()

def test_anonymous_group_with_child_group_empty_absolute_path():
    template = """
<template results="per_template">
<input name="Cisco_ios" load="text">
r2#show interfaces | inc line protocol
interface GigabitEthernet1
 vrf forwarding MGMT
 ip address 10.123.89.55 255.255.255.0
</input>

<input name="Cisco_ios" load="text">
r1#show interfaces | inc line protocol:
interface GigabitEthernet1
 description some info
 vrf forwarding MGMT
 ip address 10.123.89.56 255.255.255.0
interface GigabitEthernet2
 ip address 10.123.89.55 255.255.255.0
</input>

<group void="">
interface {{ interface }}
 description {{ description | ORPHRASE }}
 <group name="/">
 ip address {{ ip }} {{ mask }}
 </group>
</group>
</template>
    """
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[{'ip': '10.123.89.55', 'mask': '255.255.255.0'},
                    {'ip': '10.123.89.56', 'mask': '255.255.255.0'},
                    {'ip': '10.123.89.55', 'mask': '255.255.255.0'}]]
                 
# test_anonymous_group_with_child_group_empty_absolute_path()

def test_anonymous_group_with_per_template_mode():
    template = """
<template results="per_template">
<group void="">
hostname {{ hostname | record(hostname_abc) }}
</group>

<group>
interface {{ interface }}
 description {{ description | ORPHRASE }}
 ip address {{ ip }} {{ mask }}
 {{ hostname | set(hostname_abc) }}
</group>
</template>
    """
    datum_1 = """
hostname r2
!
interface GigabitEthernet1
 vrf forwarding MGMT
 ip address 10.123.89.55 255.255.255.0
    """
    datum_2 = """
hostname r1
!
interface GigabitEthernet1
 description some info
 vrf forwarding MGMT
 ip address 10.123.89.56 255.255.255.0
interface GigabitEthernet2
 ip address 10.123.89.55 255.255.255.0
    """
    parser_a = ttp(template=template)
    parser_a.add_input(datum_1)
    parser_a.add_input(datum_2)
    parser_a.parse()
    res = parser_a.result()
    # pprint.pprint(res)
    assert res == [[{'hostname': 'r2',
                     'interface': 'GigabitEthernet1',
                     'ip': '10.123.89.55',
                     'mask': '255.255.255.0'},
                    {'description': 'some info',
                     'hostname': 'r1',
                     'interface': 'GigabitEthernet1',
                     'ip': '10.123.89.56',
                     'mask': '255.255.255.0'},
                    {'hostname': 'r1',
                     'interface': 'GigabitEthernet2',
                     'ip': '10.123.89.55',
                     'mask': '255.255.255.0'}]]
    
# test_anonymous_group_with_per_template_mode()