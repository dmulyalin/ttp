import sys
sys.path.insert(0,'../..')
import pprint
from ttp import ttp


def test_group_chain_attribute_list():
    template_1 = """
<input load="text">
interface Port-Chanel11
  vlan 10
interface Loopback0
  vlan 20
  description test loopback0
interface Loopback1
  vlan 30
  description test loopback1
</input>

<vars>
chain1 = [
"del(vlan)",
"contains_val(interface, 'Loop')"
]
</vars>

<group chain="chain1">
interface {{ interface }}
  vlan {{ vlan | to_int }}
  description {{ description | ORPHRASE }}
</group>
"""
    parser = ttp(template=template_1)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[[{'description': 'test loopback0', 'interface': 'Loopback0'},
                     {'description': 'test loopback1', 'interface': 'Loopback1'}]]]
                     
def test_group_chain_attribute_list_multi_func():
    template_1 = """
<input load="text">
interface Port-Chanel11
  vlan 10
interface Loopback0
  vlan 20
  description test loopback0
interface Loopback1
  vlan 30
  description test loopback1
</input>

<vars>
chain1 = [
  "del(vlan) | set('set_value', 'set_key')",
  "contains_val(interface, 'Loop')",
  "macro('test_macro')",
  "macro('test_macro1, test_macro2')",
  "macro(test_macro3, test_macro4)",
]
</vars>

<macro>
def test_macro(data):
    data["test_macro"] = "DONE"
    return data

def test_macro1(data):
    data["test_macro1"] = "DONE"
    return data
    
def test_macro2(data):
    data["test_macro2"] = "DONE"
    return data
	
def test_macro3(data):
    data["test_macro3"] = "DONE"
    return data
	
def test_macro4(data):
    data["test_macro4"] = "DONE"
    return data
</macro>

<group chain="chain1">
interface {{ interface }}
  vlan {{ vlan | to_int }}
  description {{ description | ORPHRASE }}
</group>
"""
    parser = ttp(template=template_1)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[[{'description': 'test loopback0',
                      'interface': 'Loopback0',
                      'set_key': 'set_value',
                      'test_macro': 'DONE',
                      'test_macro1': 'DONE',
                      'test_macro2': 'DONE',
                      'test_macro3': 'DONE',
                      'test_macro4': 'DONE'},
                     {'description': 'test loopback1',
                      'interface': 'Loopback1',
                      'set_key': 'set_value',
                      'test_macro': 'DONE',
                      'test_macro1': 'DONE',
                      'test_macro2': 'DONE',
                      'test_macro3': 'DONE',
                      'test_macro4': 'DONE'}]]]
					  
