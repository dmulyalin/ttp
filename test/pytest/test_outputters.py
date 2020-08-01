import sys
sys.path.insert(0,'../..')
import pprint

import logging
logging.basicConfig(level="INFO")

from ttp import ttp

def test_csv_formatter_simple():
    template_1 = """
<input load="text">
interface Port-Chanel11
  vlan 10
interface Loopback0
  vlan 20
</input>

<group>
interface {{ interface }}
  vlan {{ vlan | to_int }}
</group>

<output
format="csv"
/>
"""
    parser = ttp(template=template_1)
    parser.parse()
    res = parser.result()
    assert res == ['interface,vlan\nPort-Chanel11,10\nLoopback0,20']
    
def test_csv_formatter_with_is_equal():
    template = """
<input load="text" groups="interfaces2.trunks2">
interface GigabitEthernet3/3
 switchport trunk allowed vlan add 138,166-173 
 description some description
!
interface GigabitEthernet3/4
 switchport trunk allowed vlan add 100-105
!
interface GigabitEthernet3/5
 switchport trunk allowed vlan add 459,531,704-707
 ip address 1.1.1.1 255.255.255.255
 vrf forwarding ABC_VRF
!
</input>

<!--group with group specific outputs:-->
<group name="interfaces2.trunks2" output="out_csv2, test3-1">
interface {{ interface }}
 switchport trunk allowed vlan add {{ trunk_vlans }}
 description {{ description | ORPHRASE }}
 vrf forwarding {{ vrf }}
 ip address {{ ip }} {{ mask }}
!{{ _end_ }}
</group>

<out>
name="out_csv2"
path="interfaces2.trunks2"
format="csv"
sep=","
missing="undefined"
description="group specific csv outputter"
</out>

<out 
name="test3-1"
load="text"
returner="self"
functions="is_equal"
description="test csv group specific outputter"
>description,interface,ip,mask,trunk_vlans,vrf
some description,GigabitEthernet3/3,undefined,undefined,138,166-173,undefined
undefined,GigabitEthernet3/4,undefined,undefined,100-105,undefined
undefined,GigabitEthernet3/5,1.1.1.1,255.255.255.255,459,531,704-707,ABC_VRF</out>
"""
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    assert res == [[{'is_equal': True,
   'output_description': 'test csv group specific outputter',
   'output_name': 'test3-1'}]]