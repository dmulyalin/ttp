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
    pprint.pprint(res, width=150)
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
    pprint.pprint(res, width=150)
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
    pprint.pprint(res, width=150)
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
    pprint.pprint(res, width=150)
    assert res == [[[{'77description.*(-bla': 'Storage', '77interface.#$%name': 'Port-Channel11'},
                     {'77description.*(-bla': 'RID', '77interface.#$%name': 'Loopback0'},
                     {'77description.*(-bla': 'Management', '77interface.#$%name': 'Port-Channel12'},
                     {'77description.*(-bla': 'Management', '77interface.#$%name': 'Vlan777'}]]]