import sys
sys.path.insert(0,'../..')
import pprint

from ttp import ttp

def test_empty_group_results():
    template = """
<input load="text">
vlan 1234
 name some_vlan
vlan 5678
vlan 910
 name one_more
vlan 777
</input>

<group name="vlans.{{ vlan }}">
vlan {{ vlan }}
 name {{ name }}
</group>
"""
    parser = ttp(template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[{'vlans': {'1234': {'name': 'some_vlan'},
                               '5678': {},
                               '777': {},
                               '910': {'name': 'one_more'}}}]]
    
# test_empty_group_results()