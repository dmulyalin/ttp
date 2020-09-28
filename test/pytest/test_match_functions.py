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
                     
def test_to_list_with_joinmatches():
    template = """
<input load="text">
interface GigabitEthernet3/3
 switchport trunk allowed vlan add 138,166,173 
 switchport trunk allowed vlan add 400,401,410
</input>
 
<group>
interface {{ interface }}
 switchport trunk allowed vlan add {{ trunk_vlans | to_list | joinmatches }}
</group>
    """
    parser = ttp(template=template)
    parser.parse()    
    res = parser.result()
    # pprint.pprint(res, width=150)
    assert res == [[[{'interface': 'GigabitEthernet3/3', 'trunk_vlans': ['138,166,173', '400,401,410']}]]]
    
# test_to_list_with_joinmatches()

def test_multiple_joinmatches():
    data = """
SWITCH# show vlan port 2/11 detail

Status and Counters - VLAN Information - for ports 2/11

Port name:

VLAN ID Name | Status Voice Jumbo Mode

------- -------------------- + ---------- ----- ----- --------

60 ABC | Port-based No No Tagged

70 DEF | Port-based No No Tagged

101 GHIJ | Port-based No No Untagged

105 KLMNO | Port-based No No Tagged

116 PQRS | Port-based No No Tagged

117 TVU | Port-based No No Tagged

SWITCH# show vlan port 2/12 detail

Status and Counters - VLAN Information - for ports 2/12

Port name:

VLAN ID Name | Status Voice Jumbo Mode

------- -------------------- + ---------- ----- ----- --------

61 ABC | Port-based No No Tagged

71 DEF | Port-based No No Tagged

103 GHI | Port-based No No Untagged
    """
    template = """
<vars>
hostname="gethostname"
</vars>

<group name="vlans*">
Status and Counters - VLAN Information - for ports {{ Port_Number }}
{{ Tagged_VLAN | joinmatches(", ") }} {{ name | joinmatches(", ") }} | {{ ignore }} {{ ignore }} {{ ignore }} Tagged
{{ Untagged_VLAN }}                   {{ name | joinmatches(", ") }} | {{ ignore }} {{ ignore }} {{ ignore }} Untagged
{{ Hostname | set(hostname) }}
</group>   
    """
    parser = ttp(data, template)
    parser.parse()
    res = parser.result()
    pprint.pprint(res)
    assert res == [[{'vlans': [{'Hostname': 'SWITCH',
                     'Port_Number': '2/11',
                     'Tagged_VLAN': '60, 70, 105, 116, 117',
                     'Untagged_VLAN': '101',
                     'name': 'ABC, DEF, GHIJ, KLMNO, PQRS, TVU'},
                    {'Hostname': 'SWITCH',
                     'Port_Number': '2/12',
                     'Tagged_VLAN': '61, 71',
                     'Untagged_VLAN': '103',
                     'name': 'ABC, DEF, GHI'}]}]]
    
# test_multiple_joinmatches()

def test_joinmatches_with_ignore():
    data = """
SWITCH# show vlan port 2/11 detail

Status and Counters - VLAN Information - for ports 2/11

Port name:

VLAN ID Name | Status Voice Jumbo Mode

------- -------------------- + ---------- ----- ----- --------

60 ABC | Port-based No No Tagged

70 DEF | Port-based No No Tagged

101 GHIJ | Port-based No No Untagged

105 KLMNO | Port-based No No Tagged

116 PQRS | Port-based No No Tagged

117 TVU | Port-based No No Tagged

SWITCH# show vlan port 2/12 detail

Status and Counters - VLAN Information - for ports 2/12

Port name:

VLAN ID Name | Status Voice Jumbo Mode

------- -------------------- + ---------- ----- ----- --------

61 ABC | Port-based No No Tagged

71 DEF | Port-based No No Tagged

103 GHI | Port-based No No Untagged
    """
    template = """
<vars>
hostname="gethostname"
</vars>

<group name="vlans*">
Status and Counters - VLAN Information - for ports {{ Port_Number }}
{{ Tagged_VLAN | joinmatches(" ") }} {{ ignore }} | {{ ignore }} {{ ignore }} {{ ignore }} Tagged
{{ Untagged_VLAN }}                  {{ ignore }} | {{ ignore }} {{ ignore }} {{ ignore }} Untagged
{{ Hostname | set(hostname) }}
</group>   
    """
    parser = ttp(data, template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[{'vlans': [{'Hostname': 'SWITCH',
                     'Port_Number': '2/11',
                     'Tagged_VLAN': '60 70 105 116 117',
                     'Untagged_VLAN': '101'},
                    {'Hostname': 'SWITCH',
                     'Port_Number': '2/12',
                     'Tagged_VLAN': '61 71',
                     'Untagged_VLAN': '103'}]}]]