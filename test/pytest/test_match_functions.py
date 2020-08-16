import sys
sys.path.insert(0,'../..')
import pprint

from ttp import ttp

def test_sformat_inline():
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
interface {{ interface | sformat("BSQ {}") }}
  description {{ description }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()    
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [[[{'description': 'Storage', 'interface': 'BSQ Port-Channel11'},
                     {'description': 'RID', 'interface': 'BSQ Loopback0'},
                     {'description': 'Management', 'interface': 'BSQ Port-Channel12'},
                     {'description': 'Management', 'interface': 'BSQ Vlan777'}]]]
# test_sformat_inline()

def test_sformat_from_vars():
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

<vars>
var_1 = "BSQ {}"
</vars>

<group>
interface {{ interface | sformat(var_1) }}
  description {{ description }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()    
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [[[{'description': 'Storage', 'interface': 'BSQ Port-Channel11'},
                     {'description': 'RID', 'interface': 'BSQ Loopback0'},
                     {'description': 'Management', 'interface': 'BSQ Port-Channel12'},
                     {'description': 'Management', 'interface': 'BSQ Vlan777'}]]]