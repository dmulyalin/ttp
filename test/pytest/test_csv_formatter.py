import sys
sys.path.insert(0,'../..')

from ttp import ttp


def test_csv_formatter_with_ints():
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
