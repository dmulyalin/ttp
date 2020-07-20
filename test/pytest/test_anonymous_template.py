import sys
sys.path.insert(0,'../..')

from ttp import ttp

template_1 = """interface {{ interface }}
  description {{ description | ORPHRASE }}"""

data_1 = """
interface Port-Chanel11
  description Storage Management
interface Loopback0
  description RID
"""

def test_simple_anonymous_template():
    parser = ttp(template=template_1, data=data_1)
    parser.parse()
    res = parser.result()
    assert res == [[[{'description': 'Storage Management', 'interface': 'Port-Chanel11'}, {'description': 'RID', 'interface': 'Loopback0'}]]]